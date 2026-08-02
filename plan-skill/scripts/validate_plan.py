#!/usr/bin/env python3
"""Lightweight structural validator for plan-skill outputs."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

from plan_markdown import (
    bold_field_section,
    bullet_field,
    check_required_items,
    check_table_shapes,
    checklist_items,
    checklist_unchecked,
    find_placeholders,
    iter_table_rows,
    markdown_h2_section,
    markdown_heading_section,
    metadata_value,
    norm_cell,
    read_text,
    read_text_for_validation,
    section_status_rows,
    table_as_mapping,
)


PROGRAM_REQUIRED = [
    "Concept Refinement",
    "Execution Readiness Gate",
    "Problem Definition",
    "Context And References",
    "Preferences And Tradeoffs",
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
    "Current Status",
    "Update Protocol",
]

PROGRAM_REQUIRED_LEAN_FULL = [
    "Outcome",
    "Execution Readiness Gate",
    "Context",
    "Constraints And Decisions",
    "Acceptance",
    "Node Index",
    "Loop Contract",
    "Loop State",
    "Checkpoints",
    "Current Status",
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

PROGRAM_REQUIRED_LITE = [
    "Outcome",
    "Constraints",
    "Acceptance",
    "Plan",
]

PROGRAM_REQUIRED_LEGACY_LITE = [
    "Concept Refinement",
    "Execution Readiness Gate",
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

TASK_REQUIRED_LEAN = [
    "Task",
    "Description",
    "Acceptance criteria",
    "Verification",
    "Dependencies",
    "Locked constraints",
    "Negotiable space",
    "Files likely touched",
    "Atomic Plan",
    "Risks And Escalation",
    "Completion Review",
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

MEMORY_REQUIRED_LEAN = [
    "Decisions",
    "Findings",
    "Runs",
    "Update Rules",
]

MEMORY_REQUIRED_COMPACT = [
    "Durable State",
    ("Changelog", "变更记录"),
    ("Run Logs", "运行日志"),
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
VALID_PLAN_MODES = {"Linear", "Loop"}
VALID_PROGRAM_STATUSES = VALID_STATUSES
VALID_TASK_STATUSES = VALID_STATUSES - {"探索中"}
VALID_ABSTRACTION_IMPACTS = {"none", "reuse", "new", "modify", "remove"}
STRUCTURAL_ABSTRACTION_IMPACTS = {"new", "modify", "remove"}
VALID_EXECUTION_READINESS = {"Blocked", "Ready", "Not required"}
VALID_CLEAN_STATES = {"Not due", "Due"}
EXECUTION_READINESS_GATE_FIELDS = (
    "Decision this work informs",
    "Claim / hypothesis",
    "Baseline / counterfactual",
    "Evidence / data quality",
    "Real constraints",
    "Pass condition",
    "Falsifier / stop condition",
    "Cheapest informative check",
    "False-positive loop",
    "Human judgment retained",
)
LEAN_EXECUTION_READINESS_GATE_FIELDS = (
    "Decision this work informs",
    "Key uncertainty / hypothesis",
    "Pass / fail evidence",
    "Cheapest informative check",
)
ABSTRACTION_GATE_FIELDS = (
    "Concrete pressure / current consumers",
    "Existing pattern / direct alternative",
    "Boundary / owned invariant",
    "Explicit non-responsibilities",
    "Expected variation",
    "Concept count / indirection",
    "Coupling / interface impact",
    "Contract verification",
    "Rollback / deletion trigger",
)
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


def detect_profile(text: str, path: Path | None = None, errors: list[str] | None = None) -> str:
    value = metadata_value(text, "Profile")
    if value is None:
        return "Full"
    normalized = value.capitalize()
    if normalized in {"Lite", "Full"}:
        return normalized
    if errors is not None:
        errors.append(
            f"{path or 'program.md'} Profile must be exactly `Lite` or `Full`, got `{value}`"
        )
    return "Full"


def parse_enum_metadata(
    path: Path,
    text: str,
    labels: tuple[str, ...],
    valid: set[str],
    display_name: str,
    errors: list[str],
) -> str | None:
    value = metadata_value(text, *labels)
    if value is None:
        errors.append(f"{path} is missing top-level field: {display_name}")
        return None
    if value not in valid:
        choices = " / ".join(sorted(valid))
        errors.append(f"{path} {display_name} must be exactly one of `{choices}`, got `{value}`")
        return None
    return value


EVIDENCE_EMPTY = {
    "",
    "无",
    "None",
    "-",
    "不适用",
    "N/A",
    "pending",
    "not produced",
    "not applicable",
    "Not run",
    "待运行",
    "待补充",
    "待填",
}
EVIDENCE_EMPTY_LOWER = {value.lower() for value in EVIDENCE_EMPTY}


def check_completed_rows(path: Path, text: str, errors: list[str]) -> None:
    """Require evidence for terminal rows and reject unresolved completed rows."""
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
        evidence_required = bool(re.fullmatch(r"(?:NODE|EXP|N|V)-\d{3}", row_id))
        if ev_idx is not None and ev_idx < len(cells):
            evidence = norm_cell(cells[ev_idx])
            if evidence.lower() in EVIDENCE_EMPTY_LOWER or re.fullmatch(
                r"<[^>\n]*>", evidence
            ):
                errors.append(
                    f"{path} row `{row_id}` is {'/'.join(sorted(statuses))} "
                    "but evidence is empty or a placeholder"
                )
        elif evidence_required:
            errors.append(
                f"{path} row `{row_id}` is {'/'.join(sorted(statuses))} "
                "but its table has no evidence column"
            )
        if "完成" in statuses and unresolved.search(" ".join(cells)):
            errors.append(f"{path} row `{row_id}` is 完成 but still contains unresolved markers")


PENDING_VALUE = re.compile(
    r"(?:<[^>\n]+>|\b(?:TBD|TODO|UNVERIFIED)\b|"
    r"^(?:pending|not produced|not applicable)\b|"
    r"待.{0,24}(?:作答|完成|填写|补充|运行|确认|验证|验收|刷新)|完成时)",
    flags=re.IGNORECASE,
)


def is_concrete(value: str | None) -> bool:
    if value is None:
        return False
    normalized = norm_cell(value).strip()
    if normalized.lower() in EVIDENCE_EMPTY_LOWER:
        return False
    return not PENDING_VALUE.search(normalized)


REFLECTION_SECTION_TITLES = ("Reflection Log", "Reflections", "Node Reflections")
REFLECTION_FIELDS = {
    "scope": "Scope",
    "evidence": "Evidence",
    "wrong / changed": "Wrong / changed",
    "right / preserve": "Right / preserve",
    "next rule": "Next rule",
}


def has_reflection_ledger(text: str) -> bool:
    return any(
        markdown_heading_section(text, title) is not None
        for title in REFLECTION_SECTION_TITLES
    )


def reflection_records(
    path: Path,
    text: str,
    errors: list[str],
) -> dict[str, dict[str, str]]:
    records: dict[str, dict[str, str]] = {}
    for title in REFLECTION_SECTION_TITLES:
        section = markdown_heading_section(text, title)
        if section is None:
            continue
        for header, cells in iter_table_rows(section):
            normalized = [norm_cell(cell).lower() for cell in header]
            lookup = {name: index for index, name in enumerate(normalized)}
            required = {"id", *REFLECTION_FIELDS}
            if not required.issubset(lookup):
                continue
            if max(lookup[field] for field in required) >= len(cells):
                continue
            reflection_id = norm_cell(cells[lookup["id"]])
            if not re.fullmatch(r"R-\d{3}", reflection_id):
                continue
            if reflection_id in records:
                errors.append(f"{path} has duplicate reflection ID `{reflection_id}`")
                continue
            record = {
                field: norm_cell(cells[lookup[field]])
                for field in REFLECTION_FIELDS
            }
            records[reflection_id] = record
            missing = [
                label
                for field, label in REFLECTION_FIELDS.items()
                if not is_concrete(record[field])
            ]
            if missing:
                errors.append(
                    f"{path} reflection `{reflection_id}` is incomplete: "
                    + ", ".join(missing)
                )
    return records


def completed_nodes(section: str | None, id_pattern: str) -> list[str]:
    return [
        row_id
        for row_id, status in section_status_rows(section)
        if re.fullmatch(id_pattern, row_id) and status == "完成"
    ]


def check_node_reflections(
    path: Path,
    text: str,
    section_title: str,
    id_pattern: str,
    records: dict[str, dict[str, str]],
    errors: list[str],
    related_plan_node: str | None = None,
) -> None:
    section = markdown_heading_section(text, section_title)
    if section is None:
        return
    node_ids_in_section = [
        row_id
        for row_id, _ in section_status_rows(section)
        if re.fullmatch(id_pattern, row_id)
    ]
    allow_plan_node_scope = len(node_ids_in_section) == 1
    used_reflections: dict[str, str] = {}
    for header, cells in iter_table_rows(section):
        normalized = [norm_cell(cell).lower() for cell in header]
        lookup = {name: index for index, name in enumerate(normalized)}
        node_idx = lookup.get("node")
        status_idx = lookup.get("status")
        if node_idx is None or status_idx is None:
            continue
        if max(node_idx, status_idx) >= len(cells):
            continue
        node = norm_cell(cells[node_idx])
        status = norm_cell(cells[status_idx])
        if not re.fullmatch(id_pattern, node) or status != "完成":
            continue
        reflection_idx = lookup.get("reflection")
        if reflection_idx is None or reflection_idx >= len(cells):
            errors.append(
                f"{path} completed atomic node `{node}` has no reflection column"
            )
            continue
        references = sorted(set(re.findall(r"\bR-\d{3}\b", cells[reflection_idx])))
        if not references:
            errors.append(
                f"{path} completed atomic node `{node}` has no `R-*` reflection"
            )
            continue
        missing = [reference for reference in references if reference not in records]
        if missing:
            errors.append(
                f"{path} completed atomic node `{node}` references missing reflections: "
                + ", ".join(missing)
            )
            continue
        scoped = [
            reference
            for reference in references
            if node in records[reference]["scope"]
            or (
                allow_plan_node_scope
                and related_plan_node is not None
                and related_plan_node in records[reference]["scope"]
            )
        ]
        if not scoped:
            errors.append(
                f"{path} completed atomic node `{node}` has no reflection scoped to "
                f"`{node}` or `{related_plan_node or 'its plan node'}`"
            )
            continue
        available = [reference for reference in scoped if reference not in used_reflections]
        if not available:
            owners = ", ".join(
                f"{reference}->{used_reflections[reference]}" for reference in scoped
            )
            errors.append(
                f"{path} completed atomic node `{node}` reuses a reflection already "
                f"assigned to another node: {owners}"
            )
            continue
        used_reflections[available[0]] = node


def is_clean_record(value: str | None) -> bool:
    if value is None:
        return False
    normalized = norm_cell(value).strip()
    no_op = re.fullmatch(r"N/A\s*:\s*(.+)", normalized, flags=re.IGNORECASE)
    if no_op is not None:
        return is_concrete(no_op.group(1))
    completed = re.fullmatch(r"\d{4}-\d{2}-\d{2}\s*/\s*(.+)", normalized)
    return completed is not None and is_concrete(completed.group(1))


def check_clean_contract(
    path: Path,
    text: str,
    program_status: str | None,
    errors: list[str],
    warnings: list[str],
) -> None:
    """Validate the optional Clean contract without breaking legacy plans."""
    state = metadata_value(text, "Clean state")
    last_clean = metadata_value(text, "Last clean")
    if state is None and last_clean is None:
        return
    if state is None or last_clean is None:
        missing = "Clean state" if state is None else "Last clean"
        errors.append(f"{path} Clean contract is incomplete: missing {missing}")
        return
    if state not in VALID_CLEAN_STATES:
        choices = " / ".join(sorted(VALID_CLEAN_STATES))
        errors.append(
            f"{path} Clean state must be exactly one of `{choices}`, got `{state}`"
        )
        return
    if state == "Due":
        message = (
            f"{path} Clean state is `Due`; run the Clean contract and set it to "
            "`Not due`"
        )
        if program_status in {"待验收", "完成"}:
            errors.append(f"{message} before Overall status is `{program_status}`")
        else:
            warnings.append(message)
    if program_status in {"待验收", "完成"} and not is_clean_record(last_clean):
        errors.append(
            f"{path} Last clean must cite a date plus evidence, or "
            f"`N/A: <concrete reason>`, before `{program_status}`"
        )


def check_standing_checklist_completion(path: Path, text: str, errors: list[str]) -> None:
    """待验收/完成 task packages must have no unchecked Standing Checklist items."""
    status = task_status(text)
    if status not in {"待验收", "完成"}:
        return
    section = markdown_h2_section(text, "Standing Checklist")
    if section is None:
        return
    if not checklist_items(section):
        errors.append(f"{path} status is `{status}`, but Standing Checklist has no checklist items")
    unchecked = re.findall(r"^\s*-\s+\[\s\]\s+(.+)$", section, flags=re.MULTILINE)
    if unchecked:
        errors.append(
            f"{path} status is `{status}`, but Standing Checklist still has "
            f"{len(unchecked)} unchecked items"
        )
    for line in re.findall(r"^\s*-\s+\[[xX]\]\s+(.+)$", section, flags=re.MULTILINE):
        if "N/A" in line and not re.search(r"N/A\s*:\s*\S+", line, flags=re.IGNORECASE):
            errors.append(
                f"{path} Standing Checklist has an N/A item without a concrete reason: {line}"
            )


def check_abstraction_gate(
    path: Path,
    text: str,
    status: str | None,
    errors: list[str],
    warnings: list[str],
) -> None:
    """Require a declared impact and proof for structural abstraction changes."""
    raw_impact = metadata_value(text, "Abstraction impact")
    if raw_impact is None:
        message = (
            f"{path} must declare Abstraction impact as one of "
            "`none / reuse / new / modify / remove`"
        )
        (errors if status in {"待验收", "完成"} else warnings).append(message)
        return
    if re.fullmatch(r"<[^>\n]+>", raw_impact):
        if status in {"待验收", "完成"}:
            errors.append(f"{path} must resolve Abstraction impact before `{status}`")
        return

    impact = raw_impact.lower()
    if impact not in VALID_ABSTRACTION_IMPACTS:
        choices = " / ".join(sorted(VALID_ABSTRACTION_IMPACTS))
        errors.append(
            f"{path} Abstraction impact must be exactly one of `{choices}`, got `{raw_impact}`"
        )
        return

    section = markdown_heading_section(text, "Abstraction Gate")
    if section is None:
        errors.append(f"{path} declares Abstraction impact `{impact}` but has no Abstraction Gate")
        return

    if impact not in STRUCTURAL_ABSTRACTION_IMPACTS:
        not_applicable = re.search(r"(?im)^\s*N/A\s*:\s*(.+?)\s*$", section)
        if not_applicable is None or not is_concrete(not_applicable.group(1)):
            errors.append(
                f"{path} Abstraction impact `{impact}` requires `N/A: <concrete reason>` "
                "in Abstraction Gate"
            )
        if table_as_mapping(section):
            errors.append(
                f"{path} Abstraction impact `{impact}` must replace the unused gate table "
                "with the concise N/A reason"
            )
        return

    gate = table_as_mapping(section)
    missing = [field for field in ABSTRACTION_GATE_FIELDS if not is_concrete(gate.get(field))]
    if missing:
        errors.append(f"{path} Abstraction Gate is incomplete: " + ", ".join(missing))


def check_execution_readiness_gate(
    path: Path,
    text: str,
    program_status: str | None,
    errors: list[str],
) -> None:
    """Block execution until uncertainty-heavy work has a concrete readiness map."""
    readiness = metadata_value(text, "Execution readiness")
    if readiness is None:
        errors.append(
            f"{path} is missing top-level field: Execution readiness "
            "(`Blocked / Ready / Not required`)"
        )
        return
    if readiness not in VALID_EXECUTION_READINESS:
        choices = " / ".join(sorted(VALID_EXECUTION_READINESS))
        errors.append(
            f"{path} Execution readiness must be exactly one of "
            f"`{choices}`, got `{readiness}`"
        )
        return

    section = markdown_heading_section(text, "Execution Readiness Gate")
    if section is None:
        errors.append(f"{path} has no Execution Readiness Gate")
        return

    if readiness == "Not required":
        not_applicable = re.search(r"(?im)^\s*N/A\s*:\s*(.+?)\s*$", section)
        if not_applicable is None or not is_concrete(not_applicable.group(1)):
            errors.append(
                f"{path} Execution readiness `Not required` needs "
                "`N/A: <concrete reason>`"
            )
        if table_as_mapping(section):
            errors.append(
                f"{path} Execution readiness `Not required` must replace the gate table "
                "with the concise N/A reason"
            )
        return

    if readiness == "Blocked":
        if program_status in {"进行中", "待验证", "待验收", "完成"}:
            errors.append(
                f"{path} Execution readiness is `Blocked`, but Overall status "
                f"is `{program_status}`; resolve the gate before execution"
            )
        return

    gate = table_as_mapping(section)
    required_fields = (
        LEAN_EXECUTION_READINESS_GATE_FIELDS
        if "Key uncertainty / hypothesis" in gate
        else EXECUTION_READINESS_GATE_FIELDS
    )
    missing = [
        field
        for field in required_fields
        if not is_concrete(gate.get(field))
    ]
    if missing:
        errors.append(
            f"{path} Execution Readiness Gate is incomplete: " + ", ".join(missing)
        )


def check_task_completion_contract(
    path: Path,
    text: str,
    status: str | None,
    require_verification_matrix: bool,
    errors: list[str],
) -> None:
    if status not in {"待验收", "完成"}:
        return

    lean = markdown_heading_section(text, "Completion Review") is not None
    for title in ("Acceptance criteria", "Verification"):
        section = bold_field_section(text, title)
        if not checklist_items(section):
            errors.append(f"{path} status is `{status}`, but {title} has no checklist items")
        unchecked = checklist_unchecked(section)
        if unchecked:
            errors.append(
                f"{path} status is `{status}`, but {title} still has "
                f"{len(unchecked)} unchecked items"
            )

    atomic_heading = "Atomic Plan" if lean else "Atomic Implementation Plan"
    atomic_rows = section_status_rows(markdown_heading_section(text, atomic_heading))
    atomic_nodes = [row for row in atomic_rows if re.fullmatch(r"N-\d{3}", row[0])]
    if not atomic_nodes:
        errors.append(
            f"{path} status is `{status}`, but Atomic Implementation Plan has no atomic nodes"
        )
    for row_id, row_status in atomic_nodes:
        if row_status not in {"完成", "已取消"}:
            errors.append(
                f"{path} status is `{status}`, but atomic node `{row_id}` is `{row_status}`"
            )

    if lean:
        review = markdown_heading_section(text, "Completion Review")
        required_fields = ["Final result", "Evidence", "Unverified / residual risk"]
        if status == "完成":
            required_fields.append("Completed")
        incomplete_fields = [
            label for label in required_fields if not is_concrete(bullet_field(review, label))
        ]
        if incomplete_fields:
            errors.append(
                f"{path} status is `{status}`, but Completion Review is incomplete: "
                + ", ".join(incomplete_fields)
            )
        return

    verification_rows = section_status_rows(markdown_heading_section(text, "Verification Matrix"))
    verification_items = [row for row in verification_rows if re.fullmatch(r"V-\d{3}", row[0])]
    if require_verification_matrix and not verification_items:
        errors.append(
            f"{path} status is `{status}`, but Verification Matrix has no verification rows"
        )
    for row_id, row_status in verification_items:
        if row_status != "完成":
            errors.append(
                f"{path} status is `{status}`, but verification `{row_id}` is `{row_status}`"
            )

    red_team = markdown_heading_section(text, "Pre-completion Red Team")
    answers: dict[str, str] = {}
    if red_team is not None:
        for header, cells in iter_table_rows(red_team):
            normalized = [norm_cell(cell).lower() for cell in header]
            if "answer" not in normalized:
                continue
            answer_idx = normalized.index("answer")
            if answer_idx < len(cells):
                answers[norm_cell(cells[0])] = norm_cell(cells[answer_idx])
    missing_answers = [
        f"RT-{number}"
        for number in range(1, 5)
        if not is_concrete(answers.get(f"RT-{number}"))
    ]
    if missing_answers:
        errors.append(
            f"{path} status is `{status}`, but Pre-completion Red Team has unanswered items: "
            + ", ".join(missing_answers)
        )

    writeback = markdown_heading_section(text, "Completion Writeback")
    if writeback is None:
        writeback = markdown_heading_section(text, "Completion Review")
    required_fields = ["Memory writeback", "Final result", "Output artifacts"]
    if status == "完成":
        required_fields.append("Completed")
    incomplete_fields = [
        label for label in required_fields if not is_concrete(bullet_field(writeback, label))
    ]
    if incomplete_fields:
        errors.append(
            f"{path} status is `{status}`, but Completion Writeback is incomplete: "
            + ", ".join(incomplete_fields)
        )


def check_completion_memory_refs(
    path: Path,
    text: str,
    status: str | None,
    memory_text: str,
    errors: list[str],
) -> None:
    if status not in {"待验收", "完成"}:
        return
    writeback = markdown_heading_section(text, "Completion Writeback")
    if writeback is None:
        writeback = markdown_heading_section(text, "Completion Review")
    value = bullet_field(writeback, "Memory writeback")
    if value is None or re.match(r"^(?:不需要|N/A)\s*[:：]", value, flags=re.IGNORECASE):
        return
    references = sorted(set(re.findall(r"\b(?:D|F|K|CHG|RUN|HIST|R|Q|PL)-\d{3}\b", value)))
    if not references:
        errors.append(
            f"{path} Completion Writeback Memory writeback has no memory IDs or N/A reason"
        )
        return
    missing = [
        reference
        for reference in references
        if not re.search(rf"\b{re.escape(reference)}\b", memory_text)
    ]
    if missing:
        errors.append(
            f"{path} Completion Writeback Memory writeback references missing entries: "
            + ", ".join(missing)
        )


def check_program_completion_contract(
    path: Path,
    text: str,
    status: str | None,
    node_statuses: dict[str, str],
    errors: list[str],
) -> None:
    if status != "完成":
        return
    for link, node_status in node_statuses.items():
        if node_status not in {"完成", "已取消"}:
            errors.append(
                f"{path} Overall status is `完成`, but `{link}` is `{node_status}` in Node Status"
            )
    task_list = markdown_heading_section(text, "Task List")
    unchecked = checklist_unchecked(task_list)
    if unchecked:
        errors.append(
            f"{path} Overall status is `完成`, but Task List still has "
            f"{len(unchecked)} unchecked items"
        )
    for label in ("Active task package", "Active plan node", "Next plan node", "Next checkpoint"):
        value = metadata_value(text, label)
        if value is not None and value not in {"None", "无"}:
            errors.append(f"{path} Overall status is `完成`, but {label} is `{value}`")
    current_status = markdown_heading_section(text, "Current Status")
    for label in ("Current blocker", "Next step", "Next human decision", "Pending memory write"):
        value = bullet_field(current_status, label)
        if value is None:
            value = metadata_value(text, label)
        if value is not None and value not in {"None", "无"}:
            errors.append(
                f"{path} Overall status is `完成`, but Current Status {label} is `{value}`"
            )
    memory_sync = markdown_heading_section(text, "Memory Sync")
    for row_id, sync_status in section_status_rows(memory_sync):
        if sync_status.lower() == "pending":
            errors.append(
                f"{path} Overall status is `完成`, but Memory Sync `{row_id}` is pending"
            )


def check_program_waiting_acceptance_contract(
    path: Path,
    text: str,
    status: str | None,
    node_statuses: dict[str, str],
    errors: list[str],
) -> None:
    if status != "待验收":
        return
    if not node_statuses:
        errors.append(f"{path} Overall status is `待验收`, but Node Status has no valid rows")
        return
    for link, node_status in node_statuses.items():
        if node_status not in {"待验收", "完成", "已取消"}:
            errors.append(
                f"{path} Overall status is `待验收`, but `{link}` is "
                f"`{node_status}` in Node Status"
            )
    if "待验收" not in node_statuses.values():
        errors.append(
            f"{path} Overall status is `待验收`, but no Node Status row awaits acceptance"
        )
    for label in ("Latest evidence", "Next checkpoint"):
        value = metadata_value(text, label)
        if not is_concrete(value):
            errors.append(
                f"{path} Overall status is `待验收`, but {label} is not concrete"
            )
    current_status = markdown_heading_section(text, "Current Status")
    next_human_decision = bullet_field(current_status, "Next human decision")
    if next_human_decision is None:
        next_human_decision = metadata_value(text, "Next human decision")
    if not is_concrete(next_human_decision):
        errors.append(
            f"{path} Overall status is `待验收`, but Current Status "
            "Next human decision is not concrete"
        )


def check_program_blocked_contract(
    path: Path,
    text: str,
    status: str | None,
    node_statuses: dict[str, str],
    errors: list[str],
) -> None:
    if status != "阻塞":
        return
    if "阻塞" not in node_statuses.values():
        errors.append(
            f"{path} Overall status is `阻塞`, but no Node Status row is `阻塞`"
        )
    current_status = markdown_heading_section(text, "Current Status")
    blocker = bullet_field(current_status, "Current blocker")
    if blocker is None:
        blocker = metadata_value(text, "Current blocker")
    if not is_concrete(blocker):
        errors.append(
            f"{path} Overall status is `阻塞`, but Current Status Current blocker "
            "is not concrete"
        )


def check_lite_plan(
    path: Path,
    text: str,
    errors: list[str],
) -> dict[str, str]:
    section = markdown_heading_section(text, "Plan")
    statuses: dict[str, str] = {}
    for header, cells in iter_table_rows(section or ""):
        normalized = [norm_cell(cell).lower() for cell in header]
        lookup = {name: index for index, name in enumerate(normalized)}
        node_idx = lookup.get("node")
        status_idx = lookup.get("status")
        if node_idx is None or status_idx is None:
            continue
        if max(node_idx, status_idx) >= len(cells):
            continue
        node = norm_cell(cells[node_idx])
        status = norm_cell(cells[status_idx])
        if not re.fullmatch(r"NODE-\d{3}", node):
            continue
        if node in statuses:
            errors.append(f"{path} Plan contains duplicate node `{node}`")
        if status not in VALID_TASK_STATUSES:
            errors.append(f"{path} Plan node `{node}` has invalid status `{status}`")
        statuses[node] = status
    if not statuses:
        errors.append(f"{path} Plan has no valid NODE-NNN row")
    return statuses


def check_unique_section_ids(
    path: Path,
    text: str,
    section_title: str,
    id_pattern: str,
    label: str,
    errors: list[str],
) -> None:
    section = markdown_heading_section(text, section_title)
    if section is None:
        return
    seen: set[str] = set()
    duplicates: set[str] = set()
    for _, cells in iter_table_rows(section):
        row_id = norm_cell(cells[0]) if cells else ""
        if not re.fullmatch(id_pattern, row_id):
            continue
        if row_id in seen:
            duplicates.add(row_id)
        seen.add(row_id)
    for row_id in sorted(duplicates):
        errors.append(f"{path} {section_title} has duplicate {label} ID `{row_id}`")


def check_unique_memory_ids(path: Path, text: str, errors: list[str]) -> None:
    pattern = r"(?:D|F|K|CHG|RUN|HIST|R|Q|PL)-\d{3}"
    seen: set[str] = set()
    duplicates: set[str] = set()
    for _, cells in iter_table_rows(text):
        row_id = norm_cell(cells[0]) if cells else ""
        if not re.fullmatch(pattern, row_id):
            continue
        if row_id in seen:
            duplicates.add(row_id)
        seen.add(row_id)
    for row_id in sorted(duplicates):
        errors.append(f"{path} has duplicate memory ID `{row_id}`")


def check_task_identity(path: Path, text: str, errors: list[str]) -> None:
    filename = re.match(r"^(TASK-\d{3})(?:[-_].*)?\.md$", path.name)
    heading = re.search(r"^#\s+(TASK-\d{3})\b", text, flags=re.MULTILINE)
    if filename is None or heading is None:
        return
    filename_id = filename.group(1)
    heading_id = heading.group(1)
    if filename_id != heading_id:
        errors.append(
            f"{path} filename ID `{filename_id}` does not match H1 ID `{heading_id}`"
        )


def check_task_list_sync(
    path: Path,
    text: str,
    node_statuses: dict[str, str],
    task_node_mapping: dict[str, str],
    errors: list[str],
) -> None:
    section = markdown_heading_section(text, "Task List")
    if section is None:
        return
    listed: dict[str, bool] = {}
    for checked, node in re.findall(
        r"^\s*-\s+\[([ xX])\]\s+(NODE-\d{3})\b",
        section,
        flags=re.MULTILINE,
    ):
        if node in listed:
            errors.append(f"{path} Task List contains duplicate entry `{node}`")
        listed[node] = checked.lower() == "x"

    for link, node in task_node_mapping.items():
        status = node_statuses.get(link)
        if node not in listed:
            errors.append(f"{path} Task List is missing `{node}`")
            continue
        expected_checked = status in {"完成", "已取消"}
        if listed[node] != expected_checked:
            expected = "checked" if expected_checked else "unchecked"
            errors.append(
                f"{path} Task List `{node}` must be {expected} while Node Status is `{status}`"
            )


def find_program_history_sections(path: Path, text: str, warnings: list[str]) -> None:
    for pattern in PROGRAM_HISTORY_PATTERNS:
        if re.search(pattern, text, flags=re.IGNORECASE | re.MULTILINE):
            warnings.append(
                f"{path} contains a history/log section that should move to memory.md: {pattern}"
            )


def current_task_from_program(text: str) -> str | None:
    value = metadata_value(text, "Active task package", "当前任务包")
    if value is None:
        return None
    if value in {"无", "none", "None"} or value.startswith("<"):
        return None
    return value.split()[0].strip()


def check_program_node_graph(
    path: Path,
    text: str,
    errors: list[str],
) -> tuple[dict[str, str], dict[str, str]]:
    section = markdown_heading_section(text, "Node Status")
    if section is None:
        section = markdown_heading_section(text, "Node Index")
    node_records: dict[str, tuple[str, str, list[str]]] = {}
    link_to_node: dict[str, str] = {}
    if section is None:
        return {}, {}

    detail_dependencies: dict[str, list[str]] = {}
    details = markdown_heading_section(text, "Node Details") or section
    for header, cells in iter_table_rows(details or ""):
        normalized = [norm_cell(cell).lower() for cell in header]
        lookup = {name: index for index, name in enumerate(normalized)}
        node_idx = lookup.get("node", lookup.get("节点"))
        dependencies_idx = lookup.get("dependencies", lookup.get("依赖"))
        if node_idx is None or dependencies_idx is None:
            continue
        if max(node_idx, dependencies_idx) >= len(cells):
            continue
        node = norm_cell(cells[node_idx])
        if not re.fullmatch(r"NODE-\d{3}", node):
            continue
        if node in detail_dependencies:
            errors.append(f"{path} has multiple Node Details rows for `{node}`")
        detail_dependencies[node] = re.findall(r"\bNODE-\d{3}\b", cells[dependencies_idx])

    for header, cells in iter_table_rows(section):
        normalized = [norm_cell(cell).lower() for cell in header]
        lookup = {name: index for index, name in enumerate(normalized)}
        node_idx = lookup.get("node", lookup.get("节点"))
        status_idx = lookup.get("status", lookup.get("状态"))
        task_idx = lookup.get("task package", lookup.get("任务包"))
        dependencies_idx = lookup.get("dependencies", lookup.get("依赖"))
        if node_idx is None or task_idx is None:
            continue
        indexes = [node_idx, task_idx]
        if status_idx is not None:
            indexes.append(status_idx)
        if max(indexes) >= len(cells):
            continue
        node = norm_cell(cells[node_idx])
        if not re.fullmatch(r"NODE-\d{3}", node):
            continue
        status = norm_cell(cells[status_idx]) if status_idx is not None else ""
        if status and status not in VALID_TASK_STATUSES:
            errors.append(f"{path} Node Status row `{node}` has invalid status `{status}`")
        task_match = re.search(r"tasks/TASK-\d{3}[-A-Za-z0-9_]*\.md", cells[task_idx])
        if task_match is None:
            errors.append(f"{path} Node Status row `{node}` has no valid task package path")
            continue
        link = task_match.group(0)
        dependencies = (
            re.findall(r"\bNODE-\d{3}\b", cells[dependencies_idx])
            if dependencies_idx is not None and dependencies_idx < len(cells)
            else detail_dependencies.get(node, [])
        )
        if node in node_records:
            errors.append(f"{path} has multiple Node Status rows for `{node}`")
        if link in link_to_node and link_to_node[link] != node:
            errors.append(
                f"{path} task package `{link}` appears in multiple Node Status rows: "
                f"`{link_to_node[link]}` and `{node}`"
            )
        node_records[node] = (link, status, dependencies)
        link_to_node.setdefault(link, node)

    for node, (_, _, dependencies) in node_records.items():
        for dependency in dependencies:
            if dependency not in node_records:
                errors.append(f"{path} node `{node}` depends on missing node `{dependency}`")

    visited: set[str] = set()
    visiting: set[str] = set()

    def visit(node: str, trail: list[str]) -> None:
        if node in visiting:
            cycle_start = trail.index(node) if node in trail else 0
            cycle = trail[cycle_start:] + [node]
            message = " -> ".join(cycle)
            error = f"{path} Node Status dependency cycle: {message}"
            if error not in errors:
                errors.append(error)
            return
        if node in visited:
            return
        visiting.add(node)
        for dependency in node_records[node][2]:
            if dependency in node_records:
                visit(dependency, trail + [node])
        visiting.remove(node)
        visited.add(node)

    for node in node_records:
        visit(node, [])

    statuses = {
        link: status
        for link, status, _ in node_records.values()
        if status in VALID_TASK_STATUSES
    }
    return statuses, link_to_node


def task_status(text: str) -> str | None:
    value = metadata_value(text, "Status")
    return value if value in VALID_TASK_STATUSES else None


LOOP_CONTRACT_FIELDS = {
    "Loop goal",
    "Success criteria",
    "Failure signal",
    "Verifier",
    "Max iterations",
    "Reflect trigger",
    "Iterate rule",
    "Stop / escalation condition",
    "Memory write rule",
}


def check_program_loop_contract(
    path: Path,
    text: str,
    mode: str | None,
    profile: str,
    errors: list[str],
) -> int | None:
    if mode != "Loop":
        return None
    if profile == "Lite":
        errors.append(f"{path} uses Loop mode, which requires Profile `Full`")

    contract = table_as_mapping(markdown_heading_section(text, "Loop Contract"))
    missing = sorted(
        field for field in LOOP_CONTRACT_FIELDS if not is_concrete(contract.get(field))
    )
    if missing:
        errors.append(f"{path} Loop Contract is incomplete: " + ", ".join(missing))

    maximum: int | None = None
    maximum_value = contract.get("Max iterations")
    if maximum_value and re.fullmatch(r"[1-9]\d*", norm_cell(maximum_value)):
        maximum = int(norm_cell(maximum_value))
    else:
        errors.append(f"{path} Loop Contract Max iterations must be a positive integer")

    loop_iteration = metadata_value(text, "Loop iteration")
    if loop_iteration is None or not re.fullmatch(r"\d+/[1-9]\d*", loop_iteration):
        errors.append(
            f"{path} Loop iteration must use `<current>/<max>` with a finite positive max"
        )
    elif maximum is not None:
        current, declared_maximum = (int(part) for part in loop_iteration.split("/"))
        if declared_maximum != maximum or current > maximum:
            errors.append(
                f"{path} Loop iteration `{loop_iteration}` does not agree with "
                f"Max iterations `{maximum}`"
            )

    loop_state = metadata_value(text, "Loop state")
    valid_loop_states = {"Goal", "Plan", "Act", "Verify", "Reflect", "Iterate", "Pass", "Blocked"}
    if loop_state not in valid_loop_states:
        errors.append(f"{path} Loop state must be one concrete Loop step")

    loop_state_section = markdown_heading_section(text, "Loop State")
    if loop_state_section is None or not re.search(r"\bL-\d{3}\b", loop_state_section):
        errors.append(f"{path} Loop State must include a current iteration ID such as L-001")
    return maximum


def check_task_loop_contract(
    path: Path,
    text: str,
    mode: str | None,
    program_mode: str | None,
    program_maximum: int | None,
    errors: list[str],
) -> None:
    if mode != program_mode and mode is not None and program_mode is not None:
        errors.append(
            f"{path} Plan mode mismatch: program.md is `{program_mode}`, task package is `{mode}`"
        )
    if mode != "Loop":
        return
    budget = metadata_value(text, "Loop budget")
    if budget is None or not re.fullmatch(r"[1-9]\d*", budget):
        errors.append(f"{path} Loop budget must be a positive integer")
    elif program_maximum is not None and int(budget) > program_maximum:
        errors.append(
            f"{path} Loop budget `{budget}` exceeds program Max iterations `{program_maximum}`"
        )
    attempt = markdown_heading_section(text, "Current Loop Attempt")
    if attempt is None or not re.search(r"\bL-\d{3}\b", attempt):
        errors.append(f"{path} Current Loop Attempt must include an iteration ID such as L-001")


def check_hypothesis_contract(path: Path, text: str, errors: list[str]) -> None:
    section = markdown_heading_section(text, "Exploration And Hypothesis Validation")
    if section is None:
        return
    verdicts = {"supported", "disproven", "uncertain", "支持", "推翻", "不确定"}
    open_statuses = {"待验证", "探索中", "进行中"}
    for header, cells in iter_table_rows(section):
        normalized = [norm_cell(cell).lower() for cell in header]
        lookup = {name: index for index, name in enumerate(normalized)}
        status_idx = lookup.get("status", lookup.get("状态"))
        validation_idx = lookup.get("validation method", lookup.get("验证方法"))
        action_idx = lookup.get("pass / fail action", lookup.get("通过 / 失败动作"))
        evidence_idx = lookup.get("evidence", lookup.get("证据"))
        if status_idx is None or not cells:
            continue
        hypothesis_id = norm_cell(cells[0])
        if not re.fullmatch(r"H-\d{3}", hypothesis_id):
            continue
        status = norm_cell(cells[status_idx]).strip("[]") if status_idx < len(cells) else ""
        validation = (
            cells[validation_idx]
            if validation_idx is not None and validation_idx < len(cells)
            else None
        )
        action = (
            cells[action_idx]
            if action_idx is not None and action_idx < len(cells)
            else None
        )
        evidence = (
            cells[evidence_idx]
            if evidence_idx is not None and evidence_idx < len(cells)
            else None
        )
        if not is_concrete(validation):
            errors.append(f"{path} hypothesis `{hypothesis_id}` lacks a concrete validation method")
        if not is_concrete(action):
            errors.append(
                f"{path} hypothesis `{hypothesis_id}` lacks a concrete pass / fail action"
            )
        if status in verdicts:
            if not is_concrete(evidence):
                errors.append(
                    f"{path} hypothesis `{hypothesis_id}` has verdict `{status}` "
                    "but no concrete evidence"
                )
        elif status in open_statuses:
            continue
        else:
            errors.append(
                f"{path} hypothesis `{hypothesis_id}` must stay open or close with a verdict "
                "(supported / disproven / uncertain), not `" + status + "`"
            )


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


def section_declares_none(text: str, heading: str) -> bool:
    section = markdown_heading_section(text, heading)
    return bool(section and re.search(r"\bNone\b|无", section, flags=re.IGNORECASE))


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


def git_command(root: Path, *args: str) -> subprocess.CompletedProcess[str] | None:
    try:
        return subprocess.run(
            ["git", "-C", str(root), *args],
            check=False,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        return None


def fallback_tasks_output_ignored(root: Path) -> bool:
    state: bool | None = None
    candidates = [root / ".gitignore", root / "tasks" / ".gitignore"]
    for gitignore in candidates:
        if not gitignore.exists():
            continue
        for raw_line in read_text(gitignore).splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            negated = line.startswith("!")
            pattern = line[1:] if negated else line
            pattern = pattern.lstrip("/").rstrip("/")
            if gitignore.parent == root / "tasks" and not pattern.startswith("tasks/"):
                pattern = f"tasks/{pattern}"
            if pattern in {
                "tasks/output",
                "tasks/output/*",
                "tasks/output/**",
                "**/tasks/output",
                "**/tasks/output/*",
                "**/tasks/output/**",
            }:
                state = not negated
    return state is True


def tasks_output_ignored(root: Path) -> bool:
    probe = "tasks/output/.plan-skill-ignore-probe"
    result = git_command(root, "check-ignore", "--no-index", "-q", "--", probe)
    if result is not None and result.returncode in {0, 1}:
        return result.returncode == 0
    return fallback_tasks_output_ignored(root)


def tracked_task_outputs(root: Path) -> list[str]:
    result = git_command(root, "ls-files", "--", TASK_OUTPUT_ROOT)
    if result is None or result.returncode != 0:
        return []
    return [line for line in result.stdout.splitlines() if line.strip()]


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Validate plan-skill program.md, tasks/TASK-*.md, output artifact "
            "pointers, execution-readiness and abstraction gates, links, and status records."
        )
    )
    parser.add_argument(
        "root",
        nargs="?",
        default=".",
        help="Project root, default: current directory",
    )
    parser.add_argument("--json", action="store_true", help="Output JSON")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Return a non-zero exit code when warnings are present",
    )
    args = parser.parse_args()

    root = Path(args.root).resolve()
    errors: list[str] = []
    warnings: list[str] = []

    program_path = root / "program.md"
    memory_path = root / "memory.md"
    if program_path.exists():
        program_text = read_text_for_validation(program_path, errors)
    else:
        errors.append(f"Missing file: {program_path}")
        program_text = ""
    profile = detect_profile(program_text, program_path, errors)
    lite = profile == "Lite"
    lean_lite = lite and markdown_heading_section(program_text, "Plan") is not None
    lean_full = not lite and markdown_heading_section(program_text, "Node Index") is not None
    program_status: str | None = None
    program_mode: str | None = None
    if program_text:
        required_program = (
            PROGRAM_REQUIRED_LITE
            if lean_lite
            else PROGRAM_REQUIRED_LEAN_FULL
            if lean_full
            else PROGRAM_REQUIRED_LEGACY_LITE
            if lite
            else PROGRAM_REQUIRED
        )
        check_required_items(
            program_path, program_text, required_program, errors
        )
        program_status = parse_enum_metadata(
            program_path,
            program_text,
            ("Overall status", "总体状态"),
            VALID_PROGRAM_STATUSES,
            "Overall status",
            errors,
        )
        if lean_lite:
            program_mode = "Linear"
        else:
            program_mode = parse_enum_metadata(
                program_path,
                program_text,
                ("Plan mode", "计划模式"),
                VALID_PLAN_MODES,
                "Plan mode",
                errors,
            )
        if not lite:
            check_execution_readiness_gate(
                program_path,
                program_text,
                program_status,
                errors,
            )
        check_clean_contract(
            program_path,
            program_text,
            program_status,
            errors,
            warnings,
        )

    memory_text = ""
    if memory_path.exists():
        memory_text = read_text_for_validation(memory_path, errors)
        if memory_text:
            if markdown_heading_section(memory_text, "Decisions") is not None:
                memory_required = MEMORY_REQUIRED_LEAN
            elif markdown_heading_section(memory_text, "Durable State") is not None:
                memory_required = MEMORY_REQUIRED_COMPACT
            else:
                memory_required = MEMORY_REQUIRED
            check_required_items(memory_path, memory_text, memory_required, errors)
    elif not lite:
        errors.append(f"Missing file: {memory_path}")

    lite_reflection_ledger = has_reflection_ledger(program_text) if lean_lite else False
    memory_reflection_ledger = has_reflection_ledger(memory_text)
    lite_reflections = (
        reflection_records(program_path, program_text, errors)
        if lite_reflection_ledger
        else {}
    )
    memory_reflections = (
        reflection_records(memory_path, memory_text, errors)
        if memory_reflection_ledger
        else {}
    )
    if lean_lite and not lite_reflection_ledger:
        warnings.append(
            "program.md has no Reflection Log; add one `R-*` entry per completed node"
        )
    if lean_full and memory_text and not memory_reflection_ledger:
        warnings.append(
            "memory.md has no Reflections ledger; add one `R-*` entry per completed node"
        )

    checked_paths: list[Path] = [program_path] if program_path.exists() else []
    if memory_path.exists():
        checked_paths.append(memory_path)

    if program_text:
        find_placeholders(program_path, program_text, warnings)
        check_table_shapes(program_path, program_text, errors)
        check_completed_rows(program_path, program_text, errors)
        check_hypothesis_contract(program_path, program_text, errors)
        find_program_history_sections(program_path, program_text, warnings)
        if not node_ids(program_text):
            warnings.append("program.md has no plan node ID, e.g. NODE-001")
        if not lite and not lean_full:
            if not size_values(program_text):
                warnings.append("program.md has no task-package size value, e.g. `S` or `M`")
            context_is_explicitly_empty = section_declares_none(
                program_text, "Context And References"
            )
            if not context_ref_ids(program_text) and not context_is_explicitly_empty:
                warnings.append("program.md has no context/reference ID, e.g. CTX-001/REF-001")
            if not preference_ref_ids(program_text) and not section_declares_none(
                program_text, "Preferences And Tradeoffs"
            ):
                warnings.append("program.md has no preference ID, e.g. PREF-001")
    if memory_text:
        find_placeholders(memory_path, memory_text, warnings)
        check_table_shapes(memory_path, memory_text, errors)
        check_unique_memory_ids(memory_path, memory_text, errors)
        if not re.search(r"\b(?:D|F|K|CHG|RUN|HIST|R|Q|PL)-\d{3}\b", memory_text):
            warnings.append(
                "memory.md has no memory entry ID, e.g. "
                "D-001/F-001/RUN-001"
            )
        pending = len(re.findall(r"\|\s*`?待提炼`?\s*\|", memory_text))
        if pending >= 5:
            warnings.append(
                f"memory.md has {pending} run logs pending distillation; "
                "set Clean state to `Due` and run Clean"
            )

    program_loop_maximum = check_program_loop_contract(
        program_path,
        program_text,
        program_mode,
        profile,
        errors,
    ) if program_text else None

    task_links = task_links_from_program(program_text) if program_text else []
    current_task = current_task_from_program(program_text) if program_text else None
    if current_task and current_task not in task_links:
        task_links.append(current_task)

    task_dir = root / "tasks"
    existing_tasks = sorted(task_dir.glob("TASK-*.md")) if task_dir.exists() else []
    existing_by_link = {f"tasks/{path.name}": path for path in existing_tasks}
    for link, path in existing_by_link.items():
        if link not in task_links:
            errors.append(f"{path} is not referenced by program.md")
    task_entries: list[tuple[str, Path]] = []
    for link in sorted(set(task_links) | set(existing_by_link)):
        task_path = check_task_link(root, link, errors)
        if task_path is not None:
            task_entries.append((link, task_path))

    if lean_lite:
        node_statuses = check_lite_plan(program_path, program_text, errors)
        if lite_reflection_ledger:
            check_node_reflections(
                program_path,
                program_text,
                "Plan",
                r"NODE-\d{3}",
                lite_reflections,
                errors,
            )
        task_node_mapping: dict[str, str] = {}
    else:
        node_statuses, task_node_mapping = (
            check_program_node_graph(program_path, program_text, errors)
            if program_text
            else ({}, {})
        )
    active_node = metadata_value(program_text, "Active plan node") if program_text else None
    if current_task:
        expected_active_node = task_node_mapping.get(current_task)
        if (
            expected_active_node is not None
            and active_node is not None
            and active_node != expected_active_node
        ):
            errors.append(
                f"{program_path} Active plan node `{active_node}` does not match "
                f"Active task package `{current_task}` mapped to `{expected_active_node}`"
            )
    elif lean_lite and active_node not in node_statuses:
        errors.append(f"{program_path} Active plan node `{active_node}` is not present in Plan")
    elif not lean_lite and active_node not in {None, "None", "无"}:
        errors.append(
            f"{program_path} Active plan node is `{active_node}`, but Active task package is `None`"
        )
    check_task_list_sync(
        program_path,
        program_text,
        node_statuses,
        task_node_mapping,
        errors,
    )
    if lite and len(task_entries) > 3:
        errors.append(
            f"{program_path} Profile `Lite` has {len(task_entries)} task packages; "
            "upgrade to `Full`"
        )
    package_statuses: dict[str, str] = {}
    has_output_contract = False
    for link, task_path in task_entries:
        checked_paths.append(task_path)
        task_text = read_text_for_validation(task_path, errors)
        if not task_text:
            continue
        check_task_identity(task_path, task_text, errors)
        check_table_shapes(task_path, task_text, errors)
        lean_task = markdown_heading_section(task_text, "Completion Review") is not None
        atomic_heading = "Atomic Plan" if lean_task else "Atomic Implementation Plan"
        check_unique_section_ids(
            task_path,
            task_text,
            atomic_heading,
            r"N-\d{3}",
            "atomic node",
            errors,
        )
        check_unique_section_ids(
            task_path,
            task_text,
            "Verification Matrix",
            r"V-\d{3}",
            "verification",
            errors,
        )
        required_task = (
            TASK_REQUIRED_LEAN
            if lean_task
            else TASK_REQUIRED_LITE
            if lite
            else TASK_REQUIRED
        )
        check_required_items(task_path, task_text, required_task, errors)
        find_placeholders(task_path, task_text, warnings)
        check_completed_rows(task_path, task_text, errors)
        package_status = parse_enum_metadata(
            task_path,
            task_text,
            ("Status",),
            VALID_TASK_STATUSES,
            "task package Status",
            errors,
        )
        if package_status is not None:
            package_statuses[link] = package_status
        package_mode = parse_enum_metadata(
            task_path,
            task_text,
            ("Plan mode",),
            VALID_PLAN_MODES,
            "Plan mode",
            errors,
        )
        if not lean_task or metadata_value(task_text, "Abstraction impact") is not None:
            check_abstraction_gate(
                task_path,
                task_text,
                package_status,
                errors,
                warnings,
            )
        check_standing_checklist_completion(task_path, task_text, errors)
        check_task_completion_contract(
            task_path,
            task_text,
            package_status,
            require_verification_matrix=not lite and not lean_task,
            errors=errors,
        )
        check_completion_memory_refs(
            task_path,
            task_text,
            package_status,
            memory_text,
            errors,
        )
        check_task_loop_contract(
            task_path,
            task_text,
            package_mode,
            program_mode,
            program_loop_maximum,
            errors,
        )
        expected_output = task_output_path(task_path)
        output_value = metadata_value(task_text, "Output artifacts")
        output_section = markdown_heading_section(task_text, "Output Artifacts")
        if output_value is not None or output_section is not None:
            has_output_contract = True
            if (
                output_value != expected_output
                or output_section is None
                or expected_output not in output_section
            ):
                errors.append(
                    f"{task_path} must point its top-level field and Output Artifacts section "
                    f"to `{expected_output}`"
                )
        node_status = node_statuses.get(link)
        task_plan_node = metadata_value(task_text, "Plan node")
        expected_plan_node = task_node_mapping.get(link)
        if expected_plan_node is not None and task_plan_node != expected_plan_node:
            errors.append(
                f"{task_path} Plan node mismatch: program.md maps it to `{expected_plan_node}`, "
                f"task package records `{task_plan_node}`"
            )
        if expected_plan_node is None:
            errors.append(f"{program_path} Node Status is missing a valid row for `{link}`")
        elif node_status is not None and package_status is not None and node_status != package_status:
            errors.append(
                f"Status mismatch: program.md Node Status records {link} as `{node_status}`, "
                f"but task package Status is `{package_status}`"
            )
        if current_task == link and package_status in {"完成", "已取消"}:
            errors.append(
                f"{program_path} Active task package `{link}` already has terminal status "
                f"`{package_status}`"
            )
        completed = completed_nodes(
            markdown_heading_section(task_text, atomic_heading),
            r"N-\d{3}",
        )
        task_reflections = memory_reflections or lite_reflections
        task_ledger_present = memory_reflection_ledger or lite_reflection_ledger
        if completed and not task_ledger_present:
            warnings.append(
                f"{task_path} has completed atomic nodes but no Reflections ledger"
            )
        elif task_ledger_present:
            check_node_reflections(
                task_path,
                task_text,
                atomic_heading,
                r"N-\d{3}",
                task_reflections,
                errors,
                related_plan_node=task_plan_node,
            )
        if "N-001" not in task_text:
            warnings.append(f"{task_path} has no atomic node ID, e.g. N-001")
        if not node_ids(task_text):
            warnings.append(f"{task_path} has no related plan node ID, e.g. NODE-001")
        if lite or lean_task:
            continue
        if package_status in {"待验证", "待验收", "完成"} and "V-001" not in task_text:
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

    effective_statuses = (
        node_statuses
        if lean_lite or node_statuses
        else package_statuses
    )
    check_program_completion_contract(
        program_path,
        program_text,
        program_status,
        effective_statuses,
        errors,
    )
    check_program_waiting_acceptance_contract(
        program_path,
        program_text,
        program_status,
        effective_statuses,
        errors,
    )
    check_program_blocked_contract(
        program_path,
        program_text,
        program_status,
        effective_statuses,
        errors,
    )
    if has_output_contract and not tasks_output_ignored(root):
        errors.append(
            "tasks/output/ is not ignored; add `/tasks/output/` or `tasks/output/` "
            "to git ignore rules"
        )
    tracked_outputs = tracked_task_outputs(root)
    if tracked_outputs:
        errors.append(
            "tasks/output/ contains files tracked by git: " + ", ".join(tracked_outputs)
        )

    ok = not errors and (not args.strict or not warnings)
    result = {
        "root": str(root),
        "profile": profile,
        "ok": ok,
        "status": "pass" if ok else "fail",
        "error_count": len(errors),
        "warning_count": len(warnings),
        "errors": errors,
        "warnings": warnings,
        "checked": [str(path) for path in checked_paths],
    }

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        if errors or (args.strict and warnings):
            print("FAIL")
        elif warnings:
            print("PASS WITH WARNINGS")
        else:
            print("PASS")
        for item in errors:
            print(f"ERROR: {item}")
        for item in warnings:
            print(f"WARN: {item}")
        if not errors and not warnings:
            print("Plan structure, task links, and status records passed validation.")

    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
