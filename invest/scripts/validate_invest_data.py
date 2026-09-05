#!/usr/bin/env python3
"""Validate material investment-model inputs and deterministic checks.

The validator checks metadata, arithmetic, and point-in-time availability. It
cannot determine whether a cited source actually supports the recorded value.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


CLASSIFICATIONS = {
    "reported_fact",
    "management_guidance",
    "consensus",
    "analyst_assumption",
}


def fail(message: str) -> None:
    print(f"error: {message}", file=sys.stderr)
    raise SystemExit(2)


def load_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        fail(f"input file not found: {path}")
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON at line {exc.lineno}, column {exc.colno}: {exc.msg}")
    if not isinstance(data, dict):
        fail("top-level JSON value must be an object")
    return data


def finite_number(value: Any) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(float(value))
    )


def parse_time(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    normalized = value.strip().replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return None
    return parsed


def add_finding(
    findings: list[dict[str, Any]],
    code: str,
    message: str,
    *,
    location: str,
    severity: str = "error",
) -> None:
    findings.append(
        {"severity": severity, "code": code, "location": location, "message": message}
    )


def nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate_metric(
    metric: Any,
    index: int,
    decision_time: datetime | None,
    findings: list[dict[str, Any]],
) -> str | None:
    location = f"metrics[{index}]"
    if not isinstance(metric, dict):
        add_finding(findings, "invalid_metric", "metric must be an object", location=location)
        return None
    metric_id = metric.get("id")
    if not nonempty_string(metric_id):
        add_finding(findings, "invalid_id", "id must be a non-empty string", location=f"{location}.id")
        return None

    for field in ("name", "unit", "period", "basis"):
        if not nonempty_string(metric.get(field)):
            add_finding(
                findings,
                f"invalid_{field}",
                f"{field} must be a non-empty string",
                location=f"{location}.{field}",
            )
    if "currency" not in metric or (
        metric.get("currency") is not None and not nonempty_string(metric.get("currency"))
    ):
        add_finding(
            findings,
            "invalid_currency",
            "currency must be a non-empty string or explicit null",
            location=f"{location}.currency",
        )
    classification = metric.get("classification")
    if classification not in CLASSIFICATIONS:
        add_finding(
            findings,
            "invalid_classification",
            "classification must distinguish fact, guidance, consensus, or analyst assumption",
            location=f"{location}.classification",
        )

    value = metric.get("value")
    if value is None:
        if not nonempty_string(metric.get("missing_reason")):
            add_finding(
                findings,
                "missing_reason_required",
                "a null value needs a non-empty missing_reason; unknown is not zero",
                location=f"{location}.missing_reason",
            )
    elif not finite_number(value):
        add_finding(
            findings,
            "invalid_value",
            "value must be a finite number or null",
            location=f"{location}.value",
        )

    source = metric.get("source")
    if not isinstance(source, dict):
        add_finding(findings, "missing_source", "source must be an object", location=f"{location}.source")
        return str(metric_id)
    for field in ("reference", "document_type"):
        if not nonempty_string(source.get(field)):
            add_finding(
                findings,
                f"invalid_source_{field}",
                f"source.{field} must be a non-empty string",
                location=f"{location}.source.{field}",
            )
    if "locator" not in source or (
        source.get("locator") is not None and not nonempty_string(source.get("locator"))
    ):
        add_finding(
            findings,
            "invalid_source_locator",
            "source.locator must be a non-empty string or explicit null",
            location=f"{location}.source.locator",
        )

    published = parse_time(source.get("published_at"))
    available = parse_time(source.get("available_at"))
    if published is None:
        add_finding(
            findings,
            "invalid_published_at",
            "source.published_at must be an ISO-8601 timestamp with timezone",
            location=f"{location}.source.published_at",
        )
    if available is None:
        add_finding(
            findings,
            "invalid_available_at",
            "source.available_at must be an ISO-8601 timestamp with timezone",
            location=f"{location}.source.available_at",
        )
    if published is not None and available is not None and available < published:
        add_finding(
            findings,
            "availability_before_publication",
            "available_at cannot precede published_at",
            location=f"{location}.source.available_at",
        )
    if decision_time is not None and available is not None and available > decision_time:
        add_finding(
            findings,
            "point_in_time_violation",
            "source became available after the historical decision time",
            location=f"{location}.source.available_at",
        )
    return str(metric_id)


def resolve_metrics(
    ids: Any,
    metrics: dict[str, dict[str, Any]],
    findings: list[dict[str, Any]],
    location: str,
) -> list[dict[str, Any]] | None:
    if not isinstance(ids, list) or not ids or not all(nonempty_string(item) for item in ids):
        add_finding(findings, "invalid_metric_refs", "metric references must be a non-empty array", location=location)
        return None
    missing = [item for item in ids if item not in metrics]
    if missing:
        add_finding(
            findings,
            "unknown_metric_ref",
            "unknown metric ids: " + ", ".join(missing),
            location=location,
        )
        return None
    return [metrics[item] for item in ids]


def comparable(metrics: list[dict[str, Any]], fields: tuple[str, ...]) -> bool:
    return all(len({metric.get(field) for metric in metrics}) == 1 for field in fields)


def tolerance(check: dict[str, Any], findings: list[dict[str, Any]], location: str) -> float | None:
    value = check.get("tolerance", 0.001)
    if not finite_number(value) or float(value) < 0:
        add_finding(findings, "invalid_tolerance", "tolerance must be non-negative", location=location)
        return None
    return float(value)


def check_sums(
    checks: Any,
    metrics: dict[str, dict[str, Any]],
    findings: list[dict[str, Any]],
) -> int:
    if not isinstance(checks, list):
        add_finding(findings, "invalid_sums", "checks.sums must be an array", location="checks.sums")
        return 0
    run = 0
    for index, check in enumerate(checks):
        location = f"checks.sums[{index}]"
        if not isinstance(check, dict):
            add_finding(findings, "invalid_sum_check", "sum check must be an object", location=location)
            continue
        total_id = check.get("total")
        referenced = resolve_metrics(check.get("components"), metrics, findings, f"{location}.components")
        if not nonempty_string(total_id) or total_id not in metrics:
            add_finding(findings, "unknown_metric_ref", "total must name a metric", location=f"{location}.total")
            continue
        if referenced is None:
            continue
        involved = referenced + [metrics[total_id]]
        if not comparable(involved, ("unit", "currency", "period", "basis")):
            add_finding(
                findings,
                "incompatible_basis",
                "sum inputs must share unit, currency, period, and basis",
                location=location,
            )
            continue
        if any(metric.get("value") is None or not finite_number(metric.get("value")) for metric in involved):
            add_finding(findings, "evidence_missing", "sum contains an unknown value", location=location)
            continue
        allowed = tolerance(check, findings, f"{location}.tolerance")
        if allowed is None:
            continue
        component_sum = sum(float(metric["value"]) for metric in referenced)
        total = float(metrics[total_id]["value"])
        run += 1
        if abs(component_sum - total) > allowed * max(1.0, abs(total)):
            add_finding(
                findings,
                "sum_mismatch",
                f"components sum to {component_sum:g}, total is {total:g}",
                location=location,
            )
    return run


def check_growth_rates(
    checks: Any,
    metrics: dict[str, dict[str, Any]],
    findings: list[dict[str, Any]],
) -> int:
    if not isinstance(checks, list):
        add_finding(findings, "invalid_growth_rates", "checks.growth_rates must be an array", location="checks.growth_rates")
        return 0
    run = 0
    for index, check in enumerate(checks):
        location = f"checks.growth_rates[{index}]"
        if not isinstance(check, dict):
            add_finding(findings, "invalid_growth_check", "growth check must be an object", location=location)
            continue
        ids = [check.get("prior"), check.get("current")]
        referenced = resolve_metrics(ids, metrics, findings, location)
        if referenced is None:
            continue
        if not comparable(referenced, ("unit", "currency", "basis")):
            add_finding(
                findings,
                "incompatible_basis",
                "growth inputs must share unit, currency, and basis",
                location=location,
            )
            continue
        if any(metric.get("value") is None or not finite_number(metric.get("value")) for metric in referenced):
            add_finding(findings, "evidence_missing", "growth check contains an unknown value", location=location)
            continue
        prior = float(referenced[0]["value"])
        current = float(referenced[1]["value"])
        if abs(prior) <= 1e-12:
            add_finding(findings, "invalid_growth_base", "growth cannot use a zero prior value", location=location)
            continue
        expected = check.get("expected")
        if not finite_number(expected):
            add_finding(findings, "invalid_expected_growth", "expected must be a decimal number", location=f"{location}.expected")
            continue
        allowed = tolerance(check, findings, f"{location}.tolerance")
        if allowed is None:
            continue
        calculated = current / prior - 1.0
        run += 1
        if abs(calculated - float(expected)) > allowed:
            add_finding(
                findings,
                "growth_mismatch",
                f"calculated growth is {calculated:.6f}, expected is {float(expected):.6f}",
                location=location,
            )
    return run


def check_probabilities(
    checks: Any,
    metrics: dict[str, dict[str, Any]],
    findings: list[dict[str, Any]],
) -> int:
    if not isinstance(checks, list):
        add_finding(findings, "invalid_probability_groups", "checks.probability_groups must be an array", location="checks.probability_groups")
        return 0
    run = 0
    for index, check in enumerate(checks):
        location = f"checks.probability_groups[{index}]"
        if not isinstance(check, dict):
            add_finding(findings, "invalid_probability_check", "probability check must be an object", location=location)
            continue
        referenced = resolve_metrics(check.get("items"), metrics, findings, f"{location}.items")
        if referenced is None:
            continue
        if any(metric.get("value") is None or not finite_number(metric.get("value")) for metric in referenced):
            add_finding(findings, "evidence_missing", "probability group contains an unknown value", location=location)
            continue
        values = [float(metric["value"]) for metric in referenced]
        if any(value < 0 or value > 1 for value in values):
            add_finding(findings, "invalid_probability", "each probability must be within [0, 1]", location=location)
            continue
        target = check.get("target", 1.0)
        allowed = tolerance(check, findings, f"{location}.tolerance")
        if not finite_number(target) or allowed is None:
            add_finding(findings, "invalid_probability_target", "target must be numeric", location=f"{location}.target")
            continue
        run += 1
        if abs(sum(values) - float(target)) > allowed:
            add_finding(
                findings,
                "probability_sum_mismatch",
                f"probabilities sum to {sum(values):.6f}, target is {float(target):.6f}",
                location=location,
            )
    return run


def check_basis_groups(
    checks: Any,
    metrics: dict[str, dict[str, Any]],
    findings: list[dict[str, Any]],
) -> int:
    if not isinstance(checks, list):
        add_finding(findings, "invalid_basis_groups", "checks.basis_groups must be an array", location="checks.basis_groups")
        return 0
    allowed_fields = {"unit", "currency", "period", "basis", "classification"}
    run = 0
    for index, check in enumerate(checks):
        location = f"checks.basis_groups[{index}]"
        if not isinstance(check, dict):
            add_finding(findings, "invalid_basis_check", "basis check must be an object", location=location)
            continue
        referenced = resolve_metrics(check.get("items"), metrics, findings, f"{location}.items")
        fields = check.get("fields")
        if (
            not isinstance(fields, list)
            or not fields
            or not all(isinstance(field, str) and field in allowed_fields for field in fields)
        ):
            add_finding(
                findings,
                "invalid_basis_fields",
                "fields must select unit, currency, period, basis, or classification",
                location=f"{location}.fields",
            )
            continue
        if referenced is None:
            continue
        run += 1
        if not comparable(referenced, tuple(fields)):
            add_finding(
                findings,
                "incompatible_basis",
                "declared comparable metrics differ on: " + ", ".join(fields),
                location=location,
            )
    return run


def validate(data: dict[str, Any]) -> dict[str, Any]:
    findings: list[dict[str, Any]] = []
    if data.get("schema_version", 1) != 1:
        add_finding(findings, "unsupported_schema", "schema_version must be 1", location="schema_version")
    decision_time = None
    if "decision_time" in data:
        decision_time = parse_time(data["decision_time"])
        if decision_time is None:
            add_finding(
                findings,
                "invalid_decision_time",
                "decision_time must be an ISO-8601 timestamp with timezone",
                location="decision_time",
            )
    if "as_of" in data and parse_time(data["as_of"]) is None:
        add_finding(
            findings,
            "invalid_as_of",
            "as_of must be an ISO-8601 timestamp with timezone",
            location="as_of",
        )

    raw_metrics = data.get("metrics")
    if not isinstance(raw_metrics, list) or not raw_metrics:
        add_finding(findings, "invalid_metrics", "metrics must be a non-empty array", location="metrics")
        raw_metrics = []
    metrics: dict[str, dict[str, Any]] = {}
    for index, metric in enumerate(raw_metrics):
        metric_id = validate_metric(metric, index, decision_time, findings)
        if metric_id is None or not isinstance(metric, dict):
            continue
        if metric_id in metrics:
            add_finding(findings, "duplicate_id", f"duplicate metric id: {metric_id}", location=f"metrics[{index}].id")
        else:
            metrics[metric_id] = metric

    checks = data.get("checks", {})
    if not isinstance(checks, dict):
        add_finding(findings, "invalid_checks", "checks must be an object", location="checks")
        checks = {}
    checks_run = {
        "sums": check_sums(checks.get("sums", []), metrics, findings),
        "growth_rates": check_growth_rates(checks.get("growth_rates", []), metrics, findings),
        "probability_groups": check_probabilities(checks.get("probability_groups", []), metrics, findings),
        "basis_groups": check_basis_groups(checks.get("basis_groups", []), metrics, findings),
    }
    return {
        "schema_version": 1,
        "status": "fail" if any(item["severity"] == "error" for item in findings) else "pass",
        "metrics_checked": len(raw_metrics),
        "checks_run": checks_run,
        "findings": findings,
        "limitations": [
            "Arithmetic and metadata checks do not prove that a source supports a value or conclusion.",
            "A clean point-in-time check covers only the timestamps recorded in this file.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate investment data provenance and arithmetic.")
    parser.add_argument("input", type=Path, help="Path to a JSON data-contract file")
    args = parser.parse_args()
    print(json.dumps(validate(load_json(args.input)), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
