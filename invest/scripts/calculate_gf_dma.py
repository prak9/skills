#!/usr/bin/env python3
"""Deterministically calculate the versioned GF-DMA v1 heuristic from JSON."""

from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
from pathlib import Path
from typing import Any


VERSION = "gf-dma-v1"
SLOPE_EPSILON = 0.00001
GROWTH_EPSILON = 0.01


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


def finite_number(value: Any) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    number = float(value)
    return number if math.isfinite(number) else None


def section(data: dict[str, Any], name: str) -> dict[str, Any]:
    value = data.get(name)
    return value if isinstance(value, dict) else {}


def interpolate(value: float, anchors: list[tuple[float, float]]) -> float:
    if value <= anchors[0][0]:
        return anchors[0][1]
    if value >= anchors[-1][0]:
        return anchors[-1][1]
    for (left_x, left_y), (right_x, right_y) in zip(anchors, anchors[1:]):
        if left_x <= value <= right_x:
            fraction = (value - left_x) / (right_x - left_x)
            return left_y + fraction * (right_y - left_y)
    raise AssertionError("unreachable interpolation range")


def clamp_score(value: float) -> float:
    return round(min(100.0, max(0.0, value)), 2)


def unavailable(reason: str, observations: dict[str, Any] | None = None) -> dict[str, Any]:
    return {
        "score": None,
        "reason": reason,
        "observations": observations or {},
    }


def growth_match(data: dict[str, Any]) -> dict[str, Any]:
    values = section(data, "growth_match")
    fundamental = finite_number(values.get("fundamental_speed_63d"))
    speeds = values.get("dma_speeds_63d")
    if fundamental is None:
        return unavailable("fundamental_speed_63d is missing or non-finite")
    if fundamental <= GROWTH_EPSILON:
        return unavailable(
            "fundamental speed is non-positive or too close to zero for a stable ratio",
            {"fundamental_speed_63d": fundamental},
        )
    if not isinstance(speeds, dict):
        return unavailable("dma_speeds_63d must contain comparable 50 and 100 values")
    dma50 = finite_number(speeds.get("50"))
    dma100 = finite_number(speeds.get("100"))
    if dma50 is None or dma100 is None:
        return unavailable("both 50DMA and 100DMA 63-day speeds are required")
    ratios = {"50": dma50 / fundamental, "100": dma100 / fundamental}
    primary_ratio = statistics.median(ratios.values())
    score = interpolate(
        primary_ratio,
        [
            (-1.0, 10.0),
            (0.0, 35.0),
            (0.5, 75.0),
            (0.8, 90.0),
            (1.0, 100.0),
            (1.3, 90.0),
            (2.0, 60.0),
            (2.5, 35.0),
            (4.0, 10.0),
        ],
    )
    return {
        "score": clamp_score(score),
        "reason": "median 50/100DMA speed divided by positive comparable fundamental speed",
        "observations": {
            "fundamental_speed_63d": fundamental,
            "dma_speeds_63d": {"50": dma50, "100": dma100},
            "ratios": {key: round(value, 6) for key, value in ratios.items()},
            "primary_ratio": round(primary_ratio, 6),
        },
    }


def d20_penalty(value: float) -> float:
    if value <= 0.05:
        return 0.0
    if value <= 0.12:
        return interpolate(value, [(0.05, 0.0), (0.12, 15.0)])
    if value <= 0.20:
        return interpolate(value, [(0.12, 15.0), (0.20, 35.0)])
    return 35.0 + min(25.0, (value - 0.20) * 125.0)


def positive_excess_penalty(value: float, threshold: float, scale: float, cap: float) -> float:
    return min(cap, max(0.0, value - threshold) * scale)


