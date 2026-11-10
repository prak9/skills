"""Replay saved artifacts; this does not rerun or independently grade an LLM."""

import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests/fixtures/learning-transfer/pagination"


class WorkflowContextFixtureTests(unittest.TestCase):
    def setUp(self):
        self.packet_path = ROOT / "tests/workflow-context-cases.json"
        self.packet = json.loads(self.packet_path.read_text())
        self.observed = json.loads(
            (ROOT / "tests/workflow-context-observed.json").read_text()
        )

    def test_frozen_inputs_and_actual_turns_are_preserved(self):
        self.assertEqual(
            hashlib.sha256(self.packet_path.read_bytes()).hexdigest(),
            self.observed["packet_sha256"],
        )
        cases = {case["id"]: case for case in self.packet["cases"]}
        runs = self.observed["runs"]
        self.assertEqual(
            {(arm, case) for arm in ("A", "B") for case in cases},
            {(run["arm"], run["case"]) for run in runs},
        )
        self.assertEqual(4, len(runs))
        for run in runs:
            with self.subTest(arm=run["arm"], case=run["case"]):
                self.assertEqual(
                    cases[run["case"]]["turns"],
                    [turn["prompt"] for turn in run["turns"]],
                )
                self.assertTrue(all(turn["response"].strip() for turn in run["turns"]))
                self.assertTrue(all(isinstance(turn["trace"], dict) for turn in run["turns"]))

    def test_saved_repairs_pass_and_reject_original_incomplete_export(self):
        for arm, files in self.observed["plan_artifacts"].items():
            with self.subTest(arm=arm), tempfile.TemporaryDirectory() as temporary:
                directory = Path(temporary)
                for name, text in files.items():
                    target = (directory / name).resolve()
                    self.assertTrue(target.is_relative_to(directory.resolve()))
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_text(text)
                for name in ("source.py", "artifacts/previous-check.txt"):
                    self.assertEqual((FIXTURE / name).read_text(), files[name])
                self.assertEqual(
                    self.packet["cases"][1]["receipt"],
                    json.loads(files["service/receipt.json"]),
                )
                self.assertEqual(
                    json.dumps(self.packet["cases"][1]["receipt"], separators=(",", ":")) + "\n",
                    files["service/receipt.json"],
                )
                original = (FIXTURE / "program.md").read_text()
                for section in ("Outcome", "Acceptance"):
                    heading = f"## {section}\n"
                    before = original.split(heading, 1)[1].split("\n## ", 1)[0]
                    after = files["program.md"].split(heading, 1)[1].split("\n## ", 1)[0]
                    self.assertEqual(before, after)
                command = [sys.executable, "-B", "-m", "unittest", "-v", "test_export.py"]
                green = subprocess.run(command, cwd=directory, capture_output=True, text=True, timeout=15)
                self.assertEqual(0, green.returncode, green.stdout + green.stderr)
                actual = subprocess.run(
                    [sys.executable, "-B", "-c",
                     "from exporter import export_rows; r=export_rows(); "
                     "ids=[row['id'] for row in r['rows']]; "
                     "assert r['status']==200; assert len(ids)==120; "
                     "assert set(ids)==set(range(1,121))"],
                    cwd=directory, capture_output=True, text=True, timeout=15,
                )
                self.assertEqual(0, actual.returncode, actual.stdout + actual.stderr)
                strict = subprocess.run(
                    [sys.executable, "-B", str(ROOT / "plan-skill/scripts/validate_plan.py"),
                     "--strict", str(directory)],
                    capture_output=True, text=True, timeout=15,
                )
                self.assertEqual(0, strict.returncode, strict.stdout + strict.stderr)
                shutil.copyfile(FIXTURE / "exporter.py", directory / "exporter.py")
                red = subprocess.run(command, cwd=directory, capture_output=True, text=True, timeout=15)
                self.assertNotEqual(0, red.returncode, "New tests failed to detect the old omission")
                self.assertIn("FAIL", red.stdout + red.stderr)

    def test_no_new_information_followup_preserves_project_bytes(self):
        for arm, pair in self.observed["plan_followup_hashes"].items():
            with self.subTest(arm=arm):
                self.assertTrue(pair["before"])
                self.assertEqual(pair["before"], pair["after"])


if __name__ == "__main__":
    unittest.main()
