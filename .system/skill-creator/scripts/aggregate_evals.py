#!/usr/bin/env python3
"""Aggregate paired candidate/baseline skill eval runs into a benchmark."""

from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from validate_evals import load_and_validate


CONFIGURATIONS = ("candidate", "baseline")


class EvalDataError(ValueError):
    pass


def _is_number(value: Any) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(value)
    )


def _read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise EvalDataError(f"could not read {path}: {exc}") from exc


def _run_numbers(config_dir: Path) -> set[int]:
    numbers: set[int] = set()
    for path in config_dir.glob("run-*"):
        if not path.is_dir():
            continue
        suffix = path.name.removeprefix("run-")
        if not suffix.isdigit() or int(suffix) < 1:
            raise EvalDataError(f"invalid run directory: {path}")
        number = int(suffix)
        if number in numbers:
            raise EvalDataError(f"duplicate run number in {config_dir}: {number}")
        numbers.add(number)
    return numbers


def _load_grading(
    path: Path, expected_assertions: dict[str, dict[str, Any]]
) -> tuple[list[dict[str, Any]], list[str]]:
    data = _read_json(path)
    if not isinstance(data, dict):
        raise EvalDataError(f"{path}: grading root must be an object")
    unexpected = sorted(data.keys() - {"assertions", "notes"})
    if unexpected:
        raise EvalDataError(
            f"{path}: unexpected grading field(s): {', '.join(unexpected)}"
        )
    assertions = data.get("assertions")
    if not isinstance(assertions, list):
        raise EvalDataError(f"{path}: assertions must be an array")

    by_id: dict[str, dict[str, Any]] = {}
    for index, assertion in enumerate(assertions):
        if not isinstance(assertion, dict):
            raise EvalDataError(f"{path}: assertions[{index}] must be an object")
        if set(assertion) != {"id", "passed", "evidence"}:
            raise EvalDataError(
                f"{path}: assertion grades require exactly id, passed, and evidence"
            )
        assertion_id = assertion.get("id")
        if not isinstance(assertion_id, str) or not assertion_id:
            raise EvalDataError(f"{path}: assertions[{index}].id must be a string")
        if assertion_id in by_id:
            raise EvalDataError(f"{path}: duplicate assertion grade '{assertion_id}'")
        if not isinstance(assertion.get("passed"), bool):
            raise EvalDataError(
                f"{path}: assertion '{assertion_id}' passed must be boolean"
            )
        evidence = assertion.get("evidence")
        if not isinstance(evidence, str) or not evidence.strip():
            raise EvalDataError(
                f"{path}: assertion '{assertion_id}' requires non-empty evidence"
            )
        by_id[assertion_id] = assertion

    missing = sorted(expected_assertions.keys() - by_id.keys())
    extra = sorted(by_id.keys() - expected_assertions.keys())
    if missing:
        raise EvalDataError(f"{path}: missing assertion grade(s): {', '.join(missing)}")
    if extra:
        raise EvalDataError(f"{path}: unknown assertion grade(s): {', '.join(extra)}")

    notes = data.get("notes", [])
    if not isinstance(notes, list) or any(not isinstance(note, str) for note in notes):
        raise EvalDataError(f"{path}: notes must be an array of strings")
    return [by_id[assertion_id] for assertion_id in expected_assertions], notes


def _load_timing(path: Path) -> tuple[float | None, int | None]:
    if not path.exists():
        return None, None
    data = _read_json(path)
    if not isinstance(data, dict):
        raise EvalDataError(f"{path}: timing root must be an object")
    unexpected = sorted(data.keys() - {"duration_seconds", "total_tokens"})
    if unexpected:
        raise EvalDataError(f"{path}: unexpected timing field(s): {', '.join(unexpected)}")

    duration = data.get("duration_seconds")
    if duration is not None and (not _is_number(duration) or duration < 0):
        raise EvalDataError(f"{path}: duration_seconds must be non-negative")
    tokens = data.get("total_tokens")
    if tokens is not None and (
        not isinstance(tokens, int) or isinstance(tokens, bool) or tokens < 0
    ):
        raise EvalDataError(f"{path}: total_tokens must be a non-negative integer")
    return float(duration) if duration is not None else None, tokens


