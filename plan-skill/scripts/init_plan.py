#!/usr/bin/env python3
"""Create a safe first plan-skill scaffold from the bundled templates."""

from __future__ import annotations

import argparse
import re
import shlex
import sys
import unicodedata
from datetime import date
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
ASSETS = SKILL_ROOT / "assets"
OUTPUT_IGNORE_RULE = "/tasks/output/"


class InitError(RuntimeError):
    pass


def slugify(value: str) -> str:
    ascii_value = (
        unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    )
    return re.sub(r"[^a-z0-9]+", "-", ascii_value.lower()).strip("-") or "task"


def validate_slug(value: str) -> str:
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", value):
        raise InitError(
            "slug must contain lowercase letters, digits, and single hyphens only"
        )
    return value


def replace_required(text: str, old: str, new: str) -> str:
    if old not in text:
        raise InitError(f"bundled template changed; missing expected text: {old}")
    return text.replace(old, new)


def render_lite_program(title: str, task_stem: str, owner: str, today: str) -> str:
    text = (ASSETS / "program-lite.template.md").read_text(encoding="utf-8")
    replacements = {
        "# Program: <Project Name>": f"# Program: {title}",
        "- Overall status: `<待开始 / 进行中 / 阻塞 / 待验收 / 完成 / 已取消 — choose one>`": "- Overall status: `待开始`",
        "- Memory: `memory.md / None`": "- Memory: `None`",
        "- Active task package: `tasks/TASK-NNN-<slug>.md / None`": f"- Active task package: `tasks/{task_stem}.md`",
        "- Active plan node: `NODE-NNN / None`": "- Active plan node: `NODE-001`",
        "- Latest evidence: `<V-NNN, RUN-NNN, command output, or None>`": "- Latest evidence: `None`",
        "- Owner: `<name or role>`": f"- Owner: `{owner}`",
        "- Last updated: `YYYY-MM-DD`": f"- Last updated: `{today}`",
        "TASK-001-short-slug": task_stem,
        "`Small / Medium — choose one`": "`Small`",
        "<evidence or None>": "None",
        "`YYYY-MM-DD`": f"`{today}`",
        "- Current blocker: <None, or blocker and unblock condition>": "- Current blocker: None",
        "- Next step: <task package and atomic node>": "- Next step: TASK-001 / N-001",
        "- Next human decision: <None, or decision point>": "- Next human decision: None",
        "- Pending memory write: <None, or durable finding/run summary to record>": "- Pending memory write: None",
    }
    for old, new in replacements.items():
        text = replace_required(text, old, new)
    return text


def render_full_program(title: str, task_stem: str, owner: str, today: str) -> str:
    text = (ASSETS / "program-full-starter.template.md").read_text(encoding="utf-8")
    replacements = {
        "# Program: <Project Name>": f"# Program: {title}",
        "TASK-001-short-slug": task_stem,
        "<owner>": owner,
        "YYYY-MM-DD": today,
    }
    for old, new in replacements.items():
        text = replace_required(text, old, new)
    return text


def render_task(
    profile: str,
    title: str,
    task_stem: str,
    owner: str,
    today: str,
) -> str:
    template = (
        "task-lite.template.md"
        if profile == "lite"
        else "task-full-starter.template.md"
    )
    text = (ASSETS / template).read_text(encoding="utf-8")
    if profile == "lite":
        text = replace_required(text, "TASK-NNN-<slug>", task_stem)
        text = text.replace("TASK-NNN", "TASK-001").replace("NODE-NNN", "NODE-001")
        text = text.replace("<Short descriptive title>", title).replace("## Task N:", "## Task 1:")
        text = replace_required(
            text,
            "- Status: `<待开始 / 进行中 / 阻塞 / 待验证 / 待验收 / 完成 / 已取消 — choose one>`",
            "- Status: `待开始`",
        )
        text = replace_required(text, "- Owner: `<person, role, or AI>`", f"- Owner: `{owner}`")
        text = replace_required(text, "- Updated: `YYYY-MM-DD`", f"- Updated: `{today}`")
        text = replace_required(text, "`Small / Medium — choose one`", "`Small`")
    else:
        text = replace_required(text, "TASK-001-short-slug", task_stem)
        text = replace_required(text, "<Short descriptive title>", title)
        text = replace_required(text, "<owner>", owner)
        text = text.replace("YYYY-MM-DD", today)
    return text


