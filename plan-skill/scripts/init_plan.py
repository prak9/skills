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


def render_lite_program(title: str, owner: str, today: str) -> str:
    text = (ASSETS / "program-lite.template.md").read_text(encoding="utf-8")
    replacements = {
        "# Program: <Project Name>": f"# Program: {title}",
        "- Overall status: `<待开始 / 进行中 / 阻塞 / 待验收 / 完成 / 已取消 — choose one>`": "- Overall status: `待开始`",
        "- Owner: `<name or role>`": f"- Owner: `{owner}`",
        "- Last updated: `YYYY-MM-DD`": f"- Last updated: `{today}`",
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
    if profile != "full":
        raise InitError("Lite plans keep execution nodes in program.md; no task is initialized")
    template = "task-full-starter.template.md"
    text = (ASSETS / template).read_text(encoding="utf-8")
    task_id = "-".join(task_stem.split("-")[:2])
    text = replace_required(text, "# TASK-001:", f"# {task_id}:")
    text = replace_required(text, "<Short descriptive title>", title)
    text = replace_required(text, "<owner>", owner)
    text = text.replace("YYYY-MM-DD", today)
    return text


def render_memory(title: str, today: str) -> str:
    text = (ASSETS / "memory-starter.template.md").read_text(encoding="utf-8")
    text = replace_required(text, "# Memory: <Project Name>", f"# Memory: {title}")
    return text.replace("`YYYY-MM-DD`", f"`{today}`")


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
        root = Path(args.root).resolve()
        if root.exists() and not root.is_dir():
            raise InitError(f"project root is not a directory: {root}")
        tasks_dir = root / "tasks"
        if args.profile == "full" and tasks_dir.exists() and not tasks_dir.is_dir():
            raise InitError(f"tasks path is not a directory: {tasks_dir}")
        task_stem = ""
        task_path: Path | None = None
        if args.profile == "full":
            slug = validate_slug(args.slug if args.slug is not None else slugify(title))
            task_stem = f"TASK-001-{slug}"
            task_path = root / "tasks" / f"{task_stem}.md"
        candidates = [root / "program.md", root / "memory.md"]
        if task_path is not None:
            candidates.append(task_path)
        if args.profile == "full" and tasks_dir.exists():
            candidates.extend(sorted(tasks_dir.glob("TASK-*.md")))
        existing = sorted({path for path in candidates if path.exists()})
        if existing:
            raise InitError(
                "Refusing to overwrite existing plan files: "
                + ", ".join(str(path) for path in existing)
            )

        today = date.today().isoformat()
        if args.profile == "lite":
            program = render_lite_program(title, owner, today)
            task = None
        else:
            program = render_full_program(title, task_stem, owner, today)
            task = render_task(args.profile, title, task_stem, owner, today)
        memory = render_memory(title, today) if args.profile == "full" else None

        root.mkdir(parents=True, exist_ok=True)
        (root / "program.md").write_text(program, encoding="utf-8")
        if task is not None:
            assert task_path is not None
            task_path.parent.mkdir(parents=True, exist_ok=True)
            task_path.write_text(task, encoding="utf-8")
        if memory is not None:
            (root / "memory.md").write_text(memory, encoding="utf-8")
    except (InitError, OSError, UnicodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print(f"Created {args.profile.capitalize()} plan at {root}")
    if args.profile == "full":
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
