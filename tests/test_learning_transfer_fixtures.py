from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests/fixtures/learning-transfer/pagination"


class LearningTransferFixtureTests(unittest.TestCase):
    def test_sequence_packet_has_distinct_turns_and_criteria(self):
        packet = json.loads((ROOT / "tests/learning-transfer-cases.json").read_text())
        sequences = packet["sequences"]
        self.assertEqual({"research", "quant", "decision", "plan"}, {s["id"] for s in sequences})
        self.assertEqual(4, len(sequences))
        for sequence in sequences:
            with self.subTest(sequence=sequence["id"]):
                self.assertTrue(sequence["turns"])
                self.assertEqual(len(sequence["turns"]), len(set(sequence["turns"])))
                self.assertTrue(sequence["criteria"])
                self.assertTrue((ROOT / sequence["skill"] / "SKILL.md").is_file())
                if "fixture" in sequence:
                    self.assertEqual(FIXTURE, ROOT / sequence["fixture"])

    def test_passing_old_checker_misses_incomplete_export(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary) / "project"
            shutil.copytree(FIXTURE, directory)
            unit = subprocess.run(
                [sys.executable, "-B", "-m", "unittest", "-v", "test_export.py"],
                cwd=directory, capture_output=True, text=True, timeout=10,
            )
            self.assertEqual(0, unit.returncode, unit.stdout + unit.stderr)
            actual = subprocess.run(
                [sys.executable, "-B", "-c",
                 "import json; from exporter import export_rows; print(json.dumps(export_rows()))"],
                cwd=directory, capture_output=True, text=True, timeout=10,
            )
            self.assertEqual(0, actual.returncode, actual.stderr)
            result = json.loads(actual.stdout)
            self.assertEqual(200, result["status"])
            self.assertEqual(list(range(1, 101)), [row["id"] for row in result["rows"]])
            self.assertNotEqual(set(range(1, 121)), {row["id"] for row in result["rows"]})

    def test_initial_lite_state_is_valid_but_not_complete(self):
        result = subprocess.run(
            [sys.executable, "-B", str(ROOT / "plan-skill/scripts/validate_plan.py"),
             "--strict", str(FIXTURE)],
            capture_output=True, text=True, timeout=10,
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("Overall status: `进行中`", (FIXTURE / "program.md").read_text())

    def test_observed_turns_preserve_frozen_prompts(self):
        packet = json.loads((ROOT / "tests/learning-transfer-cases.json").read_text())
        observed = json.loads((ROOT / "tests/learning-transfer-observed.json").read_text())
        cases = {case["id"]: case for case in packet["sequences"]}
        self.assertEqual(packet["baseline_commit"], observed["baseline_commit"])
        self.assertEqual(5, len(observed["runs"]))
        self.assertEqual(10, sum(len(run["turns"]) for run in observed["runs"]))
        for run in observed["runs"]:
            with self.subTest(case=run["case"], version=run["version"]):
                self.assertEqual(cases[run["case"]]["turns"], [t["prompt"] for t in run["turns"]])
                for turn in run["turns"]:
                    self.assertTrue(turn["response"].strip())
                    self.assertIsInstance(turn["executor_trace"], dict)

    def test_archived_repair_passes_and_detects_original_bug(self):
        observed = json.loads((ROOT / "tests/learning-transfer-observed.json").read_text())
        artifacts = observed["plan_artifacts"]
        for name in ("source.py", "artifacts/previous-check.txt"):
            self.assertEqual((FIXTURE / name).read_text(), artifacts[name])

        def acceptance(text):
            return text.split("## Acceptance\n", 1)[1].split("\n## Plan", 1)[0]

        self.assertEqual(acceptance((FIXTURE / "program.md").read_text()),
                         acceptance(artifacts["program.md"]))
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            for name, content in artifacts.items():
                target = (directory / name).resolve()
                self.assertTrue(target.is_relative_to(directory.resolve()))
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(content, encoding="utf-8")
            command = [sys.executable, "-B", "-m", "unittest", "-v", "test_export.py"]
            green = subprocess.run(command, cwd=directory, capture_output=True, text=True, timeout=10)
            self.assertEqual(0, green.returncode, green.stdout + green.stderr)
            content = subprocess.run(
                [sys.executable, "-B", "-c",
                 "from exporter import export_rows; r=export_rows(); ids=[x['id'] for x in r['rows']]; "
                 "assert r['status']==200; assert len(ids)==120 and set(ids)==set(range(1,121))"],
                cwd=directory, capture_output=True, text=True, timeout=10,
            )
            self.assertEqual(0, content.returncode, content.stderr)
            validation = subprocess.run(
                [sys.executable, "-B", str(ROOT / "plan-skill/scripts/validate_plan.py"),
                 "--strict", str(directory)],
                capture_output=True, text=True, timeout=10,
            )
            self.assertEqual(0, validation.returncode, validation.stdout + validation.stderr)
            shutil.copy2(FIXTURE / "exporter.py", directory / "exporter.py")
            red = subprocess.run(command, cwd=directory, capture_output=True, text=True, timeout=10)
            self.assertEqual(1, red.returncode, red.stdout + red.stderr)
            self.assertIn("120 != 100", red.stderr)


if __name__ == "__main__":
    unittest.main()
