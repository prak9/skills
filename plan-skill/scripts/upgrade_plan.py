#!/usr/bin/env python3
"""Upgrade a valid Lite plan to Full without discarding Lite content."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
from datetime import date
from pathlib import Path

from init_plan import render_full_program, render_memory, render_task, slugify
from plan_markdown import (
    bullet_field,
    iter_table_rows,
    markdown_heading_section,
    metadata_value,
    norm_cell,
)


SKILL_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = SKILL_ROOT / "scripts" / "validate_plan.py"


class UpgradeError(RuntimeError):
    pass


def insert_before(text: str, marker: str, block: str) -> str:
    if marker not in text:
        raise UpgradeError(f"cannot find upgrade insertion point: {marker}")
    return text.replace(marker, f"{block.rstrip()}\n\n{marker}", 1)


def insert_after_line(text: str, line: str, block: str) -> str:
    marker = f"{line}\n"
    if marker not in text:
        raise UpgradeError(f"cannot find upgrade insertion point: {line}")
    return text.replace(marker, f"{marker}{block.rstrip()}\n", 1)


def h2_line(text: str, title: str) -> str:
    match = re.search(
        rf"^##(?:\s+\d+\.)?\s+{re.escape(title)}\s*$",
        text,
        flags=re.MULTILINE,
    )
    if match is None:
        raise UpgradeError(f"cannot find H2 section: {title}")
    return match.group(0)


def replace_h2_body(text: str, title: str, body: str) -> str:
    heading = h2_line(text, title)
    pattern = rf"{re.escape(heading)}\n.*?(?=\n##\s+|\Z)"
    replacement = f"{heading}\n\n{body.strip()}"
    updated, count = re.subn(pattern, replacement, text, count=1, flags=re.DOTALL)
    if count != 1:
        raise UpgradeError(f"cannot replace H2 section: {title}")
    return updated


def inline_node_records(text: str) -> list[dict[str, str]]:
    section = markdown_heading_section(text, "Plan")
    records: list[dict[str, str]] = []
    for header, cells in iter_table_rows(section or ""):
        normalized = [norm_cell(cell).lower() for cell in header]
        lookup = {name: index for index, name in enumerate(normalized)}
        required = ("node", "status", "action", "verification", "evidence")
        if any(name not in lookup for name in required):
            continue
        if max(lookup[name] for name in required) >= len(cells):
            continue
        node = norm_cell(cells[lookup["node"]])
        if not re.fullmatch(r"NODE-\d{3}", node):
            continue
        record = {
            name: norm_cell(cells[lookup[name]])
            for name in required
        }
        reflection_idx = lookup.get("reflection")
        record["reflection"] = (
            norm_cell(cells[reflection_idx])
            if reflection_idx is not None and reflection_idx < len(cells)
            else "Pending"
        )
        records.append(record)
    if not records:
        raise UpgradeError("Lite program has no upgradeable Plan rows")
    return records


def acceptance_record(text: str) -> dict[str, str]:
    section = markdown_heading_section(text, "Acceptance")
    for header, cells in iter_table_rows(section or ""):
        normalized = [norm_cell(cell).lower() for cell in header]
        lookup = {name: index for index, name in enumerate(normalized)}
        required = ("id", "condition", "verification", "pass condition")
        if any(name not in lookup for name in required):
            continue
        if max(lookup[name] for name in required) >= len(cells):
            continue
        return {name: norm_cell(cells[lookup[name]]) for name in required}
    raise UpgradeError("Lite program has no upgradeable Acceptance row")


def validate_project(root: Path) -> dict:
    process = subprocess.run(
        [sys.executable, "-B", str(VALIDATOR), str(root), "--json"],
        check=False,
        capture_output=True,
        text=True,
    )
    try:
        result = json.loads(process.stdout)
    except json.JSONDecodeError as exc:
        raise UpgradeError(
            f"validator did not return JSON: {process.stderr.strip() or process.stdout.strip()}"
        ) from exc
    if process.returncode != 0 and result.get("errors"):
        raise UpgradeError("plan is invalid: " + "; ".join(result["errors"][:5]))
    return result


def node_records(program_text: str) -> list[tuple[str, str, str]]:
    section = markdown_heading_section(program_text, "Node Status")
    records: list[tuple[str, str, str]] = []
    for header, cells in iter_table_rows(section or ""):
        normalized = [norm_cell(cell).lower() for cell in header]
        lookup = {name: index for index, name in enumerate(normalized)}
        node_idx = lookup.get("node", lookup.get("节点"))
        status_idx = lookup.get("status", lookup.get("状态"))
        task_idx = lookup.get("task package", lookup.get("任务包"))
        if node_idx is None or status_idx is None or task_idx is None:
            continue
        if max(node_idx, status_idx, task_idx) >= len(cells):
            continue
        node = norm_cell(cells[node_idx])
        status = norm_cell(cells[status_idx])
        match = re.search(r"tasks/TASK-\d{3}[-A-Za-z0-9_]*\.md", cells[task_idx])
        if re.fullmatch(r"NODE-\d{3}", node) and match:
            records.append((node, status, match.group(0)))
    if not records:
        raise UpgradeError("Lite program has no upgradeable Node Status rows")
    return records


def next_decision_id(text: str) -> str:
    numbers = [int(value) for value in re.findall(r"\bD-(\d{3})\b", text)]
    return f"D-{max(numbers, default=0) + 1:03d}"


REFLECTION_TABLE_HEADER = (
    "| ID | Scope | Evidence | Wrong / changed | Right / preserve | Next rule |\n"
    "|---|---|---|---|---|---|"
)


def lite_reflection_rows(text: str) -> list[str]:
    section = markdown_heading_section(text, "Reflection Log") or ""
    return [
        line.strip()
        for line in section.splitlines()
        if re.match(r"^\|\s*R-\d{3}\s*\|", line.strip())
    ]


def prepare_reflection_rows(
    nodes: list[dict[str, str]],
    lite_text: str,
    memory_text: str | None,
    today: str,
) -> list[str]:
    rows = lite_reflection_rows(lite_text)
    occupied = {
        int(number)
        for number in re.findall(
            r"\bR-(\d{3})\b",
            lite_text + "\n" + (memory_text or ""),
        )
    }
    row_ids = {
        match.group(0)
        for row in rows
        if (match := re.search(r"\bR-\d{3}\b", row)) is not None
    }

    def allocate() -> str:
        number = max(occupied, default=0) + 1
        occupied.add(number)
        return f"R-{number:03d}"

    for node in nodes:
        references = re.findall(r"\bR-\d{3}\b", node["reflection"])
        if not references and node["status"] == "完成":
            references = [allocate()]
            node["reflection"] = references[0]
        if not references or references[0] in row_ids:
            continue
        reflection_id = references[0]
        row_ids.add(reflection_id)
        evidence = node["evidence"] or f"profile migration {today}"
        rows.append(
            f"| {reflection_id} | {node['node']} | {evidence} | "
            "Legacy Lite reflection details were not recorded before upgrade. | "
            "The accepted node state and verifier were preserved. | "
            "Capture wrong/right feedback before closing future nodes. |"
        )
    return rows


def merge_reflection_rows(memory: str, rows: list[str]) -> str:
    if not rows:
        return memory
    target = next(
        (
            title
            for title in ("Reflections", "Node Reflections")
            if markdown_heading_section(memory, title) is not None
        ),
        None,
    )
    if target is None:
        block = "## Reflections\n\n" + REFLECTION_TABLE_HEADER + "\n" + "\n".join(rows)
        marker = next(
            (
                h2_line(memory, title)
                for title in ("Reflection And Curation", "Update Rules", "Run Logs")
                if markdown_heading_section(memory, title) is not None
            ),
            None,
        )
        if marker is None:
            raise UpgradeError("memory.md has no insertion point for Reflections")
        return insert_before(memory, marker, block)

    body = markdown_heading_section(memory, target) or REFLECTION_TABLE_HEADER
    additions: list[str] = []
    for row in rows:
        match = re.search(r"\bR-\d{3}\b", row)
        if match is None:
            continue
        reflection_id = match.group(0)
        if re.search(rf"\b{re.escape(reflection_id)}\b", body):
            if row not in body:
                raise UpgradeError(
                    f"reflection ID collision while upgrading Lite: {reflection_id}"
                )
            continue
        additions.append(row)
    if not additions:
        return memory
    return replace_h2_body(
        memory,
        target,
        body.rstrip() + "\n" + "\n".join(additions),
    )


def upgrade_lean_memory(text: str | None, title: str, today: str) -> tuple[str, str]:
    if text is None:
        text = render_memory(title, today)
    if markdown_heading_section(text, "Decisions") is None:
        return upgrade_memory(text, title, today)
    decision_id = next_decision_id(text)
    entry = (
        f"{decision_id}: Upgraded Lite to Full because durable task packages were needed. "
        f"Evidence: profile migration on {today}."
    )
    decisions = markdown_heading_section(text, "Decisions") or ""
    if decisions.strip() == "None yet.":
        new_decisions = entry
    else:
        new_decisions = f"{decisions.strip()}\n\n{entry}"
    return replace_h2_body(text, "Decisions", new_decisions), decision_id


def upgrade_inline_lite(
    text: str,
    memory_text: str | None,
    today: str,
) -> tuple[str, dict[Path, str], str, str]:
    title_match = re.search(r"^#\s+Program:\s*(.+?)\s*$", text, re.MULTILINE)
    if title_match is None:
        raise UpgradeError("program.md has no project title")
    title = title_match.group(1)
    owner = metadata_value(text, "Owner") or "AI"
    nodes = inline_node_records(text)
    reflection_rows = prepare_reflection_rows(nodes, text, memory_text, today)
    acceptance = acceptance_record(text)
    outcome = markdown_heading_section(text, "Outcome")
    constraints = markdown_heading_section(text, "Constraints")
    problem = bullet_field(outcome, "Problem") or "<observable problem>"
    success = bullet_field(outcome, "Success") or "<observable result>"
    non_goals = bullet_field(outcome, "Non-goals") or "None"
    strategic = bullet_field(constraints, "Strategic defaults") or "None"
    tactical = bullet_field(constraints, "Tactical objective") or success
    imperative = (
        bullet_field(constraints, "Imperative bounds")
        or bullet_field(constraints, "Locked")
        or "None"
    )
    negotiable = (
        bullet_field(constraints, "Negotiable space")
        or bullet_field(constraints, "Negotiable")
        or "Implementation details"
    )
    assumptions = bullet_field(constraints, "Material assumptions") or "None"
    escalation = (
        bullet_field(constraints, "Escalate when")
        or "A preference conflicts or a better option requires changing a bound."
    )
    project_slug = slugify(title)

    task_specs: list[tuple[dict[str, str], str]] = []
    for index, node in enumerate(nodes, start=1):
        task_specs.append((node, f"TASK-{index:03d}-{project_slug}"))

    first_stem = task_specs[0][1]
    program = render_full_program(title, first_stem, owner, today)
    program = program.replace(
        "- Overall status: `待开始`",
        f"- Overall status: `{metadata_value(text, 'Overall status') or '待开始'}`",
        1,
    )
    program = program.replace(
        "- Execution readiness: `Blocked`",
        "- Execution readiness: `Not required`",
        1,
    )
    program = replace_h2_body(
        program,
        "Outcome",
        f"- Problem: {problem}\n- Success: {success}\n- Non-goals: {non_goals}",
    )
    program = replace_h2_body(
        program,
        "Execution Readiness Gate",
        "N/A: The Lite plan already has a directly verifiable outcome, acceptance check, and executable node.",
    )
    program = replace_h2_body(
        program,
        "Constraints And Decisions",
        (
            f"- Strategic defaults: {strategic}\n"
            f"- Tactical objective: {tactical}\n"
            f"- Imperative bounds: {imperative}\n"
            f"- Negotiable space: {negotiable}\n"
            f"- Material assumptions: {assumptions}\n"
            "- Decisions: The accepted Lite direction is preserved.\n"
            f"- Escalate when: {escalation}"
        ),
    )
    acceptance_body = (
        "| ID | Condition | Verification | Pass condition |\n"
        "|---|---|---|---|\n"
        f"| {acceptance['id']} | {acceptance['condition']} | "
        f"{acceptance['verification']} | {acceptance['pass condition']} |"
    )
    program = replace_h2_body(program, "Acceptance", acceptance_body)
    program = program.replace(
        "<acceptance evidence>",
        f"{acceptance['verification']} => {acceptance['pass condition']}",
        1,
    )
    node_rows = [
        "| Node | Task package | Dependencies | Acceptance |",
        "|---|---|---|---|",
    ]
    for node, task_stem in task_specs:
        node_rows.append(
            f"| {node['node']} | `tasks/{task_stem}.md` | None | {acceptance['id']} |"
        )
    program = replace_h2_body(program, "Node Index", "\n".join(node_rows))
    active_node = metadata_value(text, "Active plan node")
    active_stem = next(
        (task_stem for node, task_stem in task_specs if node["node"] == active_node),
        None,
    )
    if active_stem is None:
        program = re.sub(
            r"^- Active task package:.*$",
            "- Active task package: `None`",
            program,
            count=1,
            flags=re.MULTILINE,
        )
    else:
        program = re.sub(
            r"^- Active task package:.*$",
            f"- Active task package: `tasks/{active_stem}.md`",
            program,
            count=1,
            flags=re.MULTILINE,
        )
    latest_evidence = metadata_value(text, "Latest evidence") or "None"
    program = re.sub(
        r"^- Latest evidence:.*$",
        f"- Latest evidence: `{latest_evidence}`",
        program,
        count=1,
        flags=re.MULTILINE,
    )
    current_blocker = metadata_value(text, "Current blocker") or "None"
    program = re.sub(
        r"^- Current blocker:.*$",
        f"- Current blocker: `{current_blocker}`",
        program,
        count=1,
        flags=re.MULTILINE,
    )

    tasks: dict[Path, str] = {}
    for node, task_stem in task_specs:
        task = render_task("full", title, task_stem, owner, today)
        task = task.replace("- Status: `待开始`", f"- Status: `{node['status']}`", 1)
        task = task.replace("- Plan node: `NODE-001`", f"- Plan node: `{node['node']}`", 1)
        task = task.replace(
            "<Observable result this task delivers.>",
            success,
            1,
        )
        task = task.replace(
            "- [ ] <specific testable condition>",
            f"- [ ] {acceptance['condition']}",
            1,
        )
        task = task.replace(
            "- [ ] <command or scenario with a clear pass condition>",
            f"- [ ] {acceptance['verification']} => {acceptance['pass condition']}",
            1,
        )
        task = task.replace(
            "**Locked constraints:** None beyond accepted scope and program imperative bounds.",
            f"**Locked constraints:** {imperative}",
            1,
        )
        task = task.replace(
            "**Negotiable space:** Implementation details within the declarative objective and acceptance criteria.",
            f"**Negotiable space:** {negotiable}",
            1,
        )
        task = task.replace("<smallest useful action>", node["action"], 1)
        task = task.replace("<command or scenario>", node["verification"], 1)
        task = task.replace("| N-001 | `待开始` |", f"| N-001 | `{node['status']}` |", 1)
        task = task.replace(
            "| None | Pending; on completion use `R-*` or `None: routine pass produced no durable learning` |",
            f"| {node['evidence']} | {node['reflection']} |",
            1,
        )
        tasks[Path(f"{task_stem}.md")] = task

    memory, decision_id = upgrade_lean_memory(memory_text, title, today)
    memory = merge_reflection_rows(memory, reflection_rows)
    return program, tasks, memory, decision_id


def upgrade_program(text: str, today: str, change_id: str) -> str:
    records = node_records(text)
    if "- Profile: `Lite`" not in text:
        raise UpgradeError("program.md is not a declared Lite plan")
    text = re.sub(r"^##\s+\d+\.\s+", "## ", text, flags=re.MULTILINE)
    text = text.replace("- Profile: `Lite`", "- Profile: `Full`", 1)
    text = re.sub(r"^- Memory:.*$", "- Memory: `memory.md`", text, count=1, flags=re.MULTILINE)

    plan_mode = metadata_value(text, "Plan mode")
    if plan_mode == "Linear" and "- Loop state:" not in text:
        text = insert_after_line(
            text,
            "- Plan mode: `Linear`",
            "- Loop state: `Not applicable`\n- Loop iteration: `Not applicable`",
        )
    if "- Next plan node:" not in text:
        active_node_line = next(
            (line for line in text.splitlines() if line.startswith("- Active plan node:")),
            None,
        )
        if active_node_line is None:
            raise UpgradeError("program.md is missing Active plan node")
        text = insert_after_line(text, active_node_line, "- Next plan node: `None`")
    if "- Next checkpoint:" not in text:
        overall = metadata_value(text, "Overall status")
        checkpoint = "None" if overall == "完成" else "CP-001"
        latest_line = next(
            (line for line in text.splitlines() if line.startswith("- Latest evidence:")),
            None,
        )
        if latest_line is None:
            raise UpgradeError("program.md is missing Latest evidence")
        text = insert_after_line(text, latest_line, f"- Next checkpoint: `{checkpoint}`")
    text = re.sub(r"^- Owner:", "- Owner / TL:", text, count=1, flags=re.MULTILINE)
    if metadata_value(text, "Clean state") is None:
        last_updated_line = next(
            (line for line in text.splitlines() if line.startswith("- Last updated:")),
            None,
        )
        if last_updated_line is None:
            raise UpgradeError("program.md is missing Last updated")
        text = insert_after_line(
            text,
            last_updated_line,
            "- Clean state: `Not due`\n- Last clean: `Not run`",
        )
    if metadata_value(text, "Execution readiness") is None:
        plan_mode_line = next(
            (line for line in text.splitlines() if line.startswith("- Plan mode:")),
            None,
        )
        if plan_mode_line is None:
            raise UpgradeError("program.md is missing Plan mode")
        text = insert_after_line(
            text,
            plan_mode_line,
            "- Execution readiness: `Not required`",
        )
    if markdown_heading_section(text, "Execution Readiness Gate") is None:
        readiness_block = """## Execution Readiness Gate

