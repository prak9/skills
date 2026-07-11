#!/usr/bin/env python3
"""Lightweight structural validator for project-control-docs outputs."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


PROGRAM_REQUIRED = [
    "业务结果",
    "成功指标",
    "非目标",
    "关键假设",
    "硬约束",
    "不可接受的失败",
    "AI 可以自主决定",
    "必须先征询",
    "验收证据",
    "迁移与回滚",
    "关键决策",
]

CODEMAP_REQUIRED = [
    "系统入口",
    "核心模块",
    "数据与状态",
    "测试与 Harness",
    "高风险区域",
]

TASK_REQUIRED = [
    "目标",
    "范围",
    "验收标准与证据",
    "AI 自主空间",
    "Checkpoint",
    "证据记录",
    "风险与回滚",
    "完成记录",
]

UNRESOLVED_PATTERNS = [
    r"\[待确认\]",
    r"\[待验证\]",
    r"\[待决策\]",
    r"\bTBD\b",
    r"\bUNVERIFIED\b",
    r"\bDECISION REQUIRED\b",
]


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise RuntimeError(f"文件不是 UTF-8：{path}") from exc


def check_required(path: Path, required: list[str], errors: list[str]) -> str:
    if not path.exists():
        errors.append(f"缺少文件：{path}")
        return ""
    text = read_text(path)
    for item in required:
        if item not in text:
            errors.append(f"{path} 缺少必要章节或字段：{item}")
    return text


def find_unresolved(path: Path, text: str, warnings: list[str]) -> None:
    for pattern in UNRESOLVED_PATTERNS:
        count = len(re.findall(pattern, text, flags=re.IGNORECASE))
        if count:
            warnings.append(f"{path} 含 {count} 个未决标记：{pattern}")

    placeholders = len(re.findall(r"<[^>\n]{1,120}>", text))
    if placeholders:
        warnings.append(f"{path} 仍含 {placeholders} 个模板占位符")


def current_task_from_program(text: str) -> str | None:
    match = re.search(r"^-\s*当前任务[：:]\s*`?([^`\n]+)`?", text, flags=re.MULTILINE)
    if not match:
        return None
    value = match.group(1).strip()
    if value in {"无", "none", "None"} or value.startswith("<"):
        return None
    return value.split()[0].strip()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="检查 program.md、codemap.md 和当前任务包的基本结构与交叉引用。"
    )
    parser.add_argument("root", nargs="?", default=".", help="项目根目录，默认当前目录")
    parser.add_argument("--json", action="store_true", help="以 JSON 输出结果")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    errors: list[str] = []
    warnings: list[str] = []

    program_path = root / "program.md"
    codemap_path = root / "codemap.md"
    program_text = check_required(program_path, PROGRAM_REQUIRED, errors)
    codemap_text = check_required(codemap_path, CODEMAP_REQUIRED, errors)

    if program_text:
        find_unresolved(program_path, program_text, warnings)
    if codemap_text:
        find_unresolved(codemap_path, codemap_text, warnings)

    task_value = current_task_from_program(program_text) if program_text else None
    task_path: Path | None = None
    if task_value:
        task_path = (root / task_value).resolve()
        try:
            task_path.relative_to(root)
        except ValueError:
            errors.append(f"当前任务路径越出项目根目录：{task_value}")
            task_path = None

    if task_path:
        task_text = check_required(task_path, TASK_REQUIRED, errors)
        if task_text:
            find_unresolved(task_path, task_text, warnings)
    else:
        task_dir = root / "tasks"
        if task_dir.exists() and not any(task_dir.glob("TASK-*.md")):
            warnings.append(f"{task_dir} 存在，但没有 TASK-*.md")

    if program_text and "program.md >" not in program_text:
        warnings.append("program.md 未明确意图冲突优先级")
    if codemap_text and not re.search(r"对应版本[：:].*(commit|tag|尚无实现)", codemap_text, re.I):
        warnings.append("codemap.md 未清楚记录对应版本/commit/tag")

    result = {
        "root": str(root),
        "ok": not errors,
        "errors": errors,
        "warnings": warnings,
        "checked": [
            str(path)
            for path in (program_path, codemap_path, task_path)
            if path is not None and path.exists()
        ],
    }

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print("PASS" if result["ok"] else "FAIL")
        for item in errors:
            print(f"ERROR: {item}")
        for item in warnings:
            print(f"WARN: {item}")
        if not errors and not warnings:
            print("文档结构和交叉引用检查通过。")

    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
