#!/usr/bin/env python3
"""Extract discrete risk-neutral terminal-price probabilities from cleaned calls."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import math
import sys
from pathlib import Path


REQUIRED_FIELDS = {
    "quote_timestamp", "expiration", "spot", "risk_free_rate",
    "option_style", "price_basis", "calls",
}
ALLOWED_STYLES = {"european", "european_equivalent"}


def number(value: object, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be a finite number")
    value = float(value)
    if not math.isfinite(value):
        raise ValueError(f"{name} must be a finite number")
    return value


def iso_date(value: object, name: str) -> dt.date:
    if not isinstance(value, str):
        raise ValueError(f"{name} must be YYYY-MM-DD")
    try:
        return dt.date.fromisoformat(value)
    except ValueError as error:
        raise ValueError(f"{name} must be YYYY-MM-DD") from error


def zoned_timestamp(value: object) -> dt.datetime:
    if not isinstance(value, str):
        raise ValueError("quote_timestamp must be an ISO-8601 timestamp with timezone")
    try:
        parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise ValueError("quote_timestamp must be an ISO-8601 timestamp with timezone") from error
    if parsed.utcoffset() is None:
        raise ValueError("quote_timestamp must include a timezone")
    return parsed


def validate(raw: object) -> dict:
    if not isinstance(raw, dict):
        raise ValueError("input must be an object")
    missing = REQUIRED_FIELDS - raw.keys()
    unknown = raw.keys() - REQUIRED_FIELDS
    if missing or unknown:
        raise ValueError(f"missing fields: {sorted(missing)}; unknown fields: {sorted(unknown)}")

    quote_timestamp = zoned_timestamp(raw["quote_timestamp"])
    valuation_date = quote_timestamp.date()
    expiration = iso_date(raw["expiration"], "expiration")
    days = (expiration - valuation_date).days
    if days <= 0:
        raise ValueError("expiration must be after valuation_date")

    spot = number(raw["spot"], "spot")
    rate = number(raw["risk_free_rate"], "risk_free_rate")
    if spot <= 0:
        raise ValueError("spot must be positive")
    if raw["option_style"] not in ALLOWED_STYLES:
        raise ValueError("option_style must be european or european_equivalent; raw American prices are unsupported")
    if not isinstance(raw["price_basis"], str) or not raw["price_basis"].strip():
        raise ValueError("price_basis must be a nonempty description")
    if not isinstance(raw["calls"], list) or len(raw["calls"]) < 3:
        raise ValueError("calls must contain at least three strike prices")

    calls = []
    for index, item in enumerate(raw["calls"]):
        if not isinstance(item, dict) or set(item) != {"strike", "call_price"}:
            raise ValueError(f"calls[{index}] must contain exactly strike and call_price")
        strike = number(item["strike"], f"calls[{index}].strike")
        price = number(item["call_price"], f"calls[{index}].call_price")
        if strike <= 0 or price < 0:
            raise ValueError("strikes must be positive and call prices nonnegative")
        calls.append({"strike": strike, "call_price": price})
    calls.sort(key=lambda item: item["strike"])
    if len({item["strike"] for item in calls}) != len(calls):
        raise ValueError("duplicate strikes are unsupported")

    return {
        "quote_timestamp": quote_timestamp.isoformat(),
        "valuation_date": valuation_date.isoformat(),
        "expiration": expiration.isoformat(),
        "days_to_expiration": days,
        "time_years_act_365_25": days / 365.25,
        "spot": spot,
        "risk_free_rate": rate,
        "option_style": raw["option_style"],
        "price_basis": raw["price_basis"].strip(),
        "calls": calls,
    }


def calculate(raw: object) -> dict:
    data = validate(raw)
    calls = data["calls"]
    discount_inverse = math.exp(data["risk_free_rate"] * data["time_years_act_365_25"])
    tolerance = 1e-10
    thresholds = []

    for left, right in zip(calls, calls[1:]):
        width = right["strike"] - left["strike"]
        tail = discount_inverse * (left["call_price"] - right["call_price"]) / width
        threshold = (left["strike"] + right["strike"]) / 2
        if tail < -tolerance or tail > 1 + tolerance:
            raise ValueError(f"vertical-spread probability outside [0,1] near strike {threshold}")
        thresholds.append({
            "terminal_price_threshold": threshold,
            "return_from_spot": threshold / data["spot"] - 1,
            "probability_above": min(1.0, max(0.0, tail)),
            "probability_at_or_below": 1 - min(1.0, max(0.0, tail)),
            "source_strikes": [left["strike"], right["strike"]],
        })

    for earlier, later in zip(thresholds, thresholds[1:]):
        if later["probability_above"] > earlier["probability_above"] + tolerance:
            raise ValueError("call prices violate convexity: tail probability rises with strike")

    buckets = [{
        "lower_exclusive": None,
        "upper_inclusive": thresholds[0]["terminal_price_threshold"],
        "probability": thresholds[0]["probability_at_or_below"],
    }]
    for lower, upper in zip(thresholds, thresholds[1:]):
        buckets.append({
            "lower_exclusive": lower["terminal_price_threshold"],
            "upper_inclusive": upper["terminal_price_threshold"],
            "probability": lower["probability_above"] - upper["probability_above"],
        })
    buckets.append({
        "lower_exclusive": thresholds[-1]["terminal_price_threshold"],
        "upper_inclusive": None,
        "probability": thresholds[-1]["probability_above"],
    })

    return {
        "status": "ok",
        "model_version": "discrete-call-spread-risk-neutral-v1",
        "inputs": data,
        "horizon_note": "approximately_one_year" if 274 <= data["days_to_expiration"] <= 456 else "outside_9_to_15_month_window",
        "threshold_probabilities": thresholds,
        "range_probabilities": buckets,
        "interpretation": "Risk-neutral terminal-price probabilities from cleaned European-equivalent calls; not objective forecasts or fundamental scenario weights.",
        "tail_note": "Open-ended edge buckets are probability mass outside the usable strike grid; their internal distribution is not estimated.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="JSON input; see references/options-implied-distribution.md")
    args = parser.parse_args()
    try:
        result = calculate(json.loads(args.input.read_text(encoding="utf-8")))
        output = json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False)
    except (OSError, ValueError, OverflowError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 2
    print(output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
