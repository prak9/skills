#!/usr/bin/env python3
"""Compute weighted decision scores from a JSON input file.

Usage:
  python scripts/score_options.py assets/sample-score-input.json
  python scripts/score_options.py input.json --format json
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any


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


def validate(data: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    criteria = data.get("criteria")
    options = data.get("options")
    vetoes = data.get("vetoes", [])

    if not isinstance(criteria, list) or not criteria:
        fail("criteria must be a non-empty array")
    if not isinstance(options, list) or not options:
        fail("options must be a non-empty array")
    if not isinstance(vetoes, list):
        fail("vetoes must be an array when provided")

    names: list[str] = []
    total_weight = 0.0
    for index, criterion in enumerate(criteria):
        if not isinstance(criterion, dict):
            fail(f"criteria[{index}] must be an object")
        name = criterion.get("name")
        weight = criterion.get("weight")
        if not isinstance(name, str) or not name.strip():
            fail(f"criteria[{index}].name must be a non-empty string")
        if name in names:
            fail(f"duplicate criterion name: {name}")
        if not isinstance(weight, (int, float)) or not math.isfinite(float(weight)) or weight <= 0:
            fail(f"criterion '{name}' weight must be a positive number")
        names.append(name)
        total_weight += float(weight)

    if abs(total_weight - 100.0) > 1e-6:
        fail(f"criteria weights must sum to 100; got {total_weight:g}")

    option_names: set[str] = set()
    for index, option in enumerate(options):
        if not isinstance(option, dict):
            fail(f"options[{index}] must be an object")
        option_name = option.get("name")
        scores = option.get("scores")
        if not isinstance(option_name, str) or not option_name.strip():
            fail(f"options[{index}].name must be a non-empty string")
        if option_name in option_names:
            fail(f"duplicate option name: {option_name}")
        option_names.add(option_name)
        if not isinstance(scores, dict):
            fail(f"option '{option_name}' scores must be an object")
        missing = [name for name in names if name not in scores]
        extra = [name for name in scores if name not in names]
        if missing:
            fail(f"option '{option_name}' is missing scores for: {', '.join(missing)}")
        if extra:
            fail(f"option '{option_name}' has unknown criteria: {', '.join(extra)}")
        for criterion_name, score in scores.items():
            if not isinstance(score, (int, float)) or not math.isfinite(float(score)):
                fail(f"score for '{option_name}' / '{criterion_name}' must be numeric")
            if float(score) < 1 or float(score) > 5:
                fail(f"score for '{option_name}' / '{criterion_name}' must be between 1 and 5")

    for index, veto in enumerate(vetoes):
        if not isinstance(veto, dict):
            fail(f"vetoes[{index}] must be an object")
        if not isinstance(veto.get("name"), str) or not veto["name"].strip():
            fail(f"vetoes[{index}].name must be a non-empty string")
        if not isinstance(veto.get("triggered"), bool):
            fail(f"vetoes[{index}].triggered must be true or false")

    return criteria, options, vetoes


def recommendation(score: float, vetoed: bool) -> str:
    if vetoed:
        return "触发硬性否决：不得用总分抵消"
    if score >= 80:
        return "推进或承诺"
    if score >= 65:
        return "有条件推进"
    if score >= 50:
        return "先验证，暂不做不可逆承诺"
    return "暂停、拒绝或寻找替代方案"


def calculate(criteria: list[dict[str, Any]], options: list[dict[str, Any]], vetoes: list[dict[str, Any]]) -> dict[str, Any]:
    triggered_vetoes = [v for v in vetoes if v["triggered"]]
    vetoed = bool(triggered_vetoes)
    results: list[dict[str, Any]] = []

    for option in options:
        breakdown = []
        total = 0.0
        for criterion in criteria:
            name = criterion["name"]
            weight = float(criterion["weight"])
            score = float(option["scores"][name])
            weighted = weight * score / 5.0
            total += weighted
            breakdown.append(
                {
                    "criterion": name,
                    "weight": weight,
                    "score": score,
                    "weighted_score": round(weighted, 2),
                }
            )
        total = round(total, 2)
        results.append(
            {
                "option": option["name"],
                "total_score": total,
                "recommendation": recommendation(total, vetoed),
                "breakdown": breakdown,
            }
        )

    results.sort(key=lambda item: item["total_score"], reverse=True)
    return {
        "vetoed": vetoed,
        "triggered_vetoes": triggered_vetoes,
        "results": results,
    }


def to_markdown(result: dict[str, Any]) -> str:
    lines: list[str] = ["# 决策评分结果", ""]
    if result["vetoed"]:
        lines.append("**警告：已触发硬性否决项，总分不能覆盖该风险。**")
        lines.append("")
        for veto in result["triggered_vetoes"]:
            detail = veto.get("detail", "")
            suffix = f"：{detail}" if detail else ""
            lines.append(f"- {veto['name']}{suffix}")
        lines.append("")

    lines.extend([
        "| 方案 | 总分 | 建议 |",
        "|---|---:|---|",
    ])
    for item in result["results"]:
        lines.append(f"| {item['option']} | {item['total_score']:.2f} | {item['recommendation']} |")

    for item in result["results"]:
        lines.extend(["", f"## {item['option']}", "", "| 维度 | 权重 | 评分 | 加权分 |", "|---|---:|---:|---:|"])
        for row in item["breakdown"]:
            lines.append(
                f"| {row['criterion']} | {row['weight']:g} | {row['score']:g} | {row['weighted_score']:.2f} |"
            )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Calculate weighted scores for decision options.")
    parser.add_argument("input", type=Path, help="Path to the JSON input file")
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    args = parser.parse_args()

    data = load_json(args.input)
    criteria, options, vetoes = validate(data)
    result = calculate(criteria, options, vetoes)

    if args.format == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(to_markdown(result), end="")


if __name__ == "__main__":
    main()
