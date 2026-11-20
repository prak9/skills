#!/usr/bin/env python3
"""Lossless automatic slimming and memory indexing for plan-skill states."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path
from typing import Any

from plan_markdown import metadata_value, norm_cell, read_text, split_markdown_table_row

DEFAULT_MAX_LINES = 300
DEFAULT_KEEP_BANNERS = 3
DEFAULT_KEEP_TERMINAL_ROWS = 5
DEFAULT_MEMORY_INDEX_LINES = 500
DEFAULT_MEMORY_INDEX_BYTES = 50_000

TERMINAL_STATUSES = {
    "完成",
    "已取消",
    "done",
    "completed",
    "cancelled",
    "canceled",
    "park",
    "parked",
    "superseded",
    "archived",
}

PROTECTED_H2_TITLES = {
    "outcome",
    "current status",
    "当前研究",
    "队列纪律",
    "constraints",
    "constraints and decisions",
    "acceptance",
    "acceptance criteria",
    "plan",
    "node status",
    "node index",
    "loop contract",
    "loop state",
    "checkpoints",
    "update protocol",
    "memory sync",
    "12. memory sync",
    "concept refinement",
    "execution readiness gate",
    "problem definition",
    "context",
    "context and references",
    "preferences and tradeoffs",
    "goals and metrics",
    "strategy",
    "decisions",
    "dependency and slicing strategy",
    "exploration and hypothesis validation",
    "implementation plan",
    "6. implementation plan",
    "archive index",
}

HISTORICAL_H2_PATTERNS = [
    r"历史调度记录",
    r"（归档",
    r"\(archived?\)",
    r"^historical\b",
    r"\bcompleted\b.*\brecord\b",
    r"^deferred\s+prior\b",
    r"^\d{4}-\d{2}-\d{2}\s+",
    r"^当前状态更新[：:]\s*\d{4}-\d{2}-\d{2}",
    r"权威接力",
    r"supersedes\b",
]

MEMORY_ID_RE = re.compile(r"\b((?:F|D|R|RUN|K|CHG|HIST|Q|PL)-\d{2,4})\b")


class SlimError(RuntimeError):
    pass


ARCHIVE_BANNER_PREFIX = "> 历史状态播报"


def _is_archive_banner(block: list[str]) -> bool:
    return bool(block) and block[0].lstrip().startswith(ARCHIVE_BANNER_PREFIX)


def _split_leading_banners(lines: list[str]) -> tuple[list[list[str]], list[str], int]:
    """Return (blockquote_blocks, stray_non_banner_lines, first_h1_index) before the first H1."""
    first_h1 = -1
    for idx, line in enumerate(lines):
        if re.match(r"^#\s+", line):
            first_h1 = idx
            break
    if first_h1 <= 0:
        return [], [], first_h1

    prefix = lines[:first_h1]
    blocks: list[list[str]] = []
    stray: list[str] = []
    current: list[str] = []
    for line in prefix:
        if line.lstrip().startswith(">"):
            current.append(line)
        elif line.strip() == "":
            if current:
                blocks.append(current)
                current = []
        else:
            if current:
                blocks.append(current)
                current = []
            stray.append(line)
    if current:
        blocks.append(current)
    return blocks, stray, first_h1


def _is_historical_h2(title: str) -> bool:
    normalized = title.strip().lower()
    if normalized in PROTECTED_H2_TITLES:
        return False
    return any(
        re.search(pattern, title.strip(), flags=re.IGNORECASE)
        for pattern in HISTORICAL_H2_PATTERNS
    )


def _split_h2_sections(lines: list[str]) -> tuple[list[str], list[tuple[str, list[str]]]]:
    """Split markdown lines into (preamble_lines, [(h2_title, section_lines), ...])."""
    preamble: list[str] = []
    sections: list[tuple[str, list[str]]] = []
    current_title: str | None = None
    current_lines: list[str] = []
    in_fence = False

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
        if not in_fence:
            match = re.match(r"^##\s+(.+?)\s*$", line)
            if match:
                if current_title is None:
                    preamble = current_lines
                else:
                    sections.append((current_title, current_lines))
                current_title = match.group(1).strip()
                current_lines = [line]
                continue
        current_lines.append(line)

    if current_title is None:
        preamble = current_lines
    else:
        sections.append((current_title, current_lines))
    return preamble, sections


def _slim_tables_in_lines(
    lines: list[str],
    keep_terminal_rows: int,
    archive_rel_path: str,
) -> tuple[list[str], list[tuple[str, str, list[str]]]]:
    """Archive older terminal rows in status tables, preserving non-terminal + recent rows.

    Returns (new_lines, [(header_line, sep_line, archived_rows), ...]).
    """
    out: list[str] = []
    archived_tables: list[tuple[str, str, list[str]]] = []
    idx = 0
    total = len(lines)
    in_fence = False

    while idx < total:
        line = lines[idx]
        stripped = line.strip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
            out.append(line)
            idx += 1
            continue

        if (
            not in_fence
            and stripped.startswith("|")
            and stripped.endswith("|")
            and idx + 1 < total
        ):
            sep_line = lines[idx + 1]
            sep_stripped = sep_line.strip()
            if (
                sep_stripped.startswith("|")
                and sep_stripped.endswith("|")
                and all(
                    re.fullmatch(r":?-+:?", cell)
                    for cell in split_markdown_table_row(sep_stripped)
                )
            ):
                header_cells = [
                    norm_cell(c).lower() for c in split_markdown_table_row(stripped)
                ]
                status_col = None
                for col_idx, col_name in enumerate(header_cells):
                    if col_name in {"status", "状态"}:
                        status_col = col_idx
                        break

                table_end = idx + 2
                data_rows: list[str] = []
                while table_end < total:
                    row_stripped = lines[table_end].strip()
                    if (
                        row_stripped.startswith("|")
                        and row_stripped.endswith("|")
                        and len(row_stripped) > 2
                    ):
                        data_rows.append(lines[table_end])
                        table_end += 1
                    else:
                        break

                if status_col is not None and data_rows:
                    terminal_indices: list[int] = []
                    for r_idx, row in enumerate(data_rows):
                        cells = split_markdown_table_row(row.strip())
                        if status_col < len(cells):
                            status_val = norm_cell(cells[status_col]).lower()
                            if status_val in TERMINAL_STATUSES:
                                terminal_indices.append(r_idx)

                    if len(terminal_indices) > keep_terminal_rows:
                        archive_count = len(terminal_indices) - keep_terminal_rows
                        to_archive_idx = set(terminal_indices[:archive_count])
                        archived_rows = [
                            row
                            for r_idx, row in enumerate(data_rows)
                            if r_idx in to_archive_idx
                        ]
                        kept_rows = [
                            row
                            for r_idx, row in enumerate(data_rows)
                            if r_idx not in to_archive_idx
                        ]
                        out.append(line)
                        out.append(sep_line)
                        out.extend(kept_rows)
                        out.append(
                            f"\n> 已归档 {len(archived_rows)} 条历史终态行至 "
                            f"[{archive_rel_path}]({archive_rel_path})。"
                        )
                        archived_tables.append((line, sep_line, archived_rows))
                        idx = table_end
                        continue

                out.extend(lines[idx:table_end])
                idx = table_end
                continue

        out.append(line)
        idx += 1

    return out, archived_tables


def _update_existing_clean_metadata(text: str, today: str, archive_rel_path: str) -> str:
    """Update Clean state / Last clean ONLY if the plan already opted into them."""
    if metadata_value(text, "Clean state") is None and metadata_value(text, "Last clean") is None:
        return text
    updated = re.sub(
        r"^(-\s*Clean state[：:]\s*).*$",
        r"\1`Not due`",
        text,
        flags=re.MULTILINE | re.IGNORECASE,
    )
    updated = re.sub(
        r"^(-\s*Last clean[：:]\s*).*$",
        rf"\1`{today}` ({archive_rel_path})",
        updated,
        flags=re.MULTILINE | re.IGNORECASE,
    )
    return updated


def build_memory_index(memory_path: Path) -> list[dict[str, Any]]:
    """Extract a lightweight structured JSONL index of headings and stable IDs in memory.md."""
    text = read_text(memory_path)
    entries: list[dict[str, Any]] = []
    seen: set[tuple[str, int]] = set()
    current_heading = ""

    for lineno, raw_line in enumerate(text.splitlines(), start=1):
        line = raw_line.strip()
        if not line:
            continue
        heading_match = re.match(r"^(#{2,3})\s+(.+?)\s*$", line)
        if heading_match:
            current_heading = heading_match.group(2).strip()
            id_match = MEMORY_ID_RE.search(current_heading)
            if id_match:
                entry_id = id_match.group(1)
                key = (entry_id, lineno)
                if key not in seen:
                    seen.add(key)
                    entries.append(
                        {
                            "id": entry_id,
                            "kind": entry_id.split("-")[0],
                            "line": lineno,
                            "heading": current_heading,
                            "summary": current_heading[:180],
                        }
                    )
            continue

        for match in MEMORY_ID_RE.finditer(line):
            entry_id = match.group(1)
            # Only index declaration-like lines (table rows, bullets, bold IDs) to avoid noisy cross-refs
            is_decl = (
                line.startswith("|")
                or line.startswith("-")
                or line.startswith("*")
                or f"**{entry_id}" in line
                or line.startswith(entry_id)
            )
            if not is_decl:
                continue
            key = (entry_id, lineno)
            if key not in seen:
                seen.add(key)
                entries.append(
                    {
                        "id": entry_id,
                        "kind": entry_id.split("-")[0],
                        "line": lineno,
                        "heading": current_heading,
                        "summary": re.sub(r"\s+", " ", line)[:200],
                    }
                )
    return entries


def slim_plan(
    root: Path,
    *,
    dry_run: bool = False,
    max_lines: int = DEFAULT_MAX_LINES,
    keep_banners: int = DEFAULT_KEEP_BANNERS,
    keep_terminal_rows: int = DEFAULT_KEEP_TERMINAL_ROWS,
    archive_dir_name: str = "archive",
    index_memory: bool = False,
    today: str | None = None,
) -> dict[str, Any]:
    program_path = root / "program.md"
    if not program_path.is_file():
        raise SlimError(f"missing program.md: {program_path}")

    today_str = today or date.today().isoformat()
    archive_dir = root / archive_dir_name
    archive_filename = f"program-archive-{today_str}.md"
    archive_path = archive_dir / archive_filename
    archive_rel_path = f"{archive_dir_name}/{archive_filename}"

    original_text = read_text(program_path)
    original_lines = original_text.splitlines()
    before_line_count = len(original_lines)
    before_bytes = len(original_text.encode("utf-8"))

    # 1. Leading status banners before H1 (ignore existing archive-pointer banners)
    banners, stray_prefix, first_h1 = _split_leading_banners(original_lines)
    active_banners = [b for b in banners if not _is_archive_banner(b)]
    existing_archive_banners = [b for b in banners if _is_archive_banner(b)]
    archived_banners: list[list[str]] = []
    if len(active_banners) > keep_banners and first_h1 > 0:
        kept_banners = active_banners[:keep_banners]
        archived_banners = active_banners[keep_banners:]
        rebuilt_prefix: list[str] = []
        for block in kept_banners:
            rebuilt_prefix.extend(block)
            rebuilt_prefix.append("")
        for block in existing_archive_banners:
            rebuilt_prefix.extend(block)
            rebuilt_prefix.append("")
        rebuilt_prefix.append(
            f"{ARCHIVE_BANNER_PREFIX}（{len(archived_banners)} 条）已自动归档至 "
            f"[{archive_rel_path}]({archive_rel_path})。"
        )
        rebuilt_prefix.append("")
        if stray_prefix:
            rebuilt_prefix.extend(stray_prefix)
            rebuilt_prefix.append("")
        working_lines = rebuilt_prefix + original_lines[first_h1:]
    else:
        working_lines = list(original_lines)

    # 2. Historical H2 sections
    preamble, sections = _split_h2_sections(working_lines)
    kept_sections: list[tuple[str, list[str]]] = []
    archived_sections: list[tuple[str, list[str]]] = []
    for title, sec_lines in sections:
        if _is_historical_h2(title):
            archived_sections.append((title, sec_lines))
        else:
            kept_sections.append((title, sec_lines))

    # 3. Terminal rows in Markdown tables inside kept sections (and preamble)
    archived_tables: list[tuple[str, str, list[str]]] = []
    slim_preamble, preamble_tables = _slim_tables_in_lines(
        preamble, keep_terminal_rows, archive_rel_path
    )
    archived_tables.extend(preamble_tables)

    slim_sections: list[tuple[str, list[str]]] = []
    for title, sec_lines in kept_sections:
        new_sec_lines, sec_tables = _slim_tables_in_lines(
            sec_lines, keep_terminal_rows, archive_rel_path
        )
        archived_tables.extend(sec_tables)
        slim_sections.append((title, new_sec_lines))

    # Append or update Archive Index if any H2 sections were archived
    if archived_sections:
        index_bullets = [
            f"- `{today_str}`: 归档 {len(archived_sections)} 个历史章节至 "
            f"[{archive_rel_path}]({archive_rel_path})："
            + " / ".join(title for title, _ in archived_sections)
        ]
        updated_existing_index = False
        for idx, (title, sec_lines) in enumerate(slim_sections):
            if title.strip().lower() == "archive index":
                slim_sections[idx] = (title, sec_lines + index_bullets)
                updated_existing_index = True
                break
        if not updated_existing_index:
            slim_sections.append(
                ("Archive Index", ["## Archive Index", ""] + index_bullets)
            )

    rebuilt_lines = list(slim_preamble)
    for _, sec_lines in slim_sections:
        if rebuilt_lines and rebuilt_lines[-1].strip() != "":
            rebuilt_lines.append("")
        rebuilt_lines.extend(sec_lines)

    new_text = "\n".join(rebuilt_lines).rstrip() + "\n"
    changed_program = bool(archived_banners or archived_sections or archived_tables)
    if changed_program:
        new_text = _update_existing_clean_metadata(new_text, today_str, archive_rel_path)

    after_line_count = len(new_text.splitlines())
    after_bytes = len(new_text.encode("utf-8"))

    # 4. Optional / automatic memory.md indexing
    memory_path = root / "memory.md"
    memory_index_path = archive_dir / "memory-index.jsonl"
    memory_entries: list[dict[str, Any]] = []
    should_index_memory = False
    if memory_path.is_file():
        mem_bytes = memory_path.stat().st_size
        mem_lines = len(read_text(memory_path).splitlines())
        if index_memory or mem_lines > DEFAULT_MEMORY_INDEX_LINES or mem_bytes > DEFAULT_MEMORY_INDEX_BYTES:
            should_index_memory = True
            memory_entries = build_memory_index(memory_path)

    archive_chunks: list[str] = []
    if changed_program:
        archive_chunks.append(f"# Program Archive ({today_str})\n")
        archive_chunks.append(
            f"- Source: `program.md` (before: {before_line_count} lines -> after: {after_line_count} lines)\n"
        )
        if archived_banners:
            archive_chunks.append(f"\n## Archived Leading Status Banners ({len(archived_banners)})\n")
            for block in archived_banners:
                archive_chunks.append("\n".join(block) + "\n")
        if archived_sections:
            archive_chunks.append(f"\n## Archived Historical Sections ({len(archived_sections)})\n")
            for _, sec_lines in archived_sections:
                archive_chunks.append("\n".join(sec_lines).rstrip() + "\n")
        if archived_tables:
            total_rows = sum(len(rows) for _, _, rows in archived_tables)
            archive_chunks.append(f"\n## Archived Terminal Table Rows ({total_rows})\n")
            for header, sep, rows in archived_tables:
                archive_chunks.append(header + "\n" + sep + "\n" + "\n".join(rows) + "\n")

    if not dry_run:
        if changed_program:
            archive_dir.mkdir(parents=True, exist_ok=True)
            archive_body = "\n".join(archive_chunks).rstrip() + "\n"
            if archive_path.exists():
                existing_archive = read_text(archive_path)
                archive_path.write_text(
                    existing_archive.rstrip() + "\n\n---\n\n" + archive_body,
                    encoding="utf-8",
                )
            else:
                archive_path.write_text(archive_body, encoding="utf-8")
            program_path.write_text(new_text, encoding="utf-8")

        if should_index_memory:
            archive_dir.mkdir(parents=True, exist_ok=True)
            jsonl_body = "\n".join(
                json.dumps(entry, ensure_ascii=False) for entry in memory_entries
            )
            memory_index_path.write_text(
                (jsonl_body + "\n") if jsonl_body else "",
                encoding="utf-8",
            )

    return {
        "root": str(root),
        "dry_run": dry_run,
        "changed_program": changed_program,
        "before_lines": before_line_count,
        "after_lines": after_line_count if changed_program else before_line_count,
        "before_bytes": before_bytes,
        "after_bytes": after_bytes if changed_program else before_bytes,
        "exceeds_max_lines_after": (
            (after_line_count if changed_program else before_line_count) > max_lines
        ),
        "archived_banners": len(archived_banners),
        "archived_sections": [title for title, _ in archived_sections],
        "archived_table_rows": sum(len(rows) for _, _, rows in archived_tables),
        "archive_path": str(archive_path) if changed_program else None,
        "memory_indexed": should_index_memory,
        "memory_index_entries": len(memory_entries),
        "memory_index_path": str(memory_index_path) if should_index_memory else None,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Losslessly archive bloated program.md history and build a structured memory.md index."
    )
    parser.add_argument("root", help="Directory containing program.md (and optional memory.md)")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Inspect and report what would be archived without writing files",
    )
    parser.add_argument(
        "--max-lines",
        type=int,
        default=DEFAULT_MAX_LINES,
        help=f"Target line budget for program.md (default: {DEFAULT_MAX_LINES})",
    )
    parser.add_argument(
        "--keep-banners",
        type=int,
        default=DEFAULT_KEEP_BANNERS,
        help=f"Leading status blockquotes to keep at top of program.md (default: {DEFAULT_KEEP_BANNERS})",
    )
    parser.add_argument(
        "--keep-terminal-rows",
        type=int,
        default=DEFAULT_KEEP_TERMINAL_ROWS,
        help=f"Recent terminal status rows to keep in tables (default: {DEFAULT_KEEP_TERMINAL_ROWS})",
    )
    parser.add_argument(
        "--archive-dir",
        default="archive",
        help="Relative archive directory under root (default: archive)",
    )
    parser.add_argument(
        "--index-memory",
        action="store_true",
        help="Force generating archive/memory-index.jsonl even when memory.md is small",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print machine-readable JSON summary",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    root = Path(args.root).resolve()
    try:
        report = slim_plan(
            root,
            dry_run=args.dry_run,
            max_lines=args.max_lines,
            keep_banners=args.keep_banners,
            keep_terminal_rows=args.keep_terminal_rows,
            archive_dir_name=args.archive_dir,
            index_memory=args.index_memory,
        )
    except (SlimError, RuntimeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        mode = "DRY-RUN" if report["dry_run"] else "APPLIED"
        print(f"[{mode}] {report['root']}")
        print(
            f"  program.md: {report['before_lines']} -> {report['after_lines']} lines "
            f"({report['before_bytes']} -> {report['after_bytes']} bytes)"
        )
        print(
            f"  archived: banners={report['archived_banners']}, "
            f"sections={len(report['archived_sections'])}, "
            f"table_rows={report['archived_table_rows']}"
        )
        if report["archive_path"]:
            print(f"  archive file: {report['archive_path']}")
        if report["memory_indexed"]:
            print(
                f"  memory index: {report['memory_index_entries']} entries -> "
                f"{report['memory_index_path']}"
            )
        if report["exceeds_max_lines_after"]:
            print(
                f"  NOTE: program.md still exceeds --max-lines ({args.max_lines}); "
                "manual distillation of large non-historical sections may be needed."
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
