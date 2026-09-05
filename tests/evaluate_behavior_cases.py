#!/usr/bin/env python3
"""Evaluate recorded model/tool runs against the 24 core skill cases."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SKILLS = ("decision", "writing", "invest", "plan-skill")
METRIC_TO_LIMIT = {
    "reference_reads": "max_reference_reads",
    "followup_questions": "max_followup_questions",
    "external_mutations": "max_external_mutations",
    "operations": "max_operations",
}


def fail(message: str) -> None:
    print(f"error: {message}", file=sys.stderr)
    raise SystemExit(2)


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        fail(f"file not found: {path}")
    records: list[dict[str, Any]] = []
    for line_number, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError as exc:
            fail(f"{path}:{line_number}: invalid JSON: {exc.msg}")
        if not isinstance(record, dict):
            fail(f"{path}:{line_number}: record must be an object")
        records.append(record)
    return records


def load_cases(split: str) -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []
    for skill in SKILLS:
        path = ROOT / skill / "evals" / "behavior-cases.jsonl"
        cases.extend(load_jsonl(path))
    if split != "all":
        cases = [case for case in cases if case.get("split") == split]
    return cases


def index_results(records: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    indexed: dict[str, dict[str, Any]] = {}
    for index, record in enumerate(records):
        record_id = record.get("id")
        if not isinstance(record_id, str) or not record_id:
            fail(f"results record {index} has no non-empty id")
        if record_id in indexed:
            fail(f"duplicate result id: {record_id}")
        indexed[record_id] = record
    return indexed


def nonnegative_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and value >= 0


def evaluate_case(case: dict[str, Any], record: dict[str, Any] | None) -> dict[str, Any]:
    failures: list[str] = []
    observed_costs: dict[str, Any] = {}
    if record is None:
        return {
            "id": case["id"],
            "skill": case["skill"],
            "split": case["split"],
            "passed": False,
            "failures": ["missing result record"],
            "observed_costs": observed_costs,
        }

    output = record.get("output")
    if not isinstance(output, str):
        failures.append("output must be a string")
        output = ""
    for required in case.get("must_include", []):
        if required not in output:
            failures.append(f"missing required output: {required}")
    for forbidden in case.get("must_not_include", []):
        if forbidden in output:
            failures.append(f"forbidden output present: {forbidden}")

    tool_calls = record.get("tool_calls")
    if not isinstance(tool_calls, list) or not all(isinstance(item, str) for item in tool_calls):
        failures.append("tool_calls must be an array of tool names")
        tool_calls = []
    for prefix in case.get("required_tool_prefixes", []):
        if not any(tool.startswith(prefix) for tool in tool_calls):
            failures.append(f"required tool prefix not observed: {prefix}")
    for prefix in case.get("forbidden_tool_prefixes", []):
        if any(tool.startswith(prefix) for tool in tool_calls):
            failures.append(f"forbidden tool prefix observed: {prefix}")

    metrics = record.get("metrics")
    if not isinstance(metrics, dict):
        failures.append("metrics must record reads, questions, mutations, and operations")
        metrics = {}
    limits = case["cost_limits"]
    for metric, limit_name in METRIC_TO_LIMIT.items():
        observed = metrics.get(metric)
        observed_costs[metric] = observed
        if not nonnegative_number(observed):
            failures.append(f"metric {metric} must be a non-negative number")
        elif observed > limits[limit_name]:
            failures.append(f"metric {metric}={observed} exceeds {limit_name}={limits[limit_name]}")

    if record.get("behavior_pass") is not True:
        failures.append(f"independent behavior check failed: {case['expected_behavior']}")
    if not isinstance(record.get("behavior_evidence"), str) or not record["behavior_evidence"].strip():
        failures.append("behavior_evidence must explain the observable judgment")

    return {
        "id": case["id"],
        "skill": case["skill"],
        "split": case["split"],
        "passed": not failures,
        "failures": failures,
        "observed_costs": observed_costs,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate core skill behavior-run records.")
    parser.add_argument("results", type=Path, help="JSONL run records keyed by behavior case id")
    parser.add_argument("--split", choices=("development", "acceptance", "all"), default="all")
    args = parser.parse_args()

    cases = load_cases(args.split)
    results = index_results(load_jsonl(args.results))
    evaluations = [evaluate_case(case, results.get(case["id"])) for case in cases]
    passed = sum(item["passed"] for item in evaluations)
    report = {
        "split": args.split,
        "summary": {"total": len(evaluations), "passed": passed, "failed": len(evaluations) - passed},
        "acceptance": "pass" if passed == len(evaluations) else "fail",
        "cases": evaluations,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    raise SystemExit(0 if report["acceptance"] == "pass" else 1)


if __name__ == "__main__":
    main()
