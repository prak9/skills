#!/usr/bin/env python3
"""Search and inspect local coding-agent session transcripts.

Supports Antigravity CLI, Codex, and Claude Code JSONL transcripts.
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import sys
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


@dataclass
class Turn:
    role: str
    timestamp: str
    text: str


@dataclass
class SessionHit:
    source: str
    path: str
    session_id: str
    mtime_iso: str
    cwd: str
    matched_turns: int
    preview: str


def _default_roots() -> dict[str, list[str]]:
    home = Path.home()
    return {
        "antigravity": [
            str(home / ".gemini" / "antigravity-cli" / "brain" / "*" / ".system_generated" / "logs" / "transcript.jsonl")
        ],
        "codex": [
            str(home / ".codex" / "sessions" / "*" / "*" / "*" / "*.jsonl")
        ],
        "claude": [
            str(home / ".claude" / "projects" / "*" / "*.jsonl")
        ],
    }


def _extract_text_blocks(content: object) -> str:
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict):
                txt = item.get("text")
                if isinstance(txt, str) and txt.strip():
                    parts.append(txt.strip())
        return "\n".join(parts).strip()
    return ""


def detect_source(path: Path) -> str:
    s = str(path)
    if "antigravity-cli" in s or path.name == "transcript.jsonl":
        return "antigravity"
    if ".codex" in s or path.name.startswith("rollout-"):
        return "codex"
    if ".claude" in s:
        return "claude"
    return "unknown"


def parse_transcript(path: Path, source: str | None = None) -> tuple[str, str, list[Turn]]:
    """Return (session_id, cwd, turns) from a transcript JSONL file."""
    src = source or detect_source(path)
    session_id = path.parent.parent.parent.name if src == "antigravity" else path.stem
    cwd = ""
    turns: list[Turn] = []

    with path.open("r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            if not isinstance(obj, dict):
                continue

            if src == "antigravity":
                t = obj.get("type")
                if t in ("USER_INPUT", "PLANNER_RESPONSE"):
                    text = _extract_text_blocks(obj.get("content"))
                    if text:
                        role = "user" if t == "USER_INPUT" else "assistant"
                        turns.append(Turn(role=role, timestamp=str(obj.get("created_at", "")), text=text))
            elif src == "codex":
                t = obj.get("type")
                payload = obj.get("payload")
                if t == "session_meta" and isinstance(payload, dict):
                    cwd = str(payload.get("cwd", cwd) or cwd)
                    if payload.get("id"):
                        session_id = str(payload["id"])
                elif t == "response_item" and isinstance(payload, dict) and payload.get("type") == "message":
                    role = str(payload.get("role", ""))
                    if role in ("user", "assistant"):
                        text = _extract_text_blocks(payload.get("content"))
                        if text:
                            turns.append(Turn(role=role, timestamp=str(obj.get("timestamp", "")), text=text))
            elif src == "claude":
                t = obj.get("type")
                if not cwd and obj.get("cwd"):
                    cwd = str(obj["cwd"])
                if obj.get("sessionId"):
                    session_id = str(obj["sessionId"])
                if t in ("user", "assistant"):
                    msg = obj.get("message")
                    content = msg.get("content") if isinstance(msg, dict) else obj.get("content")
                    text = _extract_text_blocks(content)
                    if text:
                        turns.append(Turn(role=t, timestamp=str(obj.get("timestamp", "")), text=text))

    return session_id, cwd, turns


def iter_candidate_files(sources: Iterable[str], days: float | None, roots: dict[str, list[str]] | None = None) -> list[tuple[str, Path, float]]:
    root_map = roots or _default_roots()
    cutoff = (time.time() - days * 86400.0) if days is not None else None
    found: list[tuple[str, Path, float]] = []

    for src in sources:
        for pattern in root_map.get(src, []):
            for match in glob.glob(pattern):
                p = Path(match)
                try:
                    mtime = p.stat().st_mtime
                except OSError:
                    continue
                if cutoff is not None and mtime < cutoff:
                    continue
                found.append((src, p, mtime))

    found.sort(key=lambda item: item[2], reverse=True)
    return found


def search_sessions(
    *,
    sources: list[str],
    days: float | None,
    query: str | None,
    limit: int,
    roots: dict[str, list[str]] | None = None,
) -> list[SessionHit]:
    terms = [t.lower() for t in (query or "").split() if t.strip()]
    hits: list[SessionHit] = []

    for src, path, mtime in iter_candidate_files(sources, days, roots=roots):
        session_id, cwd, turns = parse_transcript(path, source=src)
        if not turns:
            continue

        if terms:
            matched = [t for t in turns if all(term in t.text.lower() for term in terms)]
            if not matched:
                joined = "\n".join(t.text.lower() for t in turns)
                if not all(term in joined for term in terms):
                    continue
                matched = [t for t in turns if any(term in t.text.lower() for term in terms)]
            preview_turn = matched[-1]
            match_count = len(matched)
        else:
            user_turns = [t for t in turns if t.role == "user"]
            preview_turn = user_turns[-1] if user_turns else turns[-1]
            match_count = len(turns)

        preview = " ".join(preview_turn.text.split())[:220]
        mtime_iso = datetime.fromtimestamp(mtime, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        hits.append(
            SessionHit(
                source=src,
                path=str(path),
                session_id=session_id,
                mtime_iso=mtime_iso,
                cwd=cwd,
                matched_turns=match_count,
                preview=preview,
            )
        )
        if len(hits) >= limit:
            break

    return hits


def _cmd_search(args: argparse.Namespace) -> int:
    sources = ["antigravity", "codex", "claude"] if args.source == "all" else [args.source]
    hits = search_sessions(sources=sources, days=args.days, query=args.query, limit=args.limit)
    if args.json:
        print(json.dumps({"ok": True, "count": len(hits), "sessions": [asdict(h) for h in hits]}, ensure_ascii=False, indent=2))
    else:
        if not hits:
            print("No matching sessions found. Try widening --days or using fewer --query terms.")
            return 0
        for h in hits:
            cwd_part = f" cwd={h.cwd}" if h.cwd else ""
            print(f"[{h.source}] {h.mtime_iso} id={h.session_id}{cwd_part} matches={h.matched_turns}")
            print(f"  path: {h.path}")
            print(f"  preview: {h.preview}")
    return 0


def _cmd_show(args: argparse.Namespace) -> int:
    path = Path(args.path).expanduser()
    if not path.is_file():
        err = {
            "ok": False,
            "error": "TRANSCRIPT_NOT_FOUND",
            "message": f"Transcript file not found: {path}",
            "next_action": "Run `python3 scripts/recall_sessions.py search --days 7 --json` to list valid paths.",
        }
        if args.json:
            print(json.dumps(err, ensure_ascii=False, indent=2))
        else:
            print(f"ERROR: {err['message']}\nNext: {err['next_action']}", file=sys.stderr)
        return 1

    src = args.source if args.source != "auto" else detect_source(path)
    session_id, cwd, turns = parse_transcript(path, source=src)
    if args.query:
        terms = [t.lower() for t in args.query.split() if t.strip()]
        turns = [t for t in turns if any(term in t.text.lower() for term in terms)]
    if args.max_turns > 0 and len(turns) > args.max_turns:
        turns = turns[-args.max_turns :]

    clipped = [
        Turn(role=t.role, timestamp=t.timestamp, text=t.text[: args.max_chars] + ("..." if len(t.text) > args.max_chars else ""))
        for t in turns
    ]
    if args.json:
        print(
            json.dumps(
                {
                    "ok": True,
                    "source": src,
                    "session_id": session_id,
                    "cwd": cwd,
                    "path": str(path),
                    "turns": [asdict(t) for t in clipped],
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    else:
        print(f"Session: {session_id} ({src}) cwd={cwd or 'unknown'}")
        for t in clipped:
            print(f"\n--- {t.role.upper()} [{t.timestamp}] ---\n{t.text}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="recall_sessions.py",
        description="Search and inspect recent local Antigravity, Codex, and Claude Code session transcripts.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_search = sub.add_parser("search", help="Search recent session transcripts by keywords and age.")
    p_search.add_argument("--source", choices=["all", "antigravity", "codex", "claude"], default="all")
    p_search.add_argument("--days", type=float, default=7.0, help="Look back N days (default: 7).")
    p_search.add_argument("--query", default="", help="Space-separated keywords (case-insensitive).")
    p_search.add_argument("--limit", type=int, default=10, help="Max sessions to return (default: 10).")
    p_search.add_argument("--json", action="store_true", help="Emit machine-readable JSON on stdout.")
    p_search.set_defaults(func=_cmd_search)

    p_show = sub.add_parser("show", help="Extract bounded turns from a specific transcript JSONL file.")
    p_show.add_argument("path", help="Path to transcript JSONL file.")
    p_show.add_argument("--source", choices=["auto", "antigravity", "codex", "claude"], default="auto")
    p_show.add_argument("--query", default="", help="Optional keyword filter for turns.")
    p_show.add_argument("--max-turns", type=int, default=20, help="Keep last N turns (default: 20).")
    p_show.add_argument("--max-chars", type=int, default=1200, help="Truncate each turn to N chars (default: 1200).")
    p_show.add_argument("--json", action="store_true", help="Emit machine-readable JSON on stdout.")
    p_show.set_defaults(func=_cmd_show)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
