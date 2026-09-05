#!/usr/bin/env python3
"""Evaluate decision options from a versioned JSON input.

Version 1 keeps the original all-scores-required interface. Version 2 adds
three-state eligibility, explicit unknown scores, score ranges, grounded
scenarios, and one low-cost validation action.

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


MIN_SCORE = 1.0
MAX_SCORE = 5.0


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


def get_schema_version(data: dict[str, Any]) -> int:
    version = data.get("schema_version", 1)
    if isinstance(version, bool) or not isinstance(version, int) or version not in (1, 2):
        fail("schema_version must be 1 or 2")
    return version


def validate_vetoes(
    vetoes: Any,
    path: str,
    *,
    allow_unresolved: bool,
) -> list[dict[str, Any]]:
    if not isinstance(vetoes, list):
        fail(f"{path} must be an array when provided")
    for index, veto in enumerate(vetoes):
        if not isinstance(veto, dict):
            fail(f"{path}[{index}] must be an object")
        if not isinstance(veto.get("name"), str) or not veto["name"].strip():
            fail(f"{path}[{index}].name must be a non-empty string")
        triggered = veto.get("triggered")
        valid = isinstance(triggered, bool) or (allow_unresolved and triggered is None)
        if not valid:
            expected = "true, false, or null" if allow_unresolved else "true or false"
            fail(f"{path}[{index}].triggered must be {expected}")
    return vetoes


def validate_weights(weights: Any, names: list[str], path: str) -> dict[str, float]:
    if not isinstance(weights, dict):
        fail(f"{path} must be an object")
    missing = [name for name in names if name not in weights]
    extra = [name for name in weights if name not in names]
    if missing:
        fail(f"{path} is missing criteria: {', '.join(missing)}")
    if extra:
        fail(f"{path} has unknown criteria: {', '.join(extra)}")
    normalized: dict[str, float] = {}
    for name in names:
        value = weights[name]
        if not finite_number(value) or float(value) <= 0:
            fail(f"{path}.{name} must be a positive number")
        normalized[name] = float(value)
    total = sum(normalized.values())
    if abs(total - 100.0) > 1e-6:
        fail(f"{path} must sum to 100; got {total:g}")
    return normalized


def validate_score(value: Any, path: str, *, allow_unknown: bool) -> None:
    if value is None and allow_unknown:
        return
    if not finite_number(value):
        fail(f"{path} must be numeric")
    if float(value) < MIN_SCORE or float(value) > MAX_SCORE:
        fail(f"{path} must be between {MIN_SCORE:g} and {MAX_SCORE:g}")


def validate_actions(
    actions: Any,
    path: str,
    criterion_names: list[str],
) -> list[dict[str, Any]]:
    if not isinstance(actions, list):
        fail(f"{path} must be an array when provided")
    for index, action in enumerate(actions):
        item_path = f"{path}[{index}]"
        if not isinstance(action, dict):
            fail(f"{item_path} must be an object")
        if action.get("criterion") not in criterion_names:
            fail(f"{item_path}.criterion must name a configured criterion")
        if not isinstance(action.get("action"), str) or not action["action"].strip():
            fail(f"{item_path}.action must be a non-empty string")
        cost = action.get("cost")
        if cost is not None and (not finite_number(cost) or float(cost) < 0):
            fail(f"{item_path}.cost must be a non-negative number or null")
        if cost is not None and (
            not isinstance(action.get("cost_unit"), str) or not action["cost_unit"].strip()
        ):
            fail(f"{item_path}.cost_unit must name the common comparison unit when cost is numeric")
        changes = action.get("could_change_decision")
        if changes is not None and not isinstance(changes, bool):
            fail(f"{item_path}.could_change_decision must be true, false, or omitted")
    return actions


def validate(data: dict[str, Any]) -> dict[str, Any]:
    version = get_schema_version(data)
    criteria = data.get("criteria")
    options = data.get("options")
    vetoes = data.get("vetoes", [])

    if not isinstance(criteria, list) or not criteria:
        fail("criteria must be a non-empty array")
    if not isinstance(options, list) or not options:
        fail("options must be a non-empty array")

    names: list[str] = []
    base_weights: dict[str, float] = {}
    for index, criterion in enumerate(criteria):
        if not isinstance(criterion, dict):
            fail(f"criteria[{index}] must be an object")
        name = criterion.get("name")
        weight = criterion.get("weight")
        if not isinstance(name, str) or not name.strip():
            fail(f"criteria[{index}].name must be a non-empty string")
        if name in names:
            fail(f"duplicate criterion name: {name}")
        if not finite_number(weight) or float(weight) <= 0:
            fail(f"criterion '{name}' weight must be a positive number")
        names.append(name)
        base_weights[name] = float(weight)
    total_weight = sum(base_weights.values())
    if abs(total_weight - 100.0) > 1e-6:
        fail(f"criteria weights must sum to 100; got {total_weight:g}")

    allow_unknown = version == 2
    vetoes = validate_vetoes(vetoes, "vetoes", allow_unresolved=allow_unknown)
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
        option["vetoes"] = validate_vetoes(
            option.get("vetoes", []),
            f"options[{index}].vetoes",
            allow_unresolved=allow_unknown,
        )
        if not isinstance(scores, dict):
            fail(f"option '{option_name}' scores must be an object")
        missing = [name for name in names if name not in scores]
        extra = [name for name in scores if name not in names]
        if missing:
            suffix = "; use null explicitly for unknown v2 scores" if allow_unknown else ""
            fail(f"option '{option_name}' is missing scores for: {', '.join(missing)}{suffix}")
        if extra:
            fail(f"option '{option_name}' has unknown criteria: {', '.join(extra)}")
        for criterion_name, score in scores.items():
            validate_score(
                score,
                f"score for '{option_name}' / '{criterion_name}'",
                allow_unknown=allow_unknown,
            )
        if version == 2:
            option["validation_actions"] = validate_actions(
                option.get("validation_actions", []),
                f"options[{index}].validation_actions",
                names,
            )

    cost_units = {
        action["cost_unit"]
        for option in options
        for action in option.get("validation_actions", [])
        if action.get("cost") is not None
    }
    if len(cost_units) > 1:
        fail("all numeric validation action costs must use one comparable cost_unit")

    scenarios = data.get("scenarios", [])
    if not isinstance(scenarios, list):
        fail("scenarios must be an array when provided")
    if version == 1 and scenarios:
        fail("scenarios require schema_version 2")
    for index, scenario in enumerate(scenarios):
        path = f"scenarios[{index}]"
        if not isinstance(scenario, dict):
            fail(f"{path} must be an object")
        if not isinstance(scenario.get("name"), str) or not scenario["name"].strip():
            fail(f"{path}.name must be a non-empty string")
        if not isinstance(scenario.get("basis"), str) or not scenario["basis"].strip():
            fail(f"{path}.basis must explain why the scenario is plausible")
        if "weights" in scenario:
            scenario["weights"] = validate_weights(scenario["weights"], names, f"{path}.weights")
        overrides = scenario.get("score_overrides", {})
        if not isinstance(overrides, dict):
            fail(f"{path}.score_overrides must be an object")
        unknown_options = [name for name in overrides if name not in option_names]
        if unknown_options:
            fail(f"{path}.score_overrides has unknown options: {', '.join(unknown_options)}")
        for option_name, score_overrides in overrides.items():
            if not isinstance(score_overrides, dict):
                fail(f"{path}.score_overrides.{option_name} must be an object")
            unknown_criteria = [name for name in score_overrides if name not in names]
            if unknown_criteria:
                fail(
                    f"{path}.score_overrides.{option_name} has unknown criteria: "
                    f"{', '.join(unknown_criteria)}"
                )
            for criterion_name, score in score_overrides.items():
                validate_score(
                    score,
                    f"{path}.score_overrides.{option_name}.{criterion_name}",
                    allow_unknown=True,
                )

    return {
        "version": version,
        "criteria": criteria,
        "base_weights": base_weights,
        "options": options,
        "vetoes": vetoes,
        "scenarios": scenarios,
    }


def recommendation(score: float | None, eligibility: str) -> str:
    if eligibility == "ineligible":
        return "触发硬性否决：不得用总分抵消"
    if eligibility == "unresolved":
        return "先确认未决红线，再比较方案"
    if score is None:
        return "保留为候选；先补齐能改变判断的未知项"
    if score >= 80:
        return "推进或承诺"
    if score >= 65:
        return "有条件推进"
    if score >= 50:
        return "先验证，暂不做不可逆承诺"
    return "暂停、拒绝或寻找替代方案"


def option_eligibility(
    global_vetoes: list[dict[str, Any]],
    option_vetoes: list[dict[str, Any]],
) -> tuple[str, list[dict[str, Any]], list[dict[str, Any]]]:
    combined = global_vetoes + option_vetoes
    triggered = [veto for veto in combined if veto["triggered"] is True]
    unresolved = [veto for veto in combined if veto["triggered"] is None]
    if triggered:
        return "ineligible", triggered, unresolved
    if unresolved:
        return "unresolved", triggered, unresolved
    return "eligible", triggered, unresolved


def compare_results(results: list[dict[str, Any]]) -> dict[str, Any]:
    eligible = [item for item in results if item["eligibility"] == "eligible"]
    unresolved = [item for item in results if item["eligibility"] == "unresolved"]
    if not eligible:
        status = "eligibility_unresolved" if unresolved else "no_eligible_options"
        return {"status": status, "preferred_option": None, "reason": "没有已确认可行的方案。"}
    if unresolved:
        return {
            "status": "eligibility_unresolved",
            "preferred_option": None,
            "reason": "至少一个方案的红线状态未决，不能完成最终比较。",
        }
    if len(eligible) == 1:
        return {
            "status": "single_eligible_option",
            "preferred_option": eligible[0]["option"],
            "reason": "当前只有一个已确认可行的方案。",
        }
    if all(item["total_score"] is not None for item in eligible):
        ordered = sorted(eligible, key=lambda item: item["total_score"], reverse=True)
        if ordered[0]["total_score"] == ordered[1]["total_score"]:
            return {
                "status": "tied",
                "preferred_option": None,
                "reason": "最高总分并列，需要用关键假设或验证动作区分。",
            }
        return {
            "status": "ranked_preference",
            "preferred_option": ordered[0]["option"],
            "reason": "所有可行方案的数据完整，按未重新归一化的加权总分比较。",
        }
    dominant: list[dict[str, Any]] = []
    for candidate in eligible:
        others = [item for item in eligible if item is not candidate]
        if all(candidate["score_range"]["min"] > item["score_range"]["max"] for item in others):
            dominant.append(candidate)
    if len(dominant) == 1:
        return {
            "status": "range_dominant",
            "preferred_option": dominant[0]["option"],
            "reason": "即使把未知项取到允许边界，该方案的分数下界仍高于其他方案上界。",
        }
    return {
        "status": "unresolved_score_ranges",
        "preferred_option": None,
        "reason": "可行方案的分数区间重叠；未知项可能改变首选。",
    }


def evaluate(
    model: dict[str, Any],
    *,
    weights: dict[str, float] | None = None,
    score_overrides: dict[str, dict[str, float | None]] | None = None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    weights = weights or model["base_weights"]
    score_overrides = score_overrides or {}
    results: list[dict[str, Any]] = []
    for option in model["options"]:
        eligibility, triggered_vetoes, unresolved_vetoes = option_eligibility(
            model["vetoes"], option.get("vetoes", [])
        )
        breakdown: list[dict[str, Any]] = []
        lower = 0.0
        upper = 0.0
        total = 0.0
        missing_scores: list[str] = []
        overrides = score_overrides.get(option["name"], {})
        for criterion in model["criteria"]:
            name = criterion["name"]
            weight = float(weights[name])
            score = overrides[name] if name in overrides else option["scores"][name]
            if score is None:
                missing_scores.append(name)
                weighted = None
                lower += weight * MIN_SCORE / MAX_SCORE
                upper += weight
            else:
                weighted = weight * float(score) / MAX_SCORE
                lower += weighted
                upper += weighted
                total += weighted
            breakdown.append(
                {
                    "criterion": name,
                    "weight": weight,
                    "score": score,
                    "weighted_score": None if weighted is None else round(weighted, 2),
                }
            )
        total_score = None if missing_scores else round(total, 2)
        feasible: bool | None = {"eligible": True, "ineligible": False, "unresolved": None}[eligibility]
        results.append(
            {
                "option": option["name"],
                "eligibility": eligibility,
                "feasible": feasible,
                "total_score": total_score,
                "score_range": {"min": round(lower, 2), "max": round(upper, 2)},
                "missing_scores": missing_scores,
                "rank": None,
                "triggered_vetoes": triggered_vetoes,
                "unresolved_vetoes": unresolved_vetoes,
                "recommendation": recommendation(total_score, eligibility),
                "breakdown": breakdown,
            }
        )
    eligible = [item for item in results if item["eligibility"] == "eligible"]
    if eligible and all(item["total_score"] is not None for item in eligible):
        ordered = sorted(eligible, key=lambda item: item["total_score"], reverse=True)
        for rank, item in enumerate(ordered, start=1):
            item["rank"] = rank
    priority = {"eligible": 2, "unresolved": 1, "ineligible": 0}
    results.sort(
        key=lambda item: (
            priority[item["eligibility"]],
            item["total_score"] if item["total_score"] is not None else item["score_range"]["max"],
        ),
        reverse=True,
    )
    return results, compare_results(results)


def choose_validation_action(model: dict[str, Any], results: list[dict[str, Any]]) -> dict[str, Any] | None:
    result_by_name = {item["option"]: item for item in results}
    weight_by_name = model["base_weights"]
    candidates: list[dict[str, Any]] = []
    for option in model["options"]:
        result = result_by_name[option["name"]]
        if result["eligibility"] == "ineligible":
            continue
        supplied: set[str] = set()
        for action in option.get("validation_actions", []):
            criterion = action["criterion"]
            supplied.add(criterion)
            candidate = dict(action)
            candidate["option"] = option["name"]
            candidate["potential_score_swing"] = round(weight_by_name[criterion] * 4 / 5, 2)
            candidates.append(candidate)
        for criterion in result["missing_scores"]:
            if criterion in supplied:
                continue
            candidates.append(
                {
                    "option": option["name"],
                    "criterion": criterion,
                    "action": f"补齐“{criterion}”的可验证数据并记录评分依据",
                    "cost": None,
                    "cost_unit": None,
                    "could_change_decision": None,
                    "potential_score_swing": round(weight_by_name[criterion] * 4 / 5, 2),
                }
            )
        for veto in result["unresolved_vetoes"]:
            candidates.append(
                {
                    "option": option["name"],
                    "criterion": None,
                    "action": f"确认红线“{veto['name']}”是否触发",
                    "cost": None,
                    "cost_unit": None,
                    "could_change_decision": True,
                    "potential_score_swing": None,
                }
            )
    if not candidates:
        return None

    def action_key(item: dict[str, Any]) -> tuple[int, float, float]:
        changes = item.get("could_change_decision")
        change_priority = 0 if changes is True else 1 if changes is None else 2
        cost = float(item["cost"]) if item.get("cost") is not None else math.inf
        swing = item.get("potential_score_swing")
        return change_priority, cost, -(float(swing) if swing is not None else math.inf)

    return sorted(candidates, key=action_key)[0]


def calculate(model: dict[str, Any]) -> dict[str, Any]:
    results, comparison = evaluate(model)
    global_triggered = [veto for veto in model["vetoes"] if veto["triggered"] is True]
    global_unresolved = [veto for veto in model["vetoes"] if veto["triggered"] is None]
    output: dict[str, Any] = {
        "schema_version": model["version"],
        "vetoed": bool(global_triggered),
        "triggered_vetoes": global_triggered,
        "global_vetoed": bool(global_triggered),
        "global_triggered_vetoes": global_triggered,
        "global_unresolved_vetoes": global_unresolved,
        "comparison": comparison,
        "results": results,
    }
    if model["version"] == 2:
        scenario_results: list[dict[str, Any]] = []
        flips: list[dict[str, str]] = []
        base_preference = comparison["preferred_option"]
        comparable = base_preference is not None
        for scenario in model["scenarios"]:
            _, scenario_comparison = evaluate(
                model,
                weights=scenario.get("weights", model["base_weights"]),
                score_overrides=scenario.get("score_overrides", {}),
            )
            scenario_preference = scenario_comparison["preferred_option"]
            scenario_results.append(
                {
                    "name": scenario["name"],
                    "basis": scenario["basis"],
                    "status": scenario_comparison["status"],
                    "preferred_option": scenario_preference,
                }
            )
            if scenario_preference is None:
                comparable = False
            elif base_preference is not None and scenario_preference != base_preference:
                flips.append({"scenario": scenario["name"], "from": base_preference, "to": scenario_preference})
        stable: bool | None
        if not model["scenarios"] or base_preference is None or not comparable:
            stable = None
        else:
            stable = not flips
        output["stability"] = {
            "status": "not_tested" if not model["scenarios"] else "tested",
            "base_preference": base_preference,
            "stable_under_tested_scenarios": stable,
            "preference_flips": flips,
            "scenarios": scenario_results,
        }
        output["next_validation_action"] = choose_validation_action(model, results)
    return output


def to_markdown(result: dict[str, Any]) -> str:
    lines: list[str] = ["# 决策评分结果", ""]
    if result["global_vetoed"]:
        lines.append("**警告：已触发全局硬性否决项，所有方案均不可行，总分不能覆盖该风险。**")
        lines.append("")
        for veto in result["global_triggered_vetoes"]:
            detail = veto.get("detail", "")
            lines.append(f"- {veto['name']}{f'：{detail}' if detail else ''}")
        lines.append("")
    lines.extend(
        [
            "| 可行排名 | 方案 | 可行性 | 总分 | 分数范围 | 建议 |",
            "|---:|---|---|---:|---:|---|",
        ]
    )
    labels = {"eligible": "可行", "ineligible": "不可行", "unresolved": "未决"}
    for item in result["results"]:
        rank = item["rank"] if item["rank"] is not None else "—"
        score = f"{item['total_score']:.2f}" if item["total_score"] is not None else "N/A"
        score_range = f"{item['score_range']['min']:.2f}–{item['score_range']['max']:.2f}"
        lines.append(
            f"| {rank} | {item['option']} | {labels[item['eligibility']]} | "
            f"{score} | {score_range} | {item['recommendation']} |"
        )
    for item in result["results"]:
        lines.extend(
            ["", f"## {item['option']}", "", "| 维度 | 权重 | 评分 | 加权分 |", "|---|---:|---:|---:|"]
        )
        for row in item["breakdown"]:
            score = row["score"] if row["score"] is not None else "未知"
            weighted = f"{row['weighted_score']:.2f}" if row["weighted_score"] is not None else "N/A"
            lines.append(f"| {row['criterion']} | {row['weight']:g} | {score} | {weighted} |")
        if item["triggered_vetoes"]:
            lines.extend(["", "**触发的否决项：**"])
            for veto in item["triggered_vetoes"]:
                detail = veto.get("detail", "")
                lines.append(f"- {veto['name']}{f'：{detail}' if detail else ''}")
        if item["unresolved_vetoes"]:
            lines.extend(["", "**尚未确认的否决项：**"])
            for veto in item["unresolved_vetoes"]:
                lines.append(f"- {veto['name']}")
    comparison = result["comparison"]
    lines.extend(["", "## 比较结论", "", comparison["reason"]])
    if comparison["preferred_option"]:
        lines.append(f"当前首选：**{comparison['preferred_option']}**")
    if result["schema_version"] == 2:
        stability = result["stability"]
        lines.extend(["", "## 稳定性", ""])
        if stability["status"] == "not_tested":
            lines.append("未提供有依据的权重或成本情景；稳定性未测试。")
        elif stability["preference_flips"]:
            for flip in stability["preference_flips"]:
                lines.append(f"- {flip['scenario']}：首选从 {flip['from']} 变为 {flip['to']}")
        else:
            lines.append("已测情景未发现首选翻转。")
        action = result["next_validation_action"]
        if action:
            lines.extend(["", "## 下一步最低成本验证", "", f"- {action['action']}"])
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate feasibility and weighted decision scores.")
    parser.add_argument("input", type=Path, help="Path to the JSON input file")
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    args = parser.parse_args()
    result = calculate(validate(load_json(args.input)))
    if args.format == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(to_markdown(result), end="")


if __name__ == "__main__":
    main()
