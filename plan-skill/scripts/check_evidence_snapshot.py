#!/usr/bin/env python3
"""Read-only validity check for an explicitly enabled evidence snapshot."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime
from pathlib import Path, PurePosixPath
from typing import Any


SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
INPUT_ROLES = {"source", "test", "config", "data"}


def fail(message: str) -> None:
    print(f"error: {message}", file=sys.stderr)
    raise SystemExit(2)


def load_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        fail(f"snapshot not found: {path}")
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON at line {exc.lineno}, column {exc.colno}: {exc.msg}")
    if not isinstance(data, dict):
        fail("top-level JSON value must be an object")
    return data


def nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def valid_time(value: Any) -> bool:
    if not nonempty(value):
        return False
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return parsed.tzinfo is not None


def digest(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(block)
    return hasher.hexdigest()


def safe_path(root: Path, value: Any) -> tuple[Path | None, str]:
    if not nonempty(value):
        return None, "path must be a non-empty relative path"
    portable = PurePosixPath(value)
    if portable.is_absolute() or ".." in portable.parts:
        return None, "path must remain inside project root"
    candidate = (root / Path(*portable.parts)).resolve()
    try:
        candidate.relative_to(root)
    except ValueError:
        return None, "resolved path escapes project root"
    return candidate, ""


def check_entry(
    entry: Any,
    role: str,
    root: Path,
    checked: list[dict[str, Any]],
    changed: list[dict[str, Any]],
    missing: list[dict[str, Any]],
    uncheckable: list[dict[str, Any]],
) -> None:
    if not isinstance(entry, dict):
        uncheckable.append({"path": "<missing>", "role": role, "reason": "entry must be an object"})
        return
    relative = entry.get("path")
    expected = entry.get("sha256")
    resolved, reason = safe_path(root, relative)
    if resolved is None:
        uncheckable.append({"path": relative, "role": role, "reason": reason})
        return
    if not isinstance(expected, str) or not SHA256_RE.fullmatch(expected):
        uncheckable.append(
            {"path": relative, "role": role, "reason": "sha256 must be 64 lowercase hex characters"}
        )
        return
    if not resolved.exists():
        missing.append({"path": relative, "role": role})
        return
    if not resolved.is_file():
        uncheckable.append({"path": relative, "role": role, "reason": "recorded path is not a file"})
        return
    try:
        actual = digest(resolved)
    except OSError as exc:
        uncheckable.append({"path": relative, "role": role, "reason": str(exc)})
        return
    record = {"path": relative, "role": role, "expected_sha256": expected, "actual_sha256": actual}
    if actual == expected:
        checked.append(record)
    else:
        changed.append(record)


def check(snapshot: dict[str, Any], project_root: Path) -> dict[str, Any]:
    root = project_root.resolve()
    checked: list[dict[str, Any]] = []
    changed: list[dict[str, Any]] = []
    missing: list[dict[str, Any]] = []
    uncheckable: list[dict[str, Any]] = []

    if snapshot.get("schema_version") != 1:
        uncheckable.append(
            {"path": "schema_version", "role": "contract", "reason": "schema_version must be 1"}
        )

    acceptance = snapshot.get("acceptance")
    if not isinstance(acceptance, dict):
        uncheckable.append({"path": "acceptance", "role": "contract", "reason": "acceptance must be an object"})
        acceptance = {}
    for field in ("id", "version", "condition"):
        if not nonempty(acceptance.get(field)):
            uncheckable.append(
                {"path": f"acceptance.{field}", "role": "contract", "reason": "required non-empty string"}
            )
    check_entry(
        acceptance.get("source"),
        "acceptance",
        root,
        checked,
        changed,
        missing,
        uncheckable,
    )

    inputs = snapshot.get("inputs")
    if not isinstance(inputs, list) or not inputs:
        uncheckable.append({"path": "inputs", "role": "contract", "reason": "inputs must be a non-empty array"})
        inputs = []
    for index, entry in enumerate(inputs):
        role = entry.get("role") if isinstance(entry, dict) else None
        if role not in INPUT_ROLES:
            uncheckable.append(
                {
                    "path": f"inputs[{index}].role",
                    "role": "contract",
                    "reason": "role must be source, test, config, or data",
                }
            )
            continue
        check_entry(entry, role, root, checked, changed, missing, uncheckable)

    verification = snapshot.get("verification")
    if not isinstance(verification, dict):
        uncheckable.append(
            {"path": "verification", "role": "contract", "reason": "verification must be an object"}
        )
        verification = {}
    method = verification.get("method")
    if not nonempty(method):
        uncheckable.append(
            {"path": "verification.method", "role": "contract", "reason": "method must be a non-empty string"}
        )
    if not valid_time(verification.get("verified_at")):
        uncheckable.append(
            {
                "path": "verification.verified_at",
                "role": "contract",
                "reason": "verified_at must be an ISO-8601 timestamp with timezone",
            }
        )
    check_entry(
        verification.get("raw_result"),
        "result",
        root,
        checked,
        changed,
        missing,
        uncheckable,
    )

    if uncheckable:
        status = "uncheckable"
        next_action = "Repair the snapshot contract or unsafe paths, then check it again."
    elif missing:
        status = "evidence_missing"
        paths = ", ".join(item["path"] for item in missing)
        next_action = f"Restore or regenerate missing evidence ({paths}) using: {method}"
    elif changed:
        status = "stale"
        paths = ", ".join(item["path"] for item in changed)
        next_action = f"Re-run {method} for the affected scope ({paths}); update the snapshot only after it passes."
    else:
        status = "valid_in_recorded_scope"
        next_action = "No revalidation is indicated by the files recorded in this snapshot."

    return {
        "schema_version": 1,
        "status": status,
        "acceptance": {
            "id": acceptance.get("id"),
            "version": acceptance.get("version"),
            "condition": acceptance.get("condition"),
        },
        "checked": checked,
        "changed": changed,
        "missing": missing,
        "uncheckable": uncheckable,
        "next_action": next_action,
        "limitations": [
            "Fingerprints show only whether recorded files changed; they do not prove test coverage or behavior.",
            "Unrecorded dependencies and external state are outside the snapshot's scope.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Check whether recorded plan evidence is still current.")
    parser.add_argument("snapshot", type=Path, help="Evidence snapshot JSON path")
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    print(json.dumps(check(load_json(args.snapshot), args.project_root), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
