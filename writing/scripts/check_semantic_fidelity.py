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
import unicodedata
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
ENGLISH_TERMS = {
    "negation": ("not", "no", "never", "neither", "nor", "without", "cannot", "can't", "won't", "isn't", "aren't", "wasn't", "weren't", "don't", "doesn't", "didn't", "hasn't", "haven't", "hadn't", "couldn't", "shouldn't", "wouldn't", "mustn't"),
    "conditions": ("only if", "even if", "if", "unless", "provided that", "providing that", "as long as", "on condition that"),
    "modality": ("may", "might", "can", "could", "should", "must", "will", "would", "possibly", "probably", "likely", "perhaps", "approximately", "expected", "estimated", "preliminary"),
}
MARKER_CATEGORIES = ("negation", "conditions", "modality", "attribution", "causal_strength")


def language_scope(text: str, declared: str) -> str:
    """Determine script coverage, not the language of arbitrary Latin text."""
    letters = [char for char in text if char.isalpha()]
    if not letters:
        return "unknown"
    han = any("\u3400" <= char <= "\u9fff" for char in letters)
    other_script = any(
        not ("\u3400" <= char <= "\u9fff" or "LATIN" in unicodedata.name(char, ""))
        for char in letters
    )
    if other_script or declared == "other":
        return "unsupported"
    if han and any("LATIN" in unicodedata.name(char, "") for char in letters):
        return "mixed"
    if declared == "zh":
        return "zh" if han else "unknown"
    if declared == "en":
        return "en" if not han else "mixed"
    return "zh" if han else "latin_unknown"


def english_counts(text: str, terms: tuple[str, ...]) -> Counter[str]:
    normalized = " ".join(text.casefold().replace("’", "'").split())
    pattern = re.compile(r"(?<![\w'])\b(?:" + "|".join(
        re.escape(term) for term in sorted(terms, key=len, reverse=True)
    ) + r")\b(?![\w'])")
    return Counter(match.group(0) for match in pattern.finditer(normalized))


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


def check(
    source: str,
    revision: str,
    protected_terms: list[str],
    *,
    source_language: str = "auto",
    revision_language: str = "auto",
) -> dict[str, Any]:
    findings: list[dict[str, Any]] = []
    source_scope = language_scope(source, source_language)
    revision_scope = language_scope(revision, revision_language)
    chinese = source_scope == revision_scope == "zh"
    english = {source_scope, revision_scope} <= {"en", "latin_unknown"}
    confirmed = chinese or source_scope == revision_scope == "en"
    evaluated: list[str] = []

    source_numbers = Counter(NUMBER_RE.findall(source))
    revision_numbers = Counter(NUMBER_RE.findall(revision))
    add_count_finding(
        findings,
        "numbers",
        source_numbers,
        revision_numbers,
        "数字、单位或出现次数发生变化；确认这不是事实漂移。",
    )
    for category, terms, message in (
        ("negation", NEGATION_TERMS, "否定标记发生变化；检查否定对象和范围。"),
        ("conditions", CONDITION_TERMS, "条件标记发生变化；检查结论是否失去前提或新增限制。"),
        ("modality", MODALITY_TERMS, "可能性或不确定性标记发生变化；检查判断强度。"),
        ("attribution", ATTRIBUTION_TERMS, "来源归属标记发生变化；确认观点仍归属于原说话者或材料。"),
    ):
        if chinese:
            before, after = term_counts(source, terms), term_counts(revision, terms)
        elif english and category in ENGLISH_TERMS:
            before = english_counts(source, ENGLISH_TERMS[category])
            after = english_counts(revision, ENGLISH_TERMS[category])
        else:
            continue
        evaluated.append(category)
        add_count_finding(findings, category, before, after, message)

    if chinese:
        evaluated.append("causal_strength")
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

    if english and not confirmed and not any(
        english_counts(text, terms)
        for text in (source, revision) for terms in ENGLISH_TERMS.values()
    ):
        evaluated = []

    marker_coverage = {
        "status": "evaluated" if confirmed else "partial" if evaluated else "not_evaluated",
        "evaluated": evaluated,
        "not_evaluated": [category for category in MARKER_CATEGORIES if category not in evaluated],
        "reason": (
            "仅比较同语言词面标记；不是语义等价验证。" if confirmed else
            "拉丁字母不等于英文；仅探测英文标记，确认语言后可显式指定 en。" if english else
            "跨语言、混合文字、空文本或不支持的文字不比较语言标记。"
        )
    }

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
        "status": "review_required" if findings else "pass" if confirmed else "not_evaluated",
        "findings": findings,
        "coverage": {
            "source_language": source_scope,
            "revision_language": revision_scope,
            "marker_comparison": marker_coverage,
            "numbers": "surface_only",
            "protected_terms": "literal_only" if protected_terms else "not_requested",
            "semantic_equivalence": "not_evaluated",
        },
        "limitations": [
            "该检查只比较表面高风险标记，不能证明语义等价。",
            "代词指向、隐含主体、论证顺序和跨句因果仍需人工或模型复核。",
            "自动模式按文字范围选择词表，不可靠识别语言；汉字也可能属于其他语言。已知语言请显式指定。",
            "英文只覆盖有限否定、条件和情态词；同次数换对象、同义改写和缩写可能漏报或误报。",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Flag high-risk semantic drift between two passages.")
    parser.add_argument("--source", required=True, help="Original text")
    parser.add_argument("--revision", required=True, help="Edited or translated text")
    for side in ("source", "revision"):
        parser.add_argument(
            f"--{side}-language", choices=("auto", "zh", "en", "other"), default="auto",
            help="Known language; auto selects script/marker coverage, not reliable language identification",
        )
    parser.add_argument(
        "--protected-term",
        action="append",
        default=[],
        help="Subject, source, term, or phrase that must survive; repeat as needed",
    )
    args = parser.parse_args()
    print(
        json.dumps(
            check(
                args.source, args.revision, args.protected_term,
                source_language=args.source_language,
                revision_language=args.revision_language,
            ),
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
