#!/usr/bin/env python3
"""Validate a skill evaluation contract without third-party dependencies."""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path
from typing import Any


SCHEMA_VERSION = 1
ID_PATTERN = re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,62}[a-z0-9])?$")
SKILL_NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
ASSERTION_KINDS = {"deterministic", "model", "human"}


def _is_number(value: Any) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(value)
    )


def _check_keys(
    value: dict[str, Any],
    location: str,
    required: set[str],
    optional: set[str],
    errors: list[str],
) -> None:
    missing = sorted(required - value.keys())
    unexpected = sorted(value.keys() - required - optional)
    if missing:
        errors.append(f"{location}: missing field(s): {', '.join(missing)}")
    if unexpected:
        errors.append(f"{location}: unexpected field(s): {', '.join(unexpected)}")


def validate_contract(data: Any, source: Path) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["root: expected a JSON object"]

    _check_keys(
        data,
        "root",
        {"schema_version", "skill_name", "acceptance", "evals"},
        set(),
        errors,
    )

    if data.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"root.schema_version: expected {SCHEMA_VERSION}")

    skill_name = data.get("skill_name")
    if not isinstance(skill_name, str) or not SKILL_NAME_PATTERN.fullmatch(skill_name):
        errors.append("root.skill_name: expected a non-empty hyphen-case name")

    acceptance = data.get("acceptance")
    if not isinstance(acceptance, dict):
        errors.append("root.acceptance: expected an object")
    else:
        _check_keys(
            acceptance,
            "root.acceptance",
            {
                "min_candidate_pass_rate",
                "max_required_failures",
                "min_pass_rate_delta",
            },
            set(),
            errors,
        )
        pass_rate = acceptance.get("min_candidate_pass_rate")
        if not _is_number(pass_rate) or not 0 <= pass_rate <= 1:
            errors.append(
                "root.acceptance.min_candidate_pass_rate: expected a number from 0 to 1"
            )
        max_failures = acceptance.get("max_required_failures")
        if (
            not isinstance(max_failures, int)
            or isinstance(max_failures, bool)
            or max_failures < 0
        ):
            errors.append(
                "root.acceptance.max_required_failures: expected a non-negative integer"
            )
        delta = acceptance.get("min_pass_rate_delta")
        if not _is_number(delta) or not -1 <= delta <= 1:
            errors.append(
                "root.acceptance.min_pass_rate_delta: expected a number from -1 to 1"
            )

    evals = data.get("evals")
    if not isinstance(evals, list) or not evals:
        errors.append("root.evals: expected a non-empty array")
        return errors

    eval_ids: set[str] = set()
    fixture_root = source.parent.resolve()
    for eval_index, evaluation in enumerate(evals):
        location = f"root.evals[{eval_index}]"
        if not isinstance(evaluation, dict):
            errors.append(f"{location}: expected an object")
            continue
        _check_keys(
            evaluation,
            location,
            {"id", "prompt", "expected_output", "files", "assertions"},
            set(),
            errors,
        )

        eval_id = evaluation.get("id")
        if not isinstance(eval_id, str) or not ID_PATTERN.fullmatch(eval_id):
            errors.append(f"{location}.id: expected a 1-64 character hyphen-case ID")
        elif eval_id in eval_ids:
            errors.append(f"{location}.id: duplicate eval ID '{eval_id}'")
        else:
            eval_ids.add(eval_id)

        for field in ("prompt", "expected_output"):
            value = evaluation.get(field)
            if not isinstance(value, str) or not value.strip():
                errors.append(f"{location}.{field}: expected a non-empty string")

        files = evaluation.get("files")
        if not isinstance(files, list):
            errors.append(f"{location}.files: expected an array")
        else:
            for file_index, raw_path in enumerate(files):
                file_location = f"{location}.files[{file_index}]"
                if not isinstance(raw_path, str) or not raw_path.strip():
                    errors.append(f"{file_location}: expected a non-empty path string")
                    continue
                relative_path = Path(raw_path)
                resolved_path = (fixture_root / relative_path).resolve()
                try:
                    resolved_path.relative_to(fixture_root)
                except ValueError:
                    errors.append(
                        f"{file_location}: fixture paths must stay within {fixture_root}"
                    )
                    continue
                if relative_path.is_absolute():
                    errors.append(f"{file_location}: expected a relative fixture path")
                elif not resolved_path.is_file():
                    errors.append(f"{file_location}: fixture file not found: {raw_path}")

        assertions = evaluation.get("assertions")
        if not isinstance(assertions, list) or not assertions:
            errors.append(f"{location}.assertions: expected a non-empty array")
            continue

        assertion_ids: set[str] = set()
        for assertion_index, assertion in enumerate(assertions):
            assertion_location = f"{location}.assertions[{assertion_index}]"
            if not isinstance(assertion, dict):
                errors.append(f"{assertion_location}: expected an object")
                continue
            _check_keys(
                assertion,
                assertion_location,
                {"id", "text", "kind", "required"},
                set(),
                errors,
            )

            assertion_id = assertion.get("id")
            if not isinstance(assertion_id, str) or not ID_PATTERN.fullmatch(
                assertion_id
            ):
                errors.append(
                    f"{assertion_location}.id: expected a 1-64 character hyphen-case ID"
                )
            elif assertion_id in assertion_ids:
                errors.append(
                    f"{assertion_location}.id: duplicate assertion ID '{assertion_id}'"
                )
            else:
                assertion_ids.add(assertion_id)

            text = assertion.get("text")
            if not isinstance(text, str) or not text.strip():
                errors.append(f"{assertion_location}.text: expected a non-empty string")
            if assertion.get("kind") not in ASSERTION_KINDS:
                allowed = ", ".join(sorted(ASSERTION_KINDS))
                errors.append(f"{assertion_location}.kind: expected one of {allowed}")
            if not isinstance(assertion.get("required"), bool):
                errors.append(f"{assertion_location}.required: expected a boolean")

    return errors


def load_and_validate(path: Path) -> tuple[dict[str, Any] | None, list[str]]:
    source = path.resolve()
    if not source.is_file():
        return None, [f"eval contract not found: {source}"]
    try:
        data = json.loads(source.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        return None, [f"could not read eval contract: {exc}"]
    errors = validate_contract(data, source)
    if errors:
        return None, errors
    return data, []


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a skill eval contract")
    parser.add_argument("evals", type=Path, help="Path to evals/evals.json")
    parser.add_argument("--json", action="store_true", help="Emit JSON result")
    args = parser.parse_args()

    contract, errors = load_and_validate(args.evals)
    result = {
        "valid": not errors,
        "errors": errors,
        "eval_count": len(contract["evals"]) if contract else 0,
        "assertion_count": (
            sum(len(evaluation["assertions"]) for evaluation in contract["evals"])
            if contract
            else 0
        ),
    }
    if args.json:
        print(json.dumps(result, indent=2))
    elif errors:
        for error in errors:
            print(f"[ERROR] {error}", file=sys.stderr)
    else:
        print(
            f"Eval contract is valid: {result['eval_count']} eval(s), "
            f"{result['assertion_count']} assertion(s)"
        )
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
