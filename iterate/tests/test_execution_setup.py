from __future__ import annotations

import csv
import importlib.util
import json
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path


EVALS = Path(__file__).resolve().parents[1] / "evals"
SPEC = importlib.util.spec_from_file_location("prepare_execution", EVALS / "prepare_execution.py")
SETUP = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SETUP)


class ExecutionSetupTests(unittest.TestCase):
    def test_executor_packet_excludes_criteria_and_starts_from_snapshot(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "run"
            SETUP.prepare("noisy-promotion", root)
            self.assertEqual(
                (EVALS.parent / "SKILL.md").read_bytes(),
                (root / "instruction.md").read_bytes(),
            )
            self.assertNotIn("criteria", (root / "task.md").read_text())
            self.assertEqual(
                {"README.md", "measurements.csv", "selection.json"},
                {path.name for path in (root / "workspace").iterdir()},
            )
            manifest = json.loads((root / "manifest.json").read_text())
            self.assertEqual("noisy-promotion", manifest["case"])
            self.assertEqual(64, len(manifest["instruction_sha256"]))
            self.assertEqual(3, len(manifest["fixture_sha256"]))

    def test_existing_destination_and_unknown_case_do_not_mutate(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            marker = root / "user.txt"
            marker.write_text("preserve")
            with self.assertRaises(FileExistsError):
                SETUP.prepare("noisy-promotion", root)
            with self.assertRaises(ValueError):
                SETUP.prepare("../unknown", root / "new")
            self.assertEqual("preserve", marker.read_text())
            self.assertFalse((root / "new").exists())

    def test_resume_exposes_stale_evidence_without_rewriting_it(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "resume"
            SETUP.prepare("pipeline-resume", root)
            old = json.loads((root / "workspace/evidence/old.json").read_text())
            self.assertNotEqual(old["candidate_sha256"], SETUP.fingerprint(root / "workspace/pipeline.py"))
            self.assertEqual("retired-v0", old["dataset"])

    def test_destination_inside_fixture_is_rejected_before_writing(self):
        with patch.object(Path, "mkdir", side_effect=AssertionError("unexpected write")):
            with self.assertRaises(ValueError):
                SETUP.prepare("noisy-promotion", EVALS / "fixtures/measurements/nested-run")

    def test_cases_have_unique_ids_and_existing_fixtures(self):
        cases = json.loads((EVALS / "execution-cases.json").read_text())["cases"]
        self.assertEqual(len(cases), len({case["id"] for case in cases}))
        for case in cases:
            self.assertTrue((EVALS / "fixtures" / case["fixture"] / "README.md").is_file())
            self.assertTrue(case["criteria"])

    def test_replay_distinguishes_discovery_from_repeated_results(self):
        with (EVALS / "fixtures/measurements/measurements.csv").open() as source:
            rows = list(csv.DictReader(source))
        discovery = {r["candidate"]: float(r["score"]) for r in rows if r["phase"] == "discovery"}
        self.assertEqual("sprint", max(discovery, key=discovery.get))
        means = {}
        for candidate in discovery:
            samples = [r for r in rows if r["phase"] == "confirmation" and r["candidate"] == candidate]
            self.assertEqual({"1", "2", "3", "4"}, {r["run"] for r in samples})
            self.assertTrue(all(r["correct"] == "true" and r["workload"] == "orders-v2" for r in samples))
            means[candidate] = sum(float(r["score"]) for r in samples) / len(samples)
        self.assertEqual({"current": 100, "sprint": 94.5, "steady": 109}, means)


if __name__ == "__main__":
    unittest.main()
