#!/usr/bin/env python3
"""Conditional two-stage FCFE/base-EPS valuation. Stdlib, JSON in/out, read-only."""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path


ECONOMIC_FIELDS = {
    "base_eps", "years", "cost_of_equity", "cash_conversion",
    "terminal_cash_conversion", "terminal_growth",
}
OPTIONAL_FIELDS = {
    "pe", "growth", "pe_basis", "forward_eps_ratio", "growth_bounds", "scenarios",
}
SENSITIVITY_FIELDS = ECONOMIC_FIELDS - {"base_eps"}


def number(value: object, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be a finite number")
    if not math.isfinite(value):
        raise ValueError(f"{name} must be a finite number")
    return float(value)


def validate(data: dict) -> dict:
    if not isinstance(data, dict):
        raise ValueError("input must be an object")
    missing = ECONOMIC_FIELDS - data.keys()
    unknown = data.keys() - ECONOMIC_FIELDS - OPTIONAL_FIELDS
    if missing or unknown:
        raise ValueError(f"missing fields: {sorted(missing)}; unknown fields: {sorted(unknown)}")
    result = dict(data)
    for field in ECONOMIC_FIELDS:
        result[field] = number(data[field], field)
    if result["base_eps"] <= 0:
        raise ValueError("base_eps must be positive normalized common-share EPS")
    years = result["years"]
    if not years.is_integer() or not 1 <= years <= 100:
        raise ValueError("years must be an integer in 1..100 (calculator scope)")
    result["years"] = int(years)
    r, h = result["cost_of_equity"], result["terminal_growth"]
    if r <= 0 or h <= -1 or r <= h:
        raise ValueError("require cost_of_equity > 0, terminal_growth > -1 and cost_of_equity > terminal_growth")
    for field in ("cash_conversion", "terminal_cash_conversion"):
        if not 0 <= result[field] <= 1:
            raise ValueError(f"{field} outside supported [0, 1]; use a fuller FCFE model")
    if result["cash_conversion"] == result["terminal_cash_conversion"] == 0:
        raise ValueError("both cash conversions are zero; no positive-price growth solution")
    if ("pe" in data) == ("growth" in data):
        raise ValueError("supply exactly one of pe (inverse) or growth (forward)")
    if "pe" in data:
        result["pe"] = number(data["pe"], "pe")
        if result["pe"] <= 0:
            raise ValueError("pe must be positive")
    else:
        result["growth"] = number(data["growth"], "growth")
        if result["growth"] <= -1:
            raise ValueError("growth must exceed -1")
    basis = data.get("pe_basis", "base")
    if basis not in ("base", "forward"):
        raise ValueError("pe_basis must be base or forward")
    result["pe_basis"] = basis
    if basis == "forward":
        if "pe" not in data or "forward_eps_ratio" not in data:
            raise ValueError("forward PE requires pe and explicit forward_eps_ratio = EPS1/EPS0")
        result["forward_eps_ratio"] = number(data["forward_eps_ratio"], "forward_eps_ratio")
        if result["forward_eps_ratio"] <= 0:
            raise ValueError("forward_eps_ratio must be positive")
    elif "forward_eps_ratio" in data:
        raise ValueError("forward_eps_ratio is only applicable to forward PE")
    if "growth" in data and "growth_bounds" in data:
        raise ValueError("growth_bounds only apply to inverse calculation")
    if "pe" in data:
        bounds = data.get("growth_bounds", [-0.99, 1.0])
        if not isinstance(bounds, list) or len(bounds) != 2:
            raise ValueError("growth_bounds must contain two numbers")
        lower, upper = [number(value, "growth_bounds") for value in bounds]
        if not -1 < lower < upper:
            raise ValueError("require -1 < lower growth bound < upper growth bound")
        result["growth_bounds"] = [lower, upper]
    return result


def value_at_growth(data: dict, growth: float) -> dict:
    r, h, n = data["cost_of_equity"], data["terminal_growth"], data["years"]
    q = (1 + growth) / (1 + r)
    # Direct summation also handles q == 1; no geometric-series singularity.
    period = data["cash_conversion"] * math.fsum(q ** t for t in range(1, n + 1))
    terminal = data["terminal_cash_conversion"] * (1 + h) / (r - h) * q ** n
    pe = period + terminal
    if not math.isfinite(pe) or pe <= 0:
        raise ValueError("valuation overflow/underflow; rescale inputs or narrow growth bounds")
    return {"base_pe": pe, "period_pv_per_base_eps": period,
            "terminal_pv_per_base_eps": terminal, "terminal_value_share": terminal / pe}


def reinvestment_diagnostic(growth: float, conversion: float) -> dict:
    retention = 1 - conversion
    if growth < 0:
        required, reason = None, "Contraction is not a positive reinvestment-return estimate."
    elif retention <= 1e-12:
        required, reason = None, "No identifiable reinvestment denominator; explain another growth mechanism if growth is positive."
    else:
        required, reason = growth / retention, "Conditional on growth funded by net equity reinvestment; not measured ROE."
    return {"equity_reinvestment_rate_proxy": retention,
            "required_incremental_equity_return": required, "reason": reason}


def run_case(raw: dict) -> dict:
    data = validate(raw)
    data.pop("scenarios", None)
    output = {"inputs": data, "status": "ok", "growth": None, "valuation": None}
    target = None
    if "pe" in data:
        target = data["pe"] * data.get("forward_eps_ratio", 1.0)
        if not math.isfinite(target):
            raise ValueError("converted base PE is nonfinite")
        output["target_base_pe"] = target
        lower, upper = data["growth_bounds"]
        attainable = [value_at_growth(data, bound)["base_pe"] for bound in (lower, upper)]
        output["solver"] = {"bounds": [lower, upper], "pe_at_bounds": attainable}
        if not attainable[0] <= target <= attainable[1]:
            output.update(status="unbracketed", reason="No root inside these numerical bounds; not proof of economic impossibility.")
            return output
        for iteration in range(200):
            growth = (lower + upper) / 2
            residual = value_at_growth(data, growth)["base_pe"] - target
            if abs(residual) <= 1e-10 * target:
                break
            if residual < 0:
                lower = growth
            else:
                upper = growth
        else:
            output.update(status="not_converged", reason="No validated root within iteration budget.")
            return output
        output["solver"].update(iterations=iteration + 1, residual_pe=residual)
    else:
        growth = data["growth"]
    valuation = value_at_growth(data, growth)
    multiplier = (1 + growth) ** data["years"]
    price = data["base_eps"] * valuation["base_pe"]
    end_eps = data["base_eps"] * multiplier
    if not all(math.isfinite(value) for value in (price, end_eps, multiplier)):
        raise ValueError("price or terminal-year EPS overflow")
    valuation.update(price=price, eps_end_year=end_eps, eps_end_multiple=multiplier)
    output.update(growth=growth, valuation=valuation, diagnostics={
        "first_stage": reinvestment_diagnostic(growth, data["cash_conversion"]),
        "terminal_stage": reinvestment_diagnostic(data["terminal_growth"], data["terminal_cash_conversion"]),
        "contraction_then_terminal_recovery": growth < 0 < data["terminal_growth"],
    })
    return output


def calculate(data: dict) -> dict:
    result = run_case(data)
    result["model_version"] = "conditional-pe-fcfe-v1"
    result["interpretation"] = "Conditional EPS-growth hurdle, not observed consensus, probability, or a buy signal. Fixed share basis; no separate nonoperating assets."
    scenarios = data.get("scenarios", [])
    if not isinstance(scenarios, list):
        raise ValueError("scenarios must be a list")
    if scenarios:
        result["scenarios"] = []
    names = set()
    for scenario in scenarios:
        if not isinstance(scenario, dict) or set(scenario) != {"name", "overrides"}:
            raise ValueError("each scenario requires name and overrides")
        name, overrides = scenario["name"], scenario["overrides"]
        if not isinstance(name, str) or not name.strip() or name in names:
            raise ValueError("scenario names must be nonempty and unique")
        names.add(name)
        if not isinstance(overrides, dict) or not overrides or not set(overrides) <= SENSITIVITY_FIELDS:
            raise ValueError(f"scenario overrides must use {sorted(SENSITIVITY_FIELDS)}")
        result["scenarios"].append({"name": name, "overrides": overrides,
                                    "result": run_case({**data, **overrides})})
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="JSON input; see references/pe-implied-growth.md")
    args = parser.parse_args()
    try:
        result = calculate(json.loads(args.input.read_text(encoding="utf-8")))
        rendered = json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False)
    except (OSError, ValueError, OverflowError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 2
    print(rendered)
    return 0


if __name__ == "__main__":
    sys.exit(main())