N/A: This legacy Lite plan predates the readiness gate; its accepted scope, observable verifier, and current execution state are preserved during profile upgrade."""
        text = insert_before(text, h2_line(text, "Problem Definition"), readiness_block)

    context_block = """## Context And References

None yet. Add `CTX-*`, `REF-*`, or `OWN-*` entries only when they change execution.

## Preferences And Tradeoffs

- Strategic defaults: Follow authoritative repository instructions, rules, and skills.
- Tactical objective: Preserve the accepted Lite outcome and its observable acceptance evidence.
- Imperative bounds: None identified beyond accepted scope; add `PREF-*` only when a method or interface is locked.
- Negotiable space: implementation details within acceptance criteria.
- Material assumptions: None identified during profile migration.
- Escalate when: a preference conflicts or scope, acceptance, or an imperative bound must change."""
    text = insert_before(text, h2_line(text, "Goals And Metrics"), context_block)

    planning_block = """## Constraints

- None identified beyond accepted scope and non-goals.

## Strategy

<Smallest vertical path to the acceptance criterion.>

### Dependency And Slicing Strategy

```text
NODE-001 -> acceptance
```

## Decisions

None yet. Add a stable ID only when a decision constrains future work.

## Exploration And Hypothesis Validation

None identified. Add a hypothesis only with a validation method and pass/fail action."""
    text = insert_before(text, h2_line(text, "Implementation Plan"), planning_block)

    graph = "\n".join(f"{node} ({status})" for node, status, _ in records)
    plan_intro = f"""### Overview

