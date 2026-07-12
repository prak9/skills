#!/usr/bin/env python3
"""Lightweight structural validator for plan-skill outputs."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


PROGRAM_REQUIRED = [
    "Concept Refinement",
    "Problem Definition",
    "Context And References",
    "Key Context",
    "Code And Runtime Entrypoints",
    "External References And Evidence",
    "People And Decisions",
    "Preferences And Tradeoffs",
    "Preferences",
    "Tradeoffs",
    "Locked Constraints And Negotiable Space",
    "Goals And Metrics",
    "Acceptance Criteria",
    "Constraints",
    "Strategy",
    "Dependency And Slicing Strategy",
    "Decisions",
    "Exploration And Hypothesis Validation",
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
    "Risks And Mitigations",
    "Open Questions",
    "Current Status",
    "Update Protocol",
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
    "Output Artifacts",
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
    "Concept Refinement",
    "Problem Definition",
    "Acceptance Criteria",
    "Node Status",
    "Current Status",
]

TASK_REQUIRED_LITE = [
    "Task ",
    "Description",
    "Acceptance criteria",
    "Verification",
    "Output Artifacts",
    "Atomic Implementation Plan",
    "Standing Checklist",
    "Pre-completion Red Team",
    "Completion Writeback",
]

MEMORY_REQUIRED = [
    ("Important Findings", "重要发现"),
    ("Knowledge Base", "知识库沉淀"),
    ("Changelog", "变更记录"),
    ("Run Logs", "运行日志"),
    ("History Summaries", "历史执行记录总结"),
    ("Failures And Rework", "失败与回炉记录"),
    ("Open Knowledge Gaps", "开放知识缺口"),
    "Preference Learning",
    ("Reflection And Curation", "提炼与整理"),
    ("Update Rules", "更新规则"),
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
TASK_OUTPUT_ROOT = "tasks/output/"

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
    r"^#{1,6}\s*(?:History Summaries|历史执行记录总结)",
]


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise RuntimeError(f"File is not UTF-8: {path}") from exc


def has_required(text: str, item: str) -> bool:
    """Match item as a markdown heading or a bold field label, not arbitrary prose."""
    escaped = re.escape(item)
    pattern = rf"^(?:#{{1,6}}\s[^\n]*{escaped}|(?:[-*+]\s+)?\*\*{escaped})"
    return bool(re.search(pattern, text, flags=re.MULTILINE))


def check_required_items(path: Path, text: str, required: list, errors: list[str]) -> None:
    for item in required:
        options = (item,) if isinstance(item, str) else item
        if not any(has_required(text, option) for option in options):
            errors.append(f"{path} is missing required section or field: {' / '.join(options)}")


def detect_profile(text: str) -> str:
    match = re.search(r"^-\s*Profile[：:]\s*`?(Lite|Full)`?", text, flags=re.MULTILINE | re.IGNORECASE)
    return match.group(1).capitalize() if match else "Full"


def find_placeholders(path: Path, text: str, warnings: list[str]) -> None:
    placeholders = len(re.findall(r"<[^>\n]{1,120}>", text))
    if placeholders:
        warnings.append(f"{path} still contains {placeholders} template placeholders")


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
                    f"{path} row `{row_id}` is {'/'.join(sorted(statuses))} but evidence is empty or a placeholder"
                )
        if "完成" in statuses and unresolved.search(" ".join(cells)):
            errors.append(f"{path} row `{row_id}` is 完成 but still contains unresolved markers")


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
            f"{path} status is `{status}`, but Standing Checklist still has {len(unchecked)} unchecked items"
        )
    for line in re.findall(r"^\s*-\s+\[[xX]\]\s+(.+)$", section, flags=re.MULTILINE):
        if re.search(r"N/A\s*:\s*(?:$|<[^>\n]*>)", line, flags=re.IGNORECASE):
            errors.append(f"{path} Standing Checklist has an N/A item without a concrete reason: {line}")


def find_program_history_sections(path: Path, text: str, warnings: list[str]) -> None:
    for pattern in PROGRAM_HISTORY_PATTERNS:
        if re.search(pattern, text, flags=re.IGNORECASE | re.MULTILINE):
            warnings.append(f"{path} contains a history/log section that should move to memory.md: {pattern}")


def current_task_from_program(text: str) -> str | None:
    match = re.search(
        r"^-\s*(?:Active task package|当前任务包)[：:]\s*`?([^`\n]+)`?",
        text,
        flags=re.MULTILINE | re.IGNORECASE,
    )
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
        header_lookup = {cell.lower(): i for i, cell in enumerate(norm_header)}
        status_idx = header_lookup.get("status")
        task_idx = header_lookup.get("task package")
        if status_idx is None and "状态" in norm_header:
            status_idx = norm_header.index("状态")
        if task_idx is None and "任务包" in norm_header:
            task_idx = norm_header.index("任务包")
        if status_idx is None or task_idx is None:
            continue
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
        errors.append(f"Task package path escapes the project root: {link}")
        return None
    if not task_path.exists():
        errors.append(f"program.md references a missing task package: {link}")
        return None
    return task_path


def task_output_path(task_path: Path) -> str:
    return f"{TASK_OUTPUT_ROOT}{task_path.stem}/"


def tasks_output_ignored(root: Path) -> bool:
    gitignore = root / ".gitignore"
    if not gitignore.exists():
        return False
    for raw_line in read_text(gitignore).splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or line.startswith("!"):
            continue
        if line.endswith("/**"):
            line = line[:-3]
        if line.rstrip("/") in {"tasks/output", "/tasks/output", "**/tasks/output"}:
            return True
    return False


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate plan-skill program.md, tasks/TASK-*.md, output artifact pointers, links, and status records."
    )
    parser.add_argument("root", nargs="?", default=".", help="Project root, default: current directory")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    errors: list[str] = []
    warnings: list[str] = []

    program_path = root / "program.md"
    memory_path = root / "memory.md"
    if program_path.exists():
        program_text = read_text(program_path)
    else:
        errors.append(f"Missing file: {program_path}")
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
        errors.append(f"Missing file: {memory_path}")

    checked_paths: list[Path] = [program_path] if program_path.exists() else []
    if memory_path.exists():
        checked_paths.append(memory_path)

    if program_text:
        find_placeholders(program_path, program_text, warnings)
        check_completed_rows(program_path, program_text, errors)
        find_program_history_sections(program_path, program_text, warnings)
        if re.search(
            r"^-\s*(?:Plan mode|计划模式)[：:].*Loop",
            program_text,
            flags=re.MULTILINE | re.IGNORECASE,
        ) and not re.search(r"\bL-\d{3}\b", program_text):
            warnings.append("program.md is in Loop mode, but no loop iteration ID was found, e.g. L-001")
        if not status_values(program_text):
            warnings.append("program.md has no recognized status value")
        if not node_ids(program_text):
            warnings.append("program.md has no plan node ID, e.g. NODE-001")
        if not lite:
            if not size_values(program_text):
                warnings.append("program.md has no task-package size value, e.g. `S` or `M`")
            if not context_ref_ids(program_text):
                warnings.append("program.md has no context/reference ID, e.g. CTX-001/REF-001")
            if not preference_ref_ids(program_text):
                warnings.append("program.md has no preference ID, e.g. PREF-001")
    if memory_text:
        find_placeholders(memory_path, memory_text, warnings)
        if not re.search(r"\b(?:F|K|CHG|RUN|HIST|R|Q|PL)-\d{3}\b", memory_text):
            warnings.append("memory.md has no memory entry ID, e.g. F-001/K-001/CHG-001/RUN-001/HIST-001/PL-001")
        pending = len(re.findall(r"\|\s*`?待提炼`?\s*\|", memory_text))
        if pending >= 5:
            warnings.append(f"memory.md has {pending} run logs pending distillation; run Reflection & Curation")

    task_links = task_links_from_program(program_text) if program_text else []
    current_task = current_task_from_program(program_text) if program_text else None
    if current_task and current_task not in task_links:
        task_links.append(current_task)

    task_dir = root / "tasks"
    existing_tasks = sorted(task_dir.glob("TASK-*.md")) if task_dir.exists() else []
    if not task_links and existing_tasks:
        warnings.append("tasks/TASK-*.md files exist, but program.md does not reference task packages")
        task_entries = [(f"tasks/{path.name}", path) for path in existing_tasks]
    else:
        task_entries = [
            (link, task_path)
            for link in task_links
            if (task_path := check_task_link(root, link, errors)) is not None
        ]

    node_statuses = program_node_statuses(program_text) if program_text else {}
    if task_entries and not tasks_output_ignored(root):
        warnings.append("tasks/output/ is not ignored by .gitignore; add `/tasks/output/` or `tasks/output/`")

    for link, task_path in task_entries:
        checked_paths.append(task_path)
        task_text = read_text(task_path)
        check_required_items(
            task_path, task_text, TASK_REQUIRED_LITE if lite else TASK_REQUIRED, errors
        )
        find_placeholders(task_path, task_text, warnings)
        check_completed_rows(task_path, task_text, errors)
        check_standing_checklist_completion(task_path, task_text, errors)
        expected_output = task_output_path(task_path)
        if expected_output not in task_text:
            errors.append(
                f"{task_path} must point Output Artifacts to `{expected_output}`"
            )
        program_status = node_statuses.get(link)
        package_status = task_status(task_text)
        if program_status and package_status and program_status != package_status:
            errors.append(
                f"Status mismatch: program.md Node Status records {link} as `{program_status}`, "
                f"but task package Status is `{package_status}`"
            )
        if "N-001" not in task_text:
            warnings.append(f"{task_path} has no atomic node ID, e.g. N-001")
        is_loop = bool(re.search(r"^-\s*Plan mode[：:].*Loop", task_text, flags=re.MULTILINE))
        if is_loop and not re.search(r"\bL-\d{3}\b", task_text):
            warnings.append(f"{task_path} has no Loop iteration ID, e.g. L-001")
        if not node_ids(task_text):
            warnings.append(f"{task_path} has no related plan node ID, e.g. NODE-001")
        if not status_values(task_text):
            warnings.append(f"{task_path} has no recognized status value")
        if lite:
            continue
        if "V-001" not in task_text:
            warnings.append(f"{task_path} has no verification item ID, e.g. V-001")
        if "CP-001" not in task_text:
            warnings.append(f"{task_path} has no Checkpoint ID, e.g. CP-001")
        if (
            "Context/Refs" in task_text
            and not context_ref_ids(task_text)
            and not explicit_no_context_refs(task_text)
        ):
            warnings.append(f"{task_path} has no Context/Refs ID, e.g. CTX-001")
        if (
            "Preference refs" in task_text
            and not preference_ref_ids(task_text)
            and not explicit_no_preference_refs(task_text)
        ):
            warnings.append(f"{task_path} has no Preference refs ID, e.g. PREF-001")
        if "Memory writeback" not in task_text:
            warnings.append(f"{task_path} has no Memory writeback completion field")
        sizes = size_values(task_text)
        if not sizes:
            warnings.append(f"{task_path} has no estimated size, e.g. `S` or `M`")
        if any(size in {"L", "XL", "Large"} for size in sizes):
            warnings.append(f"{task_path} size is L/XL/Large; confirm whether it should be split")

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
            print("Plan structure, task links, and status records passed validation.")

    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
