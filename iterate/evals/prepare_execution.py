#!/usr/bin/env python3
"""Prepare one isolated forward-execution case; does not run or grade a model."""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path


EVALS = Path(__file__).resolve().parent


def fingerprint(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def prepare(case_id: str, destination: Path) -> dict:
    packet = json.loads((EVALS / "execution-cases.json").read_text(encoding="utf-8"))
    case = next((case for case in packet["cases"] if case["id"] == case_id), None)
    if case is None:
        raise ValueError(f"unknown execution case: {case_id}")
    fixture = EVALS / "fixtures" / case["fixture"]
    if not (fixture / "README.md").is_file():
        raise FileNotFoundError(f"incomplete fixture: {fixture}")
    if destination.resolve().is_relative_to(fixture.resolve()):
        raise ValueError("destination must be outside the source fixture")
    destination.mkdir(parents=True, exist_ok=False)
    workspace = destination / "workspace"
    shutil.copytree(fixture, workspace, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    shutil.copyfile(EVALS.parent / "SKILL.md", destination / "instruction.md")
    (destination / "task.md").write_text(case["prompt"] + "\n", encoding="utf-8")
    if case.get("resume_note"):
        (workspace / "evidence").mkdir()
        (workspace / "evidence/old.json").write_text(
            json.dumps({"candidate_sha256": "0" * 64, "dataset": "retired-v0", "correctness": True}),
            encoding="utf-8",
        )
        (workspace / "progress.md").write_text(
            "# Previous progress\n\nCandidate A passed; ready to deliver. "
            "Evidence: evidence/old.json. Current implementation: pipeline.py.\n",
            encoding="utf-8",
        )
    manifest = {
        "suite": packet["suite"],
        "case": case_id,
        "case_packet_sha256": fingerprint(EVALS / "execution-cases.json"),
        "instruction_sha256": fingerprint(destination / "instruction.md"),
        "fixture_sha256": {
            str(path.relative_to(workspace)): fingerprint(path)
            for path in sorted(workspace.rglob("*")) if path.is_file()
        },
    }
    (destination / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", required=True)
    parser.add_argument("--output", type=Path, required=True, help="New case directory; never overwritten")
    args = parser.parse_args()
    try:
        manifest = prepare(args.case, args.output)
    except (ValueError, OSError) as error:
        parser.exit(2, f"error: {error}\n")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