Preserve the current Lite vertical slices while adding Full control state.

### Architecture Decisions

- None yet.

### Plan Dependency Graph

```text
{graph}
```
"""
    text = text.replace("### Node Status", f"{plan_intro}\n### Node Status", 1)

    task_lines = []
    for node, status, link in records:
        checked = "x" if status in {"完成", "已取消"} else " "
        task_lines.append(f"- [{checked}] {node} / `{link}`: migrated Lite task")
    memory_status = "written"
    plan_tail = f"""### Loop Contract

Not applicable (Linear).

### Loop State

Not applicable.

### Memory Sync

| Type | Status | Source | memory.md location | Updated |
|---|---|---|---|---|
| Plan upgrade | {memory_status} | {change_id} | memory.md | {today} |

### Task List

{chr(10).join(task_lines)}

### Checkpoints

| Checkpoint | Position | Verification requirements | Human review |
|---|---|---|---|
| CP-001 | Next boundary | <tests and acceptance evidence> | yes |

## Optional State

- Parallelization: None until shared contracts are clear.
- Risks: None identified.
- Open questions: None."""
    text = insert_before(text, h2_line(text, "Current Status"), plan_tail)
    if not re.search(r"^##(?:\s+\d+\.)?\s+Update Protocol\s*$", text, re.MULTILINE):
        text = text.rstrip() + """

