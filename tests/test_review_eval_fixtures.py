from __future__ import annotations

import json
import shlex
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


EVALS = Path(__file__).resolve().parents[1] / "code-review-craft" / "evals"


class ReviewEvalFixtureTests(unittest.TestCase):
    def copy_fixture(self, name: str) -> Path:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        directory = Path(temporary.name) / "candidate"
        shutil.copytree(EVALS / "fixtures" / name, directory)
        return directory

    def run_python(self, directory: Path, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "-B", *args],
            cwd=directory,
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )

    def test_cases_supply_existing_raw_artifacts(self):
        cases = json.loads((EVALS / "evals.json").read_text(encoding="utf-8"))["evals"]
        self.assertEqual(len(cases), len({case["id"] for case in cases}))
        for case in cases:
            with self.subTest(case=case["id"]):
                self.assertTrue(case["files"])
                for filename in case["files"]:
                    artifact = (EVALS / filename).resolve()
                    self.assertTrue(artifact.is_relative_to(EVALS.resolve()))
                    self.assertTrue(artifact.is_file(), filename)
                    self.assertGreater(artifact.stat().st_size, 0, filename)

    def test_diff_fixtures_are_parseable_without_recount(self):
        patches = sorted((EVALS / "fixtures").rglob("*.diff"))
        self.assertTrue(patches)
        for patch in patches:
            with self.subTest(patch=patch.relative_to(EVALS)):
                result = subprocess.run(
                    ["git", "apply", "--numstat", str(patch)],
                    capture_output=True,
                    text=True,
                    timeout=10,
                    check=False,
                )
                self.assertEqual(0, result.returncode, result.stderr)
                self.assertTrue(result.stdout.strip())

    def test_green_unit_tests_do_not_cover_broken_quickstart(self):
        directory = self.copy_fixture("green-tests-broken-get-started")
        unit = self.run_python(directory, "-m", "unittest", "-v", "test_catalog.py")
        self.assertEqual(0, unit.returncode, unit.stdout + unit.stderr)

        guide = (directory / "README.md").read_text(encoding="utf-8")
        command = shlex.split(guide.split("```sh\n", 1)[1].split("```", 1)[0])
        self.assertEqual("python3", command[0])
        replay = self.run_python(directory, *command[1:])
        self.assertEqual(2, replay.returncode, replay.stdout + replay.stderr)
        self.assertIn("--output-dir", replay.stderr)
        self.assertFalse((directory / "build" / "catalog.json").exists())

        control = self.run_python(
            directory, "catalog.py", "--input", "examples/items.json", "--output-dir", "build"
        )
        self.assertEqual(0, control.returncode, control.stdout + control.stderr)
        self.assertEqual(
            {"count": 2, "names": ["Desk", "Lamp"]},
            json.loads((directory / "build" / "catalog.json").read_text(encoding="utf-8")),
        )

    def test_consensus_case_has_working_code_but_no_required_replay(self):
        directory = self.copy_fixture("reviewer-consensus-without-acceptance-evidence")
        unit = self.run_python(directory, "-m", "unittest", "-v", "test_summary.py")
        self.assertEqual(0, unit.returncode, unit.stdout + unit.stderr)
        contract = json.loads((directory / "acceptance.json").read_text(encoding="utf-8"))
        self.assertFalse((directory / contract["before_merge"]["dataset"]).exists())
        for name in ("reviewer-a.json", "reviewer-b.json"):
            record = json.loads((directory / name).read_text(encoding="utf-8"))
            self.assertEqual(contract["candidate_id"], record["candidate_id"])
            self.assertEqual("Approve", record["verdict"])
            self.assertIsNone(record["snapshot_replay"])

        # A local smoke check is evidence for this sample, not the missing snapshot.
        sample = [{"id": "toy-a", "amount_cents": 110}, {"id": "toy-b", "amount_cents": 220}]
        sample_path = directory / "toy-orders.json"
        original = json.dumps(sample)
        sample_path.write_text(original, encoding="utf-8")
        replay = self.run_python(directory, "summary.py", "--input", str(sample_path))
        self.assertEqual(0, replay.returncode, replay.stdout + replay.stderr)
        self.assertEqual({"count": 2, "total_cents": 330}, json.loads(replay.stdout))
        self.assertEqual(original, sample_path.read_text(encoding="utf-8"))
        self.assertNotEqual(
            contract["before_merge"]["expected_from_existing_spreadsheet"], json.loads(replay.stdout)
        )


if __name__ == "__main__":
    unittest.main()
