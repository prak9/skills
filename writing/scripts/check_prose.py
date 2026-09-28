#!/usr/bin/env python3
"""Read-only Chinese prose diagnostics; signals are advisory, never an AI detector.

Informed by human-writing 1.1.0. Attribution and MIT permission are retained in
../references/human-writing-source.md. This implementation deliberately omits
the upstream hard bans, authorship thresholds and mandatory warning cleanup.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


HAN = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff]")
CONJUNCTIONS = re.compile(r"因为|所以|但是|然而|同时|此外|而且|并且|因此|不仅")
PATTERNS = {
    "pivot_shape": (
        r"(?:不是|并非)[^。！？!?\n]{0,90}(?:而是|，是)",
        r"(?:不是|并非)[^。！？!?\n]{0,90}[。！？!?]\s*而是",
        r"不在于[^。！？!?\n]{0,90}而在于",
        r"与其说[^。！？!?\n]{0,90}(?:倒不如|不如|毋宁)",
        r"以为[^！？!?\n]{0,70}?(?:其实|才发现|才明白)",
        r"(?:表面|看似)[^！？!?\n]{0,70}?(?:实际|实则|其实)",
    ),
    "nominalization": (
        r"(?:完成了对|进行了对)[^。，！？!?\n]{1,24}的(?:优化|调整|分析|梳理)",
        r"进行了[^。，！？!?\n]{0,12}(?:优化|调整|分析|沟通)",
        r"实现了[^。，！？!?\n]{0,18}的(?:提升|增长|转变)",
    ),
    "signpost": (r"(?:值得注意的是|需要指出的是|从某种意义上说|更微妙的是)",),
}
NOTES = {
    "pivot_shape": "核对是否空设误解来抬高判断；真实纠错、对照与有材料的自我修正可保留。",
    "nominalization": "核对能否直接写行动者与动作；保留有专业含义或特定语气的表达。",
    "signpost": "核对路标是否帮助理解，还是代替了实际联系；不按词命中自动删除。",
    "parallel_shape": "核对同构句是否逐项推进；真实并列、修辞需要和用户指定风格可保留。",
    "repeated_sentence": "核对重复是否承担照应、强调或必要复述；只合并没有作用的重复。",
}


def blank(value: str) -> str:
    return "".join("\n" if char == "\n" else " " for char in value)


def mask_protected(text: str) -> str:
    """Mask common Markdown and quotation regions without shifting offsets."""
    text = re.sub(r"\A---[ \t]*\n.*?\n---[ \t]*(?:\n|$)",
                  lambda m: blank(m.group()), text, flags=re.DOTALL)
    lines = []
    fence = None
    for line in text.splitlines(keepends=True):
        marker = re.match(r"^ {0,3}(`{3,}|~{3,})(.*)$", line.rstrip("\r\n"))
        if fence:
            lines.append(blank(line))
            if (marker and marker[1][0] == fence[0] and len(marker[1]) >= len(fence)
                    and not marker[2].strip()):
                fence = None
        elif marker:
            fence = marker[1]
            lines.append(blank(line))
        elif re.match(r"^(?: {0,3}>| {4}|\t| {0,3}#{1,6}\s)", line):
            lines.append(blank(line))
        else:
            lines.append(line)
    text = "".join(lines)
    for pattern in (
        r"(?<!`)(`+)(?!`)[^\n]*?(?<!`)\1(?!`)",
        r"(?<=\])\([^\n)]*\)",
        r"https?://[^\s)>]+",
        r"<[^>\n]+>",
        r'“[^”]*”|「[^」]*」|『[^』]*』|‘[^’]*’|"(?:\\.|[^"\\])*"',
    ):
        text = re.sub(pattern, lambda m: blank(m.group()), text)
    return text


def analyze(text: str, genre: str = "prose") -> dict:
    prose = mask_protected(text)
    han_count = len(HAN.findall(prose))
    sentences = [m for m in re.finditer(r"[^。！？!?\n]+[。！？!?]?", prose)
                 if HAN.search(m.group())]
    lengths = [len(HAN.findall(m.group())) for m in sentences]
    mean = sum(lengths) / len(lengths) if lengths else None
    cv = ((sum((n - mean) ** 2 for n in lengths) / len(lengths)) ** 0.5 / mean
          if len(lengths) >= 2 else None)
    metrics = {
        "han_count": han_count,
        "sentence_count": len(sentences),
        "mean_sentence_han": mean,
        "sentence_length_cv": cv,
        "conjunctions_per_1000_han": (len(CONJUNCTIONS.findall(prose)) * 1000 / han_count
                                      if han_count else None),
        "paragraph_han_counts": [len(HAN.findall(p)) for p in re.split(r"\n\s*\n", prose)
                                 if HAN.search(p)],
    }
    findings = []
    seen = set()

    def add(category, start, end):
        key = (category, start, end)
        if key in seen:
            return
        seen.add(key)
        findings.append({"category": category, "severity": "advisory",
                         "start": start, "end": end,
                         "line": text.count("\n", 0, start) + 1,
                         "excerpt": text[start:end], "question": NOTES[category]})

    if han_count and genre == "prose":
        for category, patterns in PATTERNS.items():
            for pattern in patterns:
                for match in re.finditer(pattern, prose):
                    add(category, *match.span())
        repeated = set()
        for sentence, length in zip(sentences, lengths):
            value = sentence.group().strip()
            if length >= 4 and value in repeated:
                start = sentence.start() + len(sentence.group()) - len(sentence.group().lstrip())
                add("repeated_sentence", start, start + len(value))
            repeated.add(value)
            clauses = [s.strip() for s in re.split(r"[，、；,;]", value)]
            for index in range(len(clauses) - 2):
                group = clauses[index:index + 3]
                if (all(len(HAN.findall(s)) >= 3 for s in group)
                        and re.fullmatch(r"[\u4e00-\u9fff]{2}", group[0][:2])
                        and len({s[:2] for s in group}) == 1):
                    add("parallel_shape", *sentence.span())
                    break
    findings.sort(key=lambda f: (f["start"], f["category"]))
    return {
        "status": ("not_evaluated" if not han_count or genre != "prose"
                   else "review_suggested" if findings else "no_findings"),
        "genre": genre,
        "findings": findings,
        "metrics": metrics,
        "limitations": [
            "仅扫描未屏蔽区域的部分中文散文形状；不是作者身份、文笔或事实判定器。",
            "词面匹配会漏报和误报；真实对照、重复与修辞须结合材料和体裁判断。",
            "代码、常见引文、标题及链接目标被屏蔽；不是完整 Markdown/引文解析器。",
            "句长及连词统计只描述被扫描文本，无合格阈值，不构成改写配额。",
            "提示无需清零；未命中不证明语义保真或表达自然。",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", help="UTF-8 稿件路径；- 表示标准输入")
    parser.add_argument("--genre", choices=("prose", "fiction", "poetry", "dialogue", "technical"),
                        default="prose", help="仅 prose 启用形状提示，其他体裁只提供描述性统计")
    args = parser.parse_args()
    try:
        text = sys.stdin.read() if args.path == "-" else Path(args.path).read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        print(f"无法读取稿件：{error}", file=sys.stderr)
        return 2
    print(json.dumps(analyze(text, args.genre), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
