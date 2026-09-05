#!/usr/bin/env python3
"""Conservatively flag surface evidence of semantic drift after editing.

This checker is intentionally narrow. It compares high-risk markers and cannot
prove that two passages mean the same thing; a passing result still requires
human or model review of scope, references, and argument structure.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from typing import Any


NUMBER_RE = re.compile(
    r"(?<![A-Za-z0-9_.])[-+]?\d+(?:\.\d+)?(?:%|％|万|亿|元|美元|年|月|日|小时|天|倍)?"
)
NEGATION_TERMS = ("并不是", "并非", "尚未", "未必", "不得", "不能", "没有", "不会", "不", "未", "无")
CONDITION_TERMS = ("只有在", "仅当", "除非", "前提是", "如果", "若", "只要", "在此条件下")
MODALITY_TERMS = ("可能", "或许", "预计", "预期", "初步", "提示", "倾向", "大约", "约", "尚未", "未必")
ATTRIBUTION_TERMS = ("根据", "据", "表示", "指出", "声称", "称", "认为", "报告")
CAUSAL_STRENGTH = {
    "相关": 1,
    "提示": 1,
    "可能影响": 1,
    "表明": 2,
    "支持": 2,
    "造成": 3,
    "导致": 3,
    "证实": 4,
    "证明": 4,
    "必然": 5,
}


def term_counts(text: str, terms: tuple[str, ...]) -> Counter[str]:
    pattern = re.compile("|".join(re.escape(term) for term in sorted(terms, key=len, reverse=True)))
    return Counter(match.group(0) for match in pattern.finditer(text))


def changed_counts(source: Counter[str], revision: Counter[str]) -> dict[str, dict[str, int]]:
    keys = sorted(set(source) | set(revision))
    return {
        key: {"source": source[key], "revision": revision[key]}
        for key in keys
        if source[key] != revision[key]
    }


def max_causal_strength(text: str) -> tuple[int, list[str]]:
    present = [term for term in CAUSAL_STRENGTH if term in text]
    if not present:
        return 0, []
    level = max(CAUSAL_STRENGTH[term] for term in present)
    return level, [term for term in present if CAUSAL_STRENGTH[term] == level]


def add_count_finding(
    findings: list[dict[str, Any]],
    category: str,
    source: Counter[str],
    revision: Counter[str],
    message: str,
) -> None:
    changes = changed_counts(source, revision)
    if changes:
        findings.append({"category": category, "message": message, "changes": changes})


def check(source: str, revision: str, protected_terms: list[str]) -> dict[str, Any]:
    findings: list[dict[str, Any]] = []

    source_numbers = Counter(NUMBER_RE.findall(source))
    revision_numbers = Counter(NUMBER_RE.findall(revision))
    add_count_finding(
        findings,
        "numbers",
        source_numbers,
        revision_numbers,
        "数字、单位或出现次数发生变化；确认这不是事实漂移。",
    )
    add_count_finding(
        findings,
        "negation",
        term_counts(source, NEGATION_TERMS),
        term_counts(revision, NEGATION_TERMS),
        "否定标记发生变化；检查否定对象和范围。",
    )
    add_count_finding(
        findings,
        "conditions",
        term_counts(source, CONDITION_TERMS),
        term_counts(revision, CONDITION_TERMS),
        "条件标记发生变化；检查结论是否失去前提或新增限制。",
    )
    add_count_finding(
        findings,
        "modality",
        term_counts(source, MODALITY_TERMS),
        term_counts(revision, MODALITY_TERMS),
        "可能性或不确定性标记发生变化；检查判断强度。",
    )
    add_count_finding(
        findings,
        "attribution",
        term_counts(source, ATTRIBUTION_TERMS),
        term_counts(revision, ATTRIBUTION_TERMS),
        "来源归属标记发生变化；确认观点仍归属于原说话者或材料。",
    )

    source_level, source_terms = max_causal_strength(source)
    revision_level, revision_terms = max_causal_strength(revision)
    if revision_level != source_level:
        findings.append(
            {
                "category": "causal_strength",
                "message": "修订稿改变了因果或证明措辞的强度。",
                "source": {"level": source_level, "terms": source_terms},
                "revision": {"level": revision_level, "terms": revision_terms},
            }
        )

    missing_terms = [term for term in protected_terms if term in source and term not in revision]
    if missing_terms:
        findings.append(
            {
                "category": "protected_terms",
                "message": "指定保护的主体、来源或术语从修订稿消失。",
                "missing": missing_terms,
            }
        )

    return {
        "status": "review_required" if findings else "pass",
        "findings": findings,
        "limitations": [
            "该检查只比较表面高风险标记，不能证明语义等价。",
            "代词指向、隐含主体、论证顺序和跨句因果仍需人工或模型复核。",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Flag high-risk semantic drift between two passages.")
    parser.add_argument("--source", required=True, help="Original text")
    parser.add_argument("--revision", required=True, help="Edited or translated text")
    parser.add_argument(
        "--protected-term",
        action="append",
        default=[],
        help="Subject, source, term, or phrase that must survive; repeat as needed",
    )
    args = parser.parse_args()
    print(
        json.dumps(
            check(args.source, args.revision, args.protected_term),
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