def render_memory(title: str, today: str) -> str:
    text = (ASSETS / "memory-starter.template.md").read_text(encoding="utf-8")
    text = replace_required(text, "# Memory: <Project Name>", f"# Memory: {title}")
    return text.replace("`YYYY-MM-DD`", f"`{today}`")


def update_gitignore(root: Path) -> None:
    path = root / ".gitignore"
    if path.exists() and not path.is_file():
        raise InitError(f"cannot update non-file: {path}")
    existing = path.read_text(encoding="utf-8") if path.exists() else ""
    rules = {line.strip() for line in existing.splitlines()}
    if rules & {OUTPUT_IGNORE_RULE, "tasks/output/"}:
        return
    prefix = "" if not existing or existing.endswith("\n") else "\n"
    path.write_text(f"{existing}{prefix}{OUTPUT_IGNORE_RULE}\n", encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Initialize a linked plan-skill program and first task package."
    )
    parser.add_argument("root", help="Project root to initialize")
    parser.add_argument("--title", required=True, help="Project and first-task title")
    parser.add_argument(
        "--profile",
        choices=("lite", "full"),
        default="lite",
        help="Plan profile; default: lite",
    )
    parser.add_argument("--slug", help="Task slug; derived from title when omitted")
    parser.add_argument("--owner", default="AI", help="Owner name or role; default: AI")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    title = args.title.strip()
    owner = args.owner.strip()
    if not title or not owner:
        print("ERROR: title and owner must not be blank", file=sys.stderr)
        return 2
    try:
        slug = validate_slug(args.slug if args.slug is not None else slugify(title))
        root = Path(args.root).resolve()
        if root.exists() and not root.is_dir():
            raise InitError(f"project root is not a directory: {root}")
        gitignore = root / ".gitignore"
        if gitignore.exists() and not gitignore.is_file():
            raise InitError(f"cannot update non-file: {gitignore}")
        tasks_dir = root / "tasks"
        if tasks_dir.exists() and not tasks_dir.is_dir():
            raise InitError(f"tasks path is not a directory: {tasks_dir}")
        task_stem = f"TASK-001-{slug}"
        task_path = root / "tasks" / f"{task_stem}.md"
        candidates = [root / "program.md", root / "memory.md", task_path]
        if tasks_dir.exists():
            candidates.extend(sorted(tasks_dir.glob("TASK-*.md")))
        existing = sorted({path for path in candidates if path.exists()})
        if existing:
            raise InitError(
                "Refusing to overwrite existing plan files: "
                + ", ".join(str(path) for path in existing)
            )

        today = date.today().isoformat()
        if args.profile == "lite":
            program = render_lite_program(title, task_stem, owner, today)
        else:
            program = render_full_program(title, task_stem, owner, today)
        task = render_task(args.profile, title, task_stem, owner, today)
        memory = render_memory(title, today) if args.profile == "full" else None

        (root / "tasks" / "output").mkdir(parents=True, exist_ok=True)
        (root / "program.md").write_text(program, encoding="utf-8")
        task_path.write_text(task, encoding="utf-8")
        if memory is not None:
            (root / "memory.md").write_text(memory, encoding="utf-8")
        update_gitignore(root)
    except (InitError, OSError, UnicodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print(f"Created {args.profile.capitalize()} plan at {root}")
    print(f"First task: tasks/{task_stem}.md")
    validator = SKILL_ROOT / "scripts" / "validate_plan.py"
    command = " ".join(
        shlex.quote(str(part))
        for part in (sys.executable, validator, "--strict", root)
    )
    print("Next: replace remaining <...> fields, then run:")
    print(command)
    return 0


if __name__ == "__main__":
    sys.exit(main())
