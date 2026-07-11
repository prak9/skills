#!/usr/bin/env python3
"""Lightweight structural validator for plan-skill outputs."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


PROGRAM_REQUIRED = [
    "问题定义",
    "上下文与 References",
    "关键上下文",
    "代码与运行入口",
    "外部资料与证据",
    "人与决策上下文",
    "目标与度量",
    "验收标准",
    "约束",
    "总体策略",
    "依赖与切片策略",
    "决策记录",
    "探索与假设验证",
    "Implementation Plan",
    "Overview",
    "Architecture Decisions",
    "Plan Dependency Graph",
    "Node Status",
    "Loop Contract",
    "Loop State",
    "Memory Sync",
    "Task List",
    "Checkpoints",
    "Parallelization Opportunities",
    "Risks and Mitigations",
    "Open Questions",
    "当前状态",
    "更新协议",
]

TASK_REQUIRED = [
    "Task ",
    "Description",
    "Acceptance criteria",
    "Verification",
    "Dependencies",
    "Context/Refs",
    "Files likely touched",
    "Estimated scope",
    "Atomic Implementation Plan",
    "Verification Matrix",
    "Checkpoint",
    "Loop Iteration Log",
    "Execution Log",
    "Escalation",
    "Risks and Rollback",
    "Completion Writeback",
]

MEMORY_REQUIRED = [
    "重要发现",
    "知识库沉淀",
    "历史执行记录总结",
    "失败与回炉记录",
    "开放知识缺口",
    "更新规则",
]

VALID_STATUSES = {
    "待开始",
    "探索中",
    "进行中",
    "阻塞",
    "待验证",
    "待验收",
    "完成",
    "已取消",
}

VALID_SIZES = {"XS", "S", "M", "L", "XL", "Small", "Medium", "Large"}

LOOP_STEPS = {"Goal", "Plan", "Act", "Verify", "Reflect", "Iterate", "Pass", "Blocked"}

UNRESOLVED_PATTERNS = [
    r"\[待确认\]",
    r"\[待验证\]",
    r"\[待决策\]",
    r"\bTBD\b",
    r"\bTODO\b(?!\.md\b)",
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
    match = re.search(r"^-\s*当前任务包[：:]\s*`?([^`\n]+)`?", text, flags=re.MULTILINE)
    if not match:
        return None
    value = match.group(1).strip()
    if value in {"无", "none", "None"} or value.startswith("<"):
        return None
    return value.split()[0].strip()


def task_links_from_program(text: str) -> list[str]:
    links = re.findall(r"`?(tasks/TASK-\d{3}[-A-Za-z0-9_]*\.md)`?", text)
    return sorted(set(links))


def node_ids(text: str) -> list[str]:
    return sorted(set(re.findall(r"\bNODE-\d{3}\b", text)))


def context_ref_ids(text: str) -> list[str]:
    return sorted(set(re.findall(r"\b(?:CTX|REF|REF-EXT|OWN)-\d{3}\b", text)))


def explicit_no_context_refs(text: str) -> bool:
    return bool(re.search(r"Context/(?:Refs|refs)[^\n]*(?:None|无)", text))


def status_values(text: str) -> list[str]:
    values = re.findall(r"`([^`]+)`", text)
    return [value for value in values if value in VALID_STATUSES]


def size_values(text: str) -> list[str]:
    values = set(re.findall(r"`([^`]+)`", text))
    for cell in re.findall(r"(?<=\|)([^|\n]+)(?=\|)", text):
        values.add(cell.strip().strip("`"))
    values.update(re.findall(r"\b(?:Small|Medium|Large)\b", text))
    return sorted(value for value in values if value in VALID_SIZES)


def loop_steps(text: str) -> list[str]:
    return sorted(set(re.findall(r"\b(?:Goal|Plan|Act|Verify|Reflect|Iterate|Pass|Blocked)\b", text)))


def check_task_link(root: Path, link: str, errors: list[str]) -> Path | None:
    task_path = (root / link).resolve()
    try:
        task_path.relative_to(root)
    except ValueError:
        errors.append(f"任务包路径越出项目根目录：{link}")
        return None
    if not task_path.exists():
        errors.append(f"program.md 引用了不存在的任务包：{link}")
        return None
    return task_path


def main() -> int:
    parser = argparse.ArgumentParser(
        description="检查 program.md 和 tasks/TASK-*.md 的计划结构、任务链接和状态记录。"
    )
    parser.add_argument("root", nargs="?", default=".", help="项目根目录，默认当前目录")
    parser.add_argument("--json", action="store_true", help="以 JSON 输出结果")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    errors: list[str] = []
    warnings: list[str] = []

    program_path = root / "program.md"
    memory_path = root / "memory.md"
    program_text = check_required(program_path, PROGRAM_REQUIRED, errors)
    memory_text = check_required(memory_path, MEMORY_REQUIRED, errors)
    checked_paths: list[Path] = [program_path] if program_path.exists() else []
    if memory_path.exists():
        checked_paths.append(memory_path)

    if program_text:
        find_unresolved(program_path, program_text, warnings)
        if "Node Status" not in program_text:
            warnings.append("program.md 应维护 Node Status 表")
        if "Plan Dependency Graph" not in program_text:
            warnings.append("program.md 应维护计划依赖图")
        if "Loop Contract" in program_text and "Loop State" in program_text and not loop_steps(program_text):
            warnings.append("program.md 未发现 Loop 步骤，例如 Plan/Act/Verify/Reflect/Iterate")
        if not status_values(program_text):
            warnings.append("program.md 未发现规范状态值")
        if not size_values(program_text):
            warnings.append("program.md 未发现任务包规模值，例如 `S` 或 `M`")
        if not node_ids(program_text):
            warnings.append("program.md 未发现计划节点 ID，例如 NODE-001")
        if not context_ref_ids(program_text):
            warnings.append("program.md 未发现上下文或引用 ID，例如 CTX-001/REF-001")
    if memory_text:
        find_unresolved(memory_path, memory_text, warnings)
        if not re.search(r"\b(?:F|K|H|R|Q)-\d{3}\b", memory_text):
            warnings.append("memory.md 未发现记忆条目编号，例如 F-001/K-001/H-001")

    task_links = task_links_from_program(program_text) if program_text else []
    current_task = current_task_from_program(program_text) if program_text else None
    if current_task and current_task not in task_links:
        task_links.append(current_task)

    task_dir = root / "tasks"
    existing_tasks = sorted(task_dir.glob("TASK-*.md")) if task_dir.exists() else []
    if not task_links and existing_tasks:
        warnings.append("存在 tasks/TASK-*.md，但 program.md 未在执行计划中引用任务包")
        task_paths = existing_tasks
    else:
        task_paths = [
            task_path
            for link in task_links
            if (task_path := check_task_link(root, link, errors)) is not None
        ]

    for task_path in task_paths:
        checked_paths.append(task_path)
        task_text = check_required(task_path, TASK_REQUIRED, errors)
        if not task_text:
            continue
        find_unresolved(task_path, task_text, warnings)
        if "N-001" not in task_text:
            warnings.append(f"{task_path} 未发现原子节点编号，例如 N-001")
        if "V-001" not in task_text:
            warnings.append(f"{task_path} 未发现验证项编号，例如 V-001")
        if "CP-001" not in task_text:
            warnings.append(f"{task_path} 未发现 Checkpoint 编号，例如 CP-001")
        if "Loop Iteration Log" in task_text and not re.search(r"\bL-\d{3}\b", task_text):
            warnings.append(f"{task_path} 未发现 Loop 轮次编号，例如 L-001")
        if not node_ids(task_text):
            warnings.append(f"{task_path} 未发现对应计划节点 ID，例如 NODE-001")
        if (
            "Context/Refs" in task_text
            and not context_ref_ids(task_text)
            and not explicit_no_context_refs(task_text)
        ):
            warnings.append(f"{task_path} 未发现 Context/Refs ID，例如 CTX-001")
        if "Memory writeback" not in task_text:
            warnings.append(f"{task_path} 未发现 Memory writeback 完成回写字段")
        if not status_values(task_text):
            warnings.append(f"{task_path} 未发现规范状态值")
        sizes = size_values(task_text)
        if not sizes:
            warnings.append(f"{task_path} 未发现预计规模，例如 `S` 或 `M`")
        if any(size in {"L", "XL", "Large"} for size in sizes):
            warnings.append(f"{task_path} 规模为 L/XL/Large，应确认是否继续拆分")

    result = {
        "root": str(root),
        "ok": not errors,
        "errors": errors,
        "warnings": warnings,
        "checked": [str(path) for path in checked_paths],
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
            print("计划结构、任务链接和状态记录检查通过。")

    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
