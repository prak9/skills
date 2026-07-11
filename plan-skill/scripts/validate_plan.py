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
    "Preferences & Tradeoffs",
    "Preferences",
    "Tradeoffs",
    "Locked Constraints",
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
    "Preference refs",
    "Locked constraints",
    "Negotiable space",
    "Files likely touched",
    "Estimated scope",
    "Atomic Implementation Plan",
    "Verification Matrix",
    "Checkpoint",
    "Current Loop Attempt",
    "Latest Execution Snapshot",
    "Escalation",
    "Risks and Rollback",
    "Standing Checklist",
    "Pre-completion Red Team",
    "Completion Writeback",
]

# Lite profile: for work of one or two focused sessions. Declared via `- Profile: Lite`
# in the program.md header; default is Full. Semantic checks apply to both profiles.
PROGRAM_REQUIRED_LITE = [
    "问题定义",
    "验收标准",
    "Node Status",
    "当前状态",
]

TASK_REQUIRED_LITE = [
    "Task ",
    "Description",
    "Acceptance criteria",
    "Verification",
    "Atomic Implementation Plan",
    "Standing Checklist",
    "Pre-completion Red Team",
    "Completion Writeback",
]

MEMORY_REQUIRED = [
    "重要发现",
    "知识库沉淀",
    "变更记录",
    "运行日志",
    "历史执行记录总结",
    "失败与回炉记录",
    "开放知识缺口",
    "Preference Learning",
    "提炼与整理",
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

UNRESOLVED_PATTERNS = [
    r"\[待确认\]",
    r"\[待验证\]",
    r"\[待决策\]",
    r"\bTBD\b",
    r"\bTODO\b(?!\.md\b)",
    r"\bUNVERIFIED\b",
    r"\bDECISION REQUIRED\b",
]

PROGRAM_HISTORY_PATTERNS = [
    r"^#{1,6}\s*(?:CHANGELOG|Changelog|变更记录)",
    r"^#{1,6}\s*(?:Run Log|运行日志|Execution Log)",
    r"^#{1,6}\s*历史执行记录总结",
]


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise RuntimeError(f"文件不是 UTF-8：{path}") from exc


def has_required(text: str, item: str) -> bool:
    """Match item as a markdown heading or a bold field label, not arbitrary prose."""
    escaped = re.escape(item)
    pattern = rf"^(?:#{{1,6}}\s[^\n]*{escaped}|(?:[-*+]\s+)?\*\*{escaped})"
    return bool(re.search(pattern, text, flags=re.MULTILINE))


def check_required_items(path: Path, text: str, required: list[str], errors: list[str]) -> None:
    for item in required:
        if not has_required(text, item):
            errors.append(f"{path} 缺少必要章节或字段：{item}")


def detect_profile(text: str) -> str:
    match = re.search(r"^-\s*Profile[：:]\s*`?(Lite|Full)`?", text, flags=re.MULTILINE | re.IGNORECASE)
    return match.group(1).capitalize() if match else "Full"


def find_placeholders(path: Path, text: str, warnings: list[str]) -> None:
    placeholders = len(re.findall(r"<[^>\n]{1,120}>", text))
    if placeholders:
        warnings.append(f"{path} 仍含 {placeholders} 个模板占位符")


def iter_table_rows(text: str):
    """Yield (header_cells, row_cells) for each data row of each markdown table."""
    header: list[str] | None = None
    for line in text.splitlines():
        stripped = line.strip()
        if not (stripped.startswith("|") and stripped.endswith("|") and len(stripped) > 2):
            header = None
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if all(re.fullmatch(r":?-+:?", cell) for cell in cells):
            continue
        if header is None:
            header = cells
        else:
            yield header, cells


def norm_cell(cell: str) -> str:
    return cell.strip("`").strip()


EVIDENCE_EMPTY = {"", "无", "None", "-", "不适用", "N/A", "待运行", "待补充", "待填"}


def check_completed_rows(path: Path, text: str, errors: list[str]) -> None:
    """完成/待验收 rows must carry real evidence; 完成 rows must not carry unresolved markers."""
    unresolved = re.compile("|".join(UNRESOLVED_PATTERNS), flags=re.IGNORECASE)
    for header, cells in iter_table_rows(text):
        statuses = {norm_cell(cell) for cell in cells} & {"完成", "待验收"}
        if not statuses:
            continue
        row_id = norm_cell(cells[0]) if cells else "?"
        norm_header = [norm_cell(cell) for cell in header]
        ev_idx = next(
            (i for i, h in enumerate(norm_header) if "证据" in h or "evidence" in h.lower()),
            None,
        )
        if ev_idx is not None and ev_idx < len(cells):
            evidence = norm_cell(cells[ev_idx])
            if evidence in EVIDENCE_EMPTY or re.fullmatch(r"<[^>\n]*>", evidence):
                errors.append(
                    f"{path} 行 `{row_id}` 状态为 {'/'.join(sorted(statuses))} 但证据为空或占位符"
                )
        if "完成" in statuses and unresolved.search(" ".join(cells)):
            errors.append(f"{path} 行 `{row_id}` 状态为 完成 但仍含未决标记")


def markdown_h2_section(text: str, title: str) -> str | None:
    pattern = rf"^##\s+{re.escape(title)}\b(?P<body>.*?)(?=^##\s+|\Z)"
    match = re.search(pattern, text, flags=re.MULTILINE | re.DOTALL)
    return match.group("body") if match else None


def check_standing_checklist_completion(path: Path, text: str, errors: list[str]) -> None:
    """待验收/完成 task packages must have no unchecked Standing Checklist items."""
    status = task_status(text)
    if status not in {"待验收", "完成"}:
        return
    section = markdown_h2_section(text, "Standing Checklist")
    if section is None:
        return
    unchecked = re.findall(r"^\s*-\s+\[\s\]\s+(.+)$", section, flags=re.MULTILINE)
    if unchecked:
        errors.append(
            f"{path} 状态为 `{status}`，但 Standing Checklist 仍有 {len(unchecked)} 个未勾选项"
        )
    for line in re.findall(r"^\s*-\s+\[[xX]\]\s+(.+)$", section, flags=re.MULTILINE):
        if re.search(r"N/A\s*:\s*(?:$|<[^>\n]*>)", line, flags=re.IGNORECASE):
            errors.append(f"{path} Standing Checklist 中 N/A 项缺少具体原因：{line}")


def find_program_history_sections(path: Path, text: str, warnings: list[str]) -> None:
    for pattern in PROGRAM_HISTORY_PATTERNS:
        if re.search(pattern, text, flags=re.IGNORECASE | re.MULTILINE):
            warnings.append(f"{path} 含历史记录章节，应迁移到 memory.md：{pattern}")


def current_task_from_program(text: str) -> str | None:
    match = re.search(r"^-\s*当前任务包[：:]\s*`?([^`\n]+)`?", text, flags=re.MULTILINE)
    if not match:
        return None
    value = match.group(1).strip()
    if value in {"无", "none", "None"} or value.startswith("<"):
        return None
    return value.split()[0].strip()


def program_node_statuses(text: str) -> dict[str, str]:
    """Map task-package link -> node status from the program.md Node Status table."""
    result: dict[str, str] = {}
    for header, cells in iter_table_rows(text):
        norm_header = [norm_cell(cell) for cell in header]
        if "状态" not in norm_header or "任务包" not in norm_header:
            continue
        status_idx = norm_header.index("状态")
        task_idx = norm_header.index("任务包")
        if max(status_idx, task_idx) >= len(cells):
            continue
        status = norm_cell(cells[status_idx])
        link = re.search(r"tasks/TASK-\d{3}[-A-Za-z0-9_]*\.md", cells[task_idx])
        if status in VALID_STATUSES and link:
            result[link.group(0)] = status
    return result


def task_status(text: str) -> str | None:
    match = re.search(r"^-\s*Status[：:]\s*`?([^`\n]+)`?", text, flags=re.MULTILINE)
    if not match:
        return None
    value = match.group(1).strip()
    return value if value in VALID_STATUSES else None


def task_links_from_program(text: str) -> list[str]:
    links = re.findall(r"`?(tasks/TASK-\d{3}[-A-Za-z0-9_]*\.md)`?", text)
    return sorted(set(links))


def node_ids(text: str) -> list[str]:
    return sorted(set(re.findall(r"\bNODE-\d{3}\b", text)))


def context_ref_ids(text: str) -> list[str]:
    return sorted(set(re.findall(r"\b(?:CTX|REF|REF-EXT|OWN)-\d{3}\b", text)))


def preference_ref_ids(text: str) -> list[str]:
    return sorted(set(re.findall(r"\bPREF-\d{3}\b", text)))


def explicit_no_context_refs(text: str) -> bool:
    return bool(re.search(r"Context/(?:Refs|refs)[^\n]*(?:None|无)", text))


def explicit_no_preference_refs(text: str) -> bool:
    return bool(re.search(r"Preference refs[^\n]*(?:None|无)", text, flags=re.IGNORECASE))


def status_values(text: str) -> list[str]:
    values = re.findall(r"`([^`]+)`", text)
    return [value for value in values if value in VALID_STATUSES]


def size_values(text: str) -> list[str]:
    values = set(re.findall(r"`([^`]+)`", text))
    for cell in re.findall(r"(?<=\|)([^|\n]+)(?=\|)", text):
        values.add(cell.strip().strip("`"))
    values.update(re.findall(r"\b(?:Small|Medium|Large)\b", text))
    return sorted(value for value in values if value in VALID_SIZES)


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
    if program_path.exists():
        program_text = read_text(program_path)
    else:
        errors.append(f"缺少文件：{program_path}")
        program_text = ""
    profile = detect_profile(program_text)
    lite = profile == "Lite"
    if program_text:
        check_required_items(
            program_path, program_text, PROGRAM_REQUIRED_LITE if lite else PROGRAM_REQUIRED, errors
        )

    memory_text = ""
    if memory_path.exists():
        memory_text = read_text(memory_path)
        if not lite:
            check_required_items(memory_path, memory_text, MEMORY_REQUIRED, errors)
    elif not lite:
        errors.append(f"缺少文件：{memory_path}")

    checked_paths: list[Path] = [program_path] if program_path.exists() else []
    if memory_path.exists():
        checked_paths.append(memory_path)

    if program_text:
        find_placeholders(program_path, program_text, warnings)
        check_completed_rows(program_path, program_text, errors)
        find_program_history_sections(program_path, program_text, warnings)
        if re.search(r"^-\s*计划模式[：:].*Loop", program_text, flags=re.MULTILINE) and not re.search(
            r"\bL-\d{3}\b", program_text
        ):
            warnings.append("program.md 计划模式为 Loop，但未发现 Loop 轮次编号，例如 L-001")
        if not status_values(program_text):
            warnings.append("program.md 未发现规范状态值")
        if not node_ids(program_text):
            warnings.append("program.md 未发现计划节点 ID，例如 NODE-001")
        if not lite:
            if not size_values(program_text):
                warnings.append("program.md 未发现任务包规模值，例如 `S` 或 `M`")
            if not context_ref_ids(program_text):
                warnings.append("program.md 未发现上下文或引用 ID，例如 CTX-001/REF-001")
            if not preference_ref_ids(program_text):
                warnings.append("program.md 未发现偏好 ID，例如 PREF-001")
    if memory_text:
        find_placeholders(memory_path, memory_text, warnings)
        if not re.search(r"\b(?:F|K|CHG|RUN|HIST|R|Q|PL)-\d{3}\b", memory_text):
            warnings.append("memory.md 未发现记忆条目编号，例如 F-001/K-001/CHG-001/RUN-001/HIST-001/PL-001")
        pending = len(re.findall(r"\|\s*`?待提炼`?\s*\|", memory_text))
        if pending >= 5:
            warnings.append(f"memory.md 有 {pending} 条运行日志待提炼，应执行提炼与整理（Reflection & Curation）")

    task_links = task_links_from_program(program_text) if program_text else []
    current_task = current_task_from_program(program_text) if program_text else None
    if current_task and current_task not in task_links:
        task_links.append(current_task)

    task_dir = root / "tasks"
    existing_tasks = sorted(task_dir.glob("TASK-*.md")) if task_dir.exists() else []
    if not task_links and existing_tasks:
        warnings.append("存在 tasks/TASK-*.md，但 program.md 未在执行计划中引用任务包")
        task_entries = [(f"tasks/{path.name}", path) for path in existing_tasks]
    else:
        task_entries = [
            (link, task_path)
            for link in task_links
            if (task_path := check_task_link(root, link, errors)) is not None
        ]

    node_statuses = program_node_statuses(program_text) if program_text else {}

    for link, task_path in task_entries:
        checked_paths.append(task_path)
        task_text = read_text(task_path)
        check_required_items(
            task_path, task_text, TASK_REQUIRED_LITE if lite else TASK_REQUIRED, errors
        )
        find_placeholders(task_path, task_text, warnings)
        check_completed_rows(task_path, task_text, errors)
        check_standing_checklist_completion(task_path, task_text, errors)
        program_status = node_statuses.get(link)
        package_status = task_status(task_text)
        if program_status and package_status and program_status != package_status:
            errors.append(
                f"状态不一致：program.md Node Status 记录 {link} 为 `{program_status}`，"
                f"任务包 Status 为 `{package_status}`"
            )
        if "N-001" not in task_text:
            warnings.append(f"{task_path} 未发现原子节点编号，例如 N-001")
        is_loop = bool(re.search(r"^-\s*Plan mode[：:].*Loop", task_text, flags=re.MULTILINE))
        if is_loop and not re.search(r"\bL-\d{3}\b", task_text):
            warnings.append(f"{task_path} 未发现 Loop 轮次编号，例如 L-001")
        if not node_ids(task_text):
            warnings.append(f"{task_path} 未发现对应计划节点 ID，例如 NODE-001")
        if not status_values(task_text):
            warnings.append(f"{task_path} 未发现规范状态值")
        if lite:
            continue
        if "V-001" not in task_text:
            warnings.append(f"{task_path} 未发现验证项编号，例如 V-001")
        if "CP-001" not in task_text:
            warnings.append(f"{task_path} 未发现 Checkpoint 编号，例如 CP-001")
        if (
            "Context/Refs" in task_text
            and not context_ref_ids(task_text)
            and not explicit_no_context_refs(task_text)
        ):
            warnings.append(f"{task_path} 未发现 Context/Refs ID，例如 CTX-001")
        if (
            "Preference refs" in task_text
            and not preference_ref_ids(task_text)
            and not explicit_no_preference_refs(task_text)
        ):
            warnings.append(f"{task_path} 未发现 Preference refs ID，例如 PREF-001")
        if "Memory writeback" not in task_text:
            warnings.append(f"{task_path} 未发现 Memory writeback 完成回写字段")
        sizes = size_values(task_text)
        if not sizes:
            warnings.append(f"{task_path} 未发现预计规模，例如 `S` 或 `M`")
        if any(size in {"L", "XL", "Large"} for size in sizes):
            warnings.append(f"{task_path} 规模为 L/XL/Large，应确认是否继续拆分")

    result = {
        "root": str(root),
        "profile": profile,
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