## Update Protocol

- Keep current state here; write history and durable findings to `memory.md`.
- Keep atomic execution state in task packages.
- Run strict validation before execution, handoff, or completion.
"""
    return text


def upgrade_task(text: str, today: str, change_id: str) -> str:
    if "- Plan mode: `Linear`" not in text:
        raise UpgradeError("Lite task is not Linear or lacks Plan mode")
    if "- Loop budget:" not in text:
        text = insert_after_line(text, "- Plan mode: `Linear`", "- Loop budget: `not applicable`")
    if "- Context refs:" not in text:
        plan_node = next(
            (line for line in text.splitlines() if line.startswith("- Plan node:")),
            None,
        )
        if plan_node is None:
            raise UpgradeError("Lite task is missing Plan node")
        text = insert_after_line(
            text,
            plan_node,
            "- Context refs: `None`\n- Preference refs: `None`",
        )
    if "- Created:" not in text:
        owner = next((line for line in text.splitlines() if line.startswith("- Owner:")), None)
        if owner is None:
            raise UpgradeError("Lite task is missing Owner")
        text = insert_after_line(text, owner, f"- Created: `{today}`")
    dependencies = next(
        (line for line in text.splitlines() if line.startswith("**Dependencies:**")),
        None,
    )
    if dependencies is None:
        raise UpgradeError("Lite task is missing Dependencies")
    if "**Context/Refs:**" not in text:
        text = text.replace(
            dependencies,
            dependencies + "\n\n**Context/Refs:** None\n\n**Preference refs:** None",
            1,
        )

    status = metadata_value(text, "Status")
    verification_status = "完成" if status in {"待验收", "完成"} else "待验证"
    verification_evidence = (
        "retained Lite verification evidence"
        if verification_status == "完成"
        else "pending"
    )
    if verification_status == "完成":
        verification = f"""| Check | Covers | Method/command | Pass condition | Status | Evidence |
