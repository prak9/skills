from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = SKILL_ROOT / "scripts" / "check_evidence_snapshot.py"


class EvidenceSnapshotTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        for relative, content in (
            ("acceptance.md", "A-001 v1: endpoint returns 200\n"),
            ("src/app.py", "def status(): return 200\n"),
            ("tests/test_app.py", "def test_status(): assert True\n"),
            ("artifacts/test.log", "1 passed\n"),
        ):
            path = self.root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
        self.snapshot_path = self.root / "evidence-snapshot.json"
        self.write_snapshot()

    def tearDown(self) -> None:
        self.temp.cleanup()

    def digest(self, relative: str) -> str:
        return hashlib.sha256((self.root / relative).read_bytes()).hexdigest()

    def write_snapshot(self) -> None:
        snapshot = {
            "schema_version": 1,
            "acceptance": {
                "id": "A-001",
                "version": "v1",
                "condition": "endpoint returns 200",
                "source": {"path": "acceptance.md", "sha256": self.digest("acceptance.md")},
            },
            "inputs": [
                {"path": "src/app.py", "role": "source", "sha256": self.digest("src/app.py")},
                {"path": "tests/test_app.py", "role": "test", "sha256": self.digest("tests/test_app.py")},
            ],
            "verification": {
                "method": "python -m pytest tests/test_app.py",
                "verified_at": "2026-09-05T10:00:00+08:00",
                "raw_result": {
                    "path": "artifacts/test.log",
                    "sha256": self.digest("artifacts/test.log"),
                },
            },
        }
        self.snapshot_path.write_text(json.dumps(snapshot), encoding="utf-8")

    def run_check(self) -> dict:
        process = subprocess.run(
            [
                sys.executable,
                "-B",
                str(SCRIPT),
                str(self.snapshot_path),
                "--project-root",
                str(self.root),
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(0, process.returncode, process.stderr)
        return json.loads(process.stdout)

    def test_unchanged_recorded_scope_is_valid(self) -> None:
        result = self.run_check()

        self.assertEqual("valid_in_recorded_scope", result["status"])
        self.assertEqual([], result["changed"])

    def test_related_source_change_makes_evidence_stale(self) -> None:
        (self.root / "src/app.py").write_text("def status(): return 500\n", encoding="utf-8")

        result = self.run_check()

        self.assertEqual("stale", result["status"])
        self.assertEqual("src/app.py", result["changed"][0]["path"])
        self.assertIn("python -m pytest tests/test_app.py", result["next_action"])

    def test_acceptance_version_source_change_makes_evidence_stale(self) -> None:
        (self.root / "acceptance.md").write_text("A-001 v2: endpoint returns JSON\n", encoding="utf-8")

        result = self.run_check()

        self.assertEqual("stale", result["status"])
        self.assertEqual("acceptance.md", result["changed"][0]["path"])

    def test_unrelated_file_change_does_not_invalidate_snapshot(self) -> None:
        (self.root / "README.md").write_text("unrelated documentation\n", encoding="utf-8")

        result = self.run_check()

        self.assertEqual("valid_in_recorded_scope", result["status"])

    def test_missing_raw_result_is_evidence_missing(self) -> None:
        (self.root / "artifacts/test.log").unlink()

        result = self.run_check()

        self.assertEqual("evidence_missing", result["status"])
        self.assertEqual("artifacts/test.log", result["missing"][0]["path"])

    def test_path_outside_project_is_uncheckable(self) -> None:
        snapshot = json.loads(self.snapshot_path.read_text(encoding="utf-8"))
        snapshot["inputs"][0]["path"] = "../outside.py"
        self.snapshot_path.write_text(json.dumps(snapshot), encoding="utf-8")

        result = self.run_check()

        self.assertEqual("uncheckable", result["status"])
        self.assertEqual("../outside.py", result["uncheckable"][0]["path"])


if __name__ == "__main__":
    unittest.main()
