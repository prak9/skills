from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "recall_sessions.py"
sys.path.insert(0, str(SCRIPT.parent))

import recall_sessions  # noqa: E402


def _write_jsonl(path: Path, rows: list[dict]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8")
    return path


def test_parse_all_three_formats_and_search(tmp_path: Path) -> None:
    ag_path = _write_jsonl(
        tmp_path / "antigravity" / "conv-123" / ".system_generated" / "logs" / "transcript.jsonl",
        [
            {"type": "USER_INPUT", "created_at": "2026-11-20T10:00:00Z", "content": "Fix virtualization jitter"},
            {"type": "PLANNER_RESPONSE", "created_at": "2026-11-20T10:01:00Z", "content": "Measured layout shift in list renderer."},
        ],
    )
    codex_path = _write_jsonl(
        tmp_path / "codex" / "2026" / "11" / "20" / "rollout-abc.jsonl",
        [
            {"type": "session_meta", "payload": {"id": "codex-1", "cwd": "/data/code/app"}},
            {
                "type": "response_item",
                "timestamp": "2026-11-20T11:00:00Z",
                "payload": {"type": "message", "role": "user", "content": [{"type": "input_text", "text": "Refactor webhook rate limiter"}]},
            },
        ],
    )
    claude_path = _write_jsonl(
        tmp_path / "claude" / "-data-code-app" / "sess-9.jsonl",
        [
            {
                "type": "user",
                "sessionId": "claude-9",
                "cwd": "/data/code/app",
                "timestamp": "2026-11-20T12:00:00Z",
                "message": {"content": "Check Bayesian likelihood ratio update"},
            },
        ],
    )

    roots = {
        "antigravity": [str(ag_path)],
        "codex": [str(codex_path)],
        "claude": [str(claude_path)],
    }

    all_hits = recall_sessions.search_sessions(
        sources=["antigravity", "codex", "claude"], days=7, query=None, limit=10, roots=roots
    )
    assert len(all_hits) == 3
    assert {h.source for h in all_hits} == {"antigravity", "codex", "claude"}

    jitter_hits = recall_sessions.search_sessions(
        sources=["antigravity", "codex", "claude"], days=7, query="virtualization jitter", limit=10, roots=roots
    )
    assert len(jitter_hits) == 1
    assert jitter_hits[0].source == "antigravity"
    assert jitter_hits[0].session_id == "conv-123"


def test_cli_show_json_and_missing_file_error(tmp_path: Path) -> None:
    sample = _write_jsonl(
        tmp_path / "transcript.jsonl",
        [
            {"type": "USER_INPUT", "created_at": "2026-11-21T01:00:00Z", "content": "Hello recall"},
            {"type": "PLANNER_RESPONSE", "created_at": "2026-11-21T01:00:05Z", "content": "Found context"},
        ],
    )
    res = subprocess.run(
        [sys.executable, str(SCRIPT), "show", str(sample), "--json"],
        capture_output=True,
        text=True,
        check=True,
    )
    payload = json.loads(res.stdout)
    assert payload["ok"] is True
    assert len(payload["turns"]) == 2

    missing = subprocess.run(
        [sys.executable, str(SCRIPT), "show", str(tmp_path / "nope.jsonl"), "--json"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert missing.returncode == 1
    err = json.loads(missing.stdout)
    assert err["ok"] is False
    assert err["error"] == "TRANSCRIPT_NOT_FOUND"
    assert "search" in err["next_action"]