|---|---|---|---|---|---|
| V-001 | N-001 | retained Lite verification checklist | Lite verification remains satisfied | `完成` | {verification_evidence} |"""
    else:
        verification = (
            "Add `V-001` rows before `待验收` or `完成`; keep planned checks "
            "in the atomic plan until then."
        )
    extra = f"""## Verification Matrix

{verification}

## Checkpoint

- ID: `CP-001`
- Covers: `N-001`
- Requirement: acceptance evidence
- Human review: yes

## Current Loop Attempt

Not applicable (Linear).

## Latest Execution Snapshot

- Latest action: Profile upgrade
- Latest result: Lite content retained
- Evidence: {change_id}
- Next: current Lite next step

## Escalation

- Stop when a locked constraint or acceptance criterion must change.

## Risks and Rollback

None introduced by the profile upgrade; retain existing task risks.
"""
    return insert_before(text, "## Standing Checklist", extra)


def next_change_id(text: str) -> str:
    numbers = [int(value) for value in re.findall(r"\bCHG-(\d{3})\b", text)]
    return f"CHG-{max(numbers, default=0) + 1:03d}"


def upgrade_memory(text: str | None, title: str, today: str) -> tuple[str, str]:
    if text is None:
        text = render_memory(title, today)
    if markdown_heading_section(text, "Decisions") is not None:
        decision_id = next_decision_id(text)
        decisions = markdown_heading_section(text, "Decisions") or ""
        entry = (
            f"{decision_id}: Upgraded Lite to Full because durable task packages were "
            f"needed. Evidence: profile migration on {today}."
        )
        body = entry if decisions.strip() == "None yet." else f"{decisions.strip()}\n\n{entry}"
        return replace_h2_body(text, "Decisions", body), decision_id
    change_id = next_change_id(text)
    note = (
        f"Upgrade {change_id} ({today}): changed Profile from Lite to Full; "
        "preserved Lite state and added Full control sections."
    )
    return insert_before(text, h2_line(text, "Run Logs"), note), change_id


def validate_candidate(
    program: str,
    tasks: dict[Path, str],
    memory: str,
    gitignore: str,
) -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory) / "project"
        (root / "tasks").mkdir(parents=True)
        (root / "program.md").write_text(program, encoding="utf-8")
        (root / "memory.md").write_text(memory, encoding="utf-8")
        (root / ".gitignore").write_text(gitignore, encoding="utf-8")
        for source, content in tasks.items():
            (root / "tasks" / source.name).write_text(content, encoding="utf-8")
        validate_project(root)


def apply_atomically(changes: dict[Path, str]) -> None:
    temporary: dict[Path, Path] = {}
    originals: dict[Path, str | None] = {}
    created_directories: list[Path] = []
    try:
        for path, content in changes.items():
            if not path.parent.exists():
                path.parent.mkdir(parents=True)
                created_directories.append(path.parent)
            temp_path = path.with_name(path.name + ".plan-skill-upgrade.tmp")
            if temp_path.exists():
                raise UpgradeError(f"temporary upgrade file already exists: {temp_path}")
            temp_path.write_text(content, encoding="utf-8")
            temporary[path] = temp_path
            originals[path] = path.read_text(encoding="utf-8") if path.exists() else None
        for path, temp_path in temporary.items():
            temp_path.replace(path)
    except Exception:
        for path, original in originals.items():
            if original is None:
                if path.exists():
                    path.unlink()
            else:
                path.write_text(original, encoding="utf-8")
        for directory in reversed(created_directories):
            try:
                directory.rmdir()
            except OSError:
                pass
        raise
    finally:
        for temp_path in temporary.values():
            if temp_path.exists():
                temp_path.unlink()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Upgrade a structurally valid Lite plan to Full while preserving content."
    )
    parser.add_argument("root", help="Lite project root")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate and report the upgrade without writing files",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    root = Path(args.root).resolve()
    try:
        program_path = root / "program.md"
        if not program_path.is_file():
            raise UpgradeError(f"missing program.md: {program_path}")
        program_text = program_path.read_text(encoding="utf-8")
        profile = metadata_value(program_text, "Profile")
        if profile == "Full":
            raise UpgradeError("plan is already Full")
        if profile != "Lite":
            raise UpgradeError(f"plan Profile must be Lite, got {profile!r}")
        validate_project(root)
        task_paths = sorted((root / "tasks").glob("TASK-*.md"))
        title_match = re.search(r"^#\s+Program:\s*(.+?)\s*$", program_text, re.MULTILINE)
        if title_match is None:
            raise UpgradeError("program.md has no project title")
        title = title_match.group(1)
        today = date.today().isoformat()
        memory_path = root / "memory.md"
        memory_text = memory_path.read_text(encoding="utf-8") if memory_path.exists() else None
        gitignore_path = root / ".gitignore"
        gitignore = (
            gitignore_path.read_text(encoding="utf-8")
            if gitignore_path.exists()
            else ""
        )
        if task_paths:
            upgraded_memory, change_id = upgrade_memory(memory_text, title, today)
            upgraded_program = upgrade_program(program_text, today, change_id)
            upgraded_tasks = {
                path: upgrade_task(path.read_text(encoding="utf-8"), today, change_id)
                for path in task_paths
            }
        else:
            (
                upgraded_program,
                generated_tasks,
                upgraded_memory,
                change_id,
            ) = upgrade_inline_lite(program_text, memory_text, today)
            upgraded_tasks = {
                root / "tasks" / relative.name: content
                for relative, content in generated_tasks.items()
            }
        validate_candidate(upgraded_program, upgraded_tasks, upgraded_memory, gitignore)

        if args.dry_run:
            print(
                f"Would upgrade {root}: program.md, {len(upgraded_tasks)} task package(s), "
                "and memory.md"
            )
            return 0
        changes = {program_path: upgraded_program, memory_path: upgraded_memory}
        changes.update(upgraded_tasks)
        apply_atomically(changes)
    except (UpgradeError, OSError, UnicodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print(f"Upgraded Lite plan to Full at {root}")
    print(f"Prepared {len(upgraded_tasks)} task package(s); recorded {change_id} in memory.md")
    print("Next: fill Full-only <...> fields and run strict validation.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
