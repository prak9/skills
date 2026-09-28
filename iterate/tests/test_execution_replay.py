from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


EVALS = Path(__file__).resolve().parents[1] / "evals"


def module(name):
    spec = importlib.util.spec_from_file_location(name, EVALS / (name + ".py"))
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


SETUP = module("prepare_execution")
REPLAY = module("replay_execution")


class ExecutionReplayTests(unittest.TestCase):
    def prepare(self, case):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name) / "run"
        SETUP.prepare(case, root)
        return root

    def test_correct_selection_and_frozen_input_integrity_are_separate(self):
        root = self.prepare("noisy-promotion")
        self.assertFalse(REPLAY.replay(root)["artifact_checks_passed"])
        (root / "workspace/selection.json").write_text('{"candidate":"steady"}')
        self.assertTrue(REPLAY.replay(root)["artifact_checks_passed"])
        with (root / "workspace/measurements.csv").open("a") as stream:
            stream.write("\n")
        result = REPLAY.replay(root)
        self.assertFalse(result["artifact_checks_passed"])
        self.assertEqual(["measurements.csv"], result["changed_frozen_files"])

    def test_scope_and_explicit_target_keep_current(self):
        for case in ("search-converged", "explicit-target-done"):
            root = self.prepare(case)
            self.assertTrue(REPLAY.replay(root)["artifact_checks_passed"])
            (root / "workspace/selection.json").write_text('{"candidate":"steady"}')
            self.assertFalse(REPLAY.replay(root)["artifact_checks_passed"])

    def test_baseline_and_broken_code_cannot_pass_as_an_improvement(self):
        root = self.prepare("pipeline-search")
        report = REPLAY.replay(root)
        self.assertFalse(report["artifact_checks_passed"])
        self.assertTrue(all(row["candidate"]["correctness"] for row in report["observations"]))
        (root / "workspace/pipeline.py").write_text("def process(records, categories):\n    return []\n")
        report = REPLAY.replay(root)
        self.assertFalse(report["artifact_checks_passed"])
        self.assertTrue(all(not row["candidate"]["correctness"] for row in report["observations"]))


if __name__ == "__main__":
    unittest.main()