def divergence(data: dict[str, Any]) -> dict[str, Any]:
    values = section(data, "divergence")
    names = ("d20", "d50", "d100", "d200", "z20")
    numbers = {name: finite_number(values.get(name)) for name in names}
    missing = [name for name, value in numbers.items() if value is None]
    stable = values.get("fundamentals_stable_or_improving")
    revisions = values.get("revisions_nonnegative")
    if missing:
        return unavailable("missing or non-finite divergence inputs: " + ", ".join(missing))
    if not isinstance(stable, bool) or not isinstance(revisions, bool):
        return unavailable("both divergence fundamental/revision gates must be boolean")

    d20 = numbers["d20"]
    d50 = numbers["d50"]
    d100 = numbers["d100"]
    d200 = numbers["d200"]
    z20 = numbers["z20"]
    assert None not in (d20, d50, d100, d200, z20)

    penalties = {
        "d20": d20_penalty(d20),
        "d50": positive_excess_penalty(d50, 0.30, 100.0, 20.0),
        "d100": positive_excess_penalty(d100, 0.50, 50.0, 15.0),
        "d200": positive_excess_penalty(d200, 1.00, 20.0, 10.0),
        "z20": 0.0 if z20 <= 2.0 else interpolate(
            min(z20, 5.0),
            [(2.0, 0.0), (3.0, 10.0), (4.0, 20.0), (5.0, 35.0)],
        ),
    }
    pullback_bonus = 0.0
    breakdown_penalty = 0.0
    if stable and revisions:
        mild_20 = d20 < 0.0 and d50 >= 0.0
        healthy_50 = -0.15 <= d50 < 0.0 and d100 >= 0.0 and d200 >= 0.0
        if mild_20 or healthy_50:
            pullback_bonus = 5.0
    else:
        breakdown_penalty += min(25.0, max(0.0, -d50) * 100.0)
        breakdown_penalty += min(20.0, max(0.0, -d100) * 100.0)
        breakdown_penalty += min(25.0, max(0.0, -d200) * 100.0)

    score = 90.0 - sum(penalties.values()) - breakdown_penalty + pullback_bonus
    return {
        "score": clamp_score(score),
        "reason": "versioned price/DMA/ATR stretch and pullback mapping",
        "observations": {
            **{name: numbers[name] for name in names},
            "fundamentals_stable_or_improving": stable,
            "revisions_nonnegative": revisions,
            "penalties": {key: round(value, 2) for key, value in penalties.items()},
            "breakdown_penalty": round(breakdown_penalty, 2),
            "pullback_bonus": pullback_bonus,
        },
    }


def parallel(data: dict[str, Any]) -> dict[str, Any]:
    values = section(data, "parallel")
    price_slope = finite_number(values.get("price_daily_slope_5d"))
    dma_slope = finite_number(values.get("dma50_daily_slope_5d"))
    if price_slope is None or dma_slope is None:
        return unavailable("both normalized five-day daily slopes are required")
    observations = {
        "price_daily_slope_5d": price_slope,
        "dma50_daily_slope_5d": dma_slope,
    }
    if abs(dma_slope) <= SLOPE_EPSILON:
        return unavailable("50DMA daily slope is near zero; EscapeRatio is unstable", observations)
    if dma_slope < 0:
        return unavailable(
            "parallel-health scoring requires a positive 50DMA slope; two negative slopes are not healthy",
            observations,
        )
    ratio = price_slope / dma_slope
    score = interpolate(
        ratio,
        [
            (-1.0, 10.0),
            (0.0, 30.0),
            (0.5, 60.0),
            (0.8, 85.0),
            (1.0, 100.0),
            (1.2, 90.0),
            (1.8, 65.0),
            (2.5, 35.0),
            (4.0, 10.0),
        ],
    )
    observations["escape_ratio"] = round(ratio, 6)
    return {
        "score": clamp_score(score),
        "reason": "price slope relative to a positive, non-flat 50DMA slope",
        "observations": observations,
    }


def revision(data: dict[str, Any]) -> dict[str, Any]:
    values = section(data, "revision")
    names = ("revenue_30d", "eps_30d", "guide_vs_consensus")
    available = {
        name: number
        for name in names
        if (number := finite_number(values.get(name))) is not None
    }
    if len(available) < 2:
        return unavailable("at least two comparable revision inputs are required", available)
    primary = statistics.median(available.values())
    score = interpolate(
        primary,
        [(-0.10, 10.0), (-0.05, 35.0), (0.0, 60.0), (0.05, 85.0), (0.10, 100.0)],
    )
    return {
        "score": clamp_score(score),
        "reason": "median of at least two comparable 30-day revision/guide gaps",
        "observations": {**available, "median_revision": round(primary, 6)},
    }


def calculate(data: dict[str, Any]) -> dict[str, Any]:
    modules = {
        "growth_match": growth_match(data),
        "divergence": divergence(data),
        "parallel": parallel(data),
        "revision": revision(data),
    }
    missing = [name for name, result in modules.items() if result["score"] is None]
    return {
        "heuristic_version": VERSION,
        "calibration": "uncalibrated heuristic; validate on point-in-time holdout data",
        "aggregate_enabled": False,
        "aggregate_status": (
            "disabled until module mappings, valid domains, and aggregate weights are calibrated "
            "on point-in-time holdout data"
        ),
        "scorable": False,
        "health_score": None,
        "state": "N/A",
        "missing_modules": missing,
        "modules": modules,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Calculate the GF-DMA v1 heuristic.")
    parser.add_argument("input", type=Path, help="JSON input path")
    args = parser.parse_args()
    print(json.dumps(calculate(load_json(args.input)), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