def _stats(values: list[float | int]) -> dict[str, int | float | None]:
    if not values:
        return {"samples": 0, "mean": None, "stddev": None, "min": None, "max": None}
    return {
        "samples": len(values),
        "mean": round(statistics.fmean(values), 4),
        "stddev": round(statistics.stdev(values), 4) if len(values) > 1 else 0.0,
        "min": min(values),
        "max": max(values),
    }


def _summary(records: list[dict[str, Any]]) -> dict[str, Any]:
    passed = sum(record["passed"] for record in records)
    total = sum(record["total"] for record in records)
    durations = [
        record["duration_seconds"]
        for record in records
        if record["duration_seconds"] is not None
    ]
    tokens = [
        record["total_tokens"]
        for record in records
        if record["total_tokens"] is not None
    ]
    return {
        "run_count": len(records),
        "passed_assertions": passed,
        "total_assertions": total,
        "pass_rate": round(passed / total, 6) if total else 0.0,
        "required_failures": sum(record["required_failures"] for record in records),
        "duration_seconds": _stats(durations),
        "total_tokens": _stats(tokens),
    }


def aggregate(iteration_dir: Path, contract: dict[str, Any], contract_path: Path) -> dict:
    expected_eval_dirs = {f"eval-{evaluation['id']}" for evaluation in contract["evals"]}
    actual_eval_dirs = {
        path.name for path in iteration_dir.glob("eval-*") if path.is_dir()
    }
    missing_dirs = sorted(expected_eval_dirs - actual_eval_dirs)
    extra_dirs = sorted(actual_eval_dirs - expected_eval_dirs)
    if missing_dirs:
        raise EvalDataError(f"missing eval directory(s): {', '.join(missing_dirs)}")
    if extra_dirs:
        raise EvalDataError(f"unexpected eval directory(s): {', '.join(extra_dirs)}")

    records: dict[str, list[dict[str, Any]]] = {
        configuration: [] for configuration in CONFIGURATIONS
    }
    per_eval: dict[str, dict[str, Any]] = {}

    for evaluation in contract["evals"]:
        eval_id = evaluation["id"]
        eval_dir = iteration_dir / f"eval-{eval_id}"
        assertion_specs = {
            assertion["id"]: assertion for assertion in evaluation["assertions"]
        }
        run_sets: dict[str, set[int]] = {}
        for configuration in CONFIGURATIONS:
            config_dir = eval_dir / configuration
            if not config_dir.is_dir():
                raise EvalDataError(f"missing configuration directory: {config_dir}")
            run_sets[configuration] = _run_numbers(config_dir)
            if not run_sets[configuration]:
                raise EvalDataError(f"no runs found in {config_dir}")

        if run_sets["candidate"] != run_sets["baseline"]:
            raise EvalDataError(
                f"{eval_dir}: candidate and baseline runs must be paired; "
                f"candidate={sorted(run_sets['candidate'])}, "
                f"baseline={sorted(run_sets['baseline'])}"
            )

        eval_records: dict[str, list[dict[str, Any]]] = {
            configuration: [] for configuration in CONFIGURATIONS
        }
        for configuration in CONFIGURATIONS:
            for run_number in sorted(run_sets[configuration]):
                run_dir = eval_dir / configuration / f"run-{run_number}"
                grading_path = run_dir / "grading.json"
                if not grading_path.is_file():
                    raise EvalDataError(f"missing grading file: {grading_path}")
                grades, notes = _load_grading(grading_path, assertion_specs)
                duration, tokens = _load_timing(run_dir / "timing.json")
                record = {
                    "eval_id": eval_id,
                    "configuration": configuration,
                    "run_number": run_number,
                    "passed": sum(grade["passed"] for grade in grades),
                    "total": len(grades),
                    "required_failures": sum(
                        not grade["passed"] and assertion_specs[grade["id"]]["required"]
                        for grade in grades
                    ),
                    "duration_seconds": duration,
                    "total_tokens": tokens,
                    "assertions": grades,
                    "notes": notes,
                }
                records[configuration].append(record)
                eval_records[configuration].append(record)
        per_eval[eval_id] = {
            configuration: _summary(eval_records[configuration])
            for configuration in CONFIGURATIONS
        }

    configurations = {
        configuration: _summary(records[configuration])
        for configuration in CONFIGURATIONS
    }
    delta = round(
        configurations["candidate"]["pass_rate"]
        - configurations["baseline"]["pass_rate"],
        6,
    )
    thresholds = contract["acceptance"]
    checks = {
        "candidate_pass_rate": (
            configurations["candidate"]["pass_rate"]
            >= thresholds["min_candidate_pass_rate"]
        ),
        "required_failures": (
            configurations["candidate"]["required_failures"]
            <= thresholds["max_required_failures"]
        ),
        "pass_rate_delta": delta >= thresholds["min_pass_rate_delta"],
    }
    reasons = [name for name, passed in checks.items() if not passed]

    return {
        "schema_version": 1,
        "skill_name": contract["skill_name"],
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "contract_path": str(contract_path.resolve()),
        "iteration_path": str(iteration_dir.resolve()),
        "configurations": configurations,
        "delta": {"pass_rate": delta},
        "per_eval": per_eval,
        "runs": records,
        "acceptance": {
            "passed": all(checks.values()),
            "thresholds": thresholds,
            "checks": checks,
            "failed_checks": reasons,
        },
    }


