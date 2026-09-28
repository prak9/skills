#!/usr/bin/env python3
"""Post-run counterexample check, separate from the frozen v1 comparison."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import runpy


class UnhashableString(str):
    __hash__ = None


def check(candidate: Path) -> dict:
    result = {
        "check": "unhashable-string-record-v1",
        "evidence_type": "post-hoc supplemental counterexample, not a predeclared holdout",
        "candidate_sha256": hashlib.sha256(candidate.read_bytes()).hexdigest(),
        "checker_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "passed": False,
    }
    expected = [{"id": "x", "amount": 0, "category": 0}] * 3
    try:
        process = runpy.run_path(str(candidate))["process"]
        actual = process([UnhashableString('{"id":"x","category":" A "}')] * 3, ["a"])
        result["passed"] = actual == expected
    except Exception as error:
        result["error_type"] = type(error).__name__
        result["error"] = str(error)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("candidate", type=Path)
    args = parser.parse_args()
    result = check(args.candidate)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