def _format_metric(stats: dict[str, Any], suffix: str = "") -> str:
    if not stats["samples"]:
        return "—"
    return f"{stats['mean']:.2f}{suffix} ± {stats['stddev']:.2f}{suffix}"


def benchmark_markdown(benchmark: dict[str, Any]) -> str:
    candidate = benchmark["configurations"]["candidate"]
    baseline = benchmark["configurations"]["baseline"]
    decision = "ACCEPT" if benchmark["acceptance"]["passed"] else "REJECT"
    lines = [
        f"# Skill Eval Benchmark: {benchmark['skill_name']}",
        "",
        f"Decision: **{decision}**",
        "",
        "| Metric | Candidate | Baseline |",
        "| --- | ---: | ---: |",
        f"| Runs | {candidate['run_count']} | {baseline['run_count']} |",
        f"| Assertion pass rate | {candidate['pass_rate']:.1%} | {baseline['pass_rate']:.1%} |",
        f"| Required failures | {candidate['required_failures']} | {baseline['required_failures']} |",
        f"| Duration | {_format_metric(candidate['duration_seconds'], 's')} | {_format_metric(baseline['duration_seconds'], 's')} |",
        f"| Total tokens | {_format_metric(candidate['total_tokens'])} | {_format_metric(baseline['total_tokens'])} |",
        "",
        f"Pass-rate delta: **{benchmark['delta']['pass_rate']:+.1%}**",
        "",
        "## Acceptance Checks",
        "",
    ]
    for name, passed in benchmark["acceptance"]["checks"].items():
        lines.append(f"- {'PASS' if passed else 'FAIL'}: `{name}`")
    lines.extend(
        ["", "## Per Eval", "", "| Eval | Candidate | Baseline |", "| --- | ---: | ---: |"]
    )
    for eval_id, configurations in benchmark["per_eval"].items():
        lines.append(
            f"| `{eval_id}` | {configurations['candidate']['pass_rate']:.1%} | "
            f"{configurations['baseline']['pass_rate']:.1%} |"
        )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Aggregate paired skill eval runs")
    parser.add_argument("iteration", type=Path, help="Path to iteration-N directory")
    parser.add_argument("--evals", type=Path, required=True, help="Frozen evals.json")
    parser.add_argument("--output", type=Path, help="Output benchmark.json path")
    args = parser.parse_args()

    iteration_dir = args.iteration.resolve()
    if not iteration_dir.is_dir():
        print(f"[ERROR] iteration directory not found: {iteration_dir}", file=sys.stderr)
        return 1
    contract, errors = load_and_validate(args.evals)
    if errors:
        for error in errors:
            print(f"[ERROR] {error}", file=sys.stderr)
        return 1
    assert contract is not None

    try:
        benchmark = aggregate(iteration_dir, contract, args.evals)
    except EvalDataError as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 1

    output_path = (args.output or iteration_dir / "benchmark.json").resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(benchmark, indent=2) + "\n", encoding="utf-8")
    markdown_path = output_path.with_suffix(".md")
    markdown_path.write_text(benchmark_markdown(benchmark), encoding="utf-8")
    print(f"Generated {output_path}")
    print(f"Generated {markdown_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
