from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


EVALS = Path(__file__).resolve().parents[1] / "evals"


def load(name):
    spec = importlib.util.spec_from_file_location(name, EVALS / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


REPLAY = load("replay_execution")
EDGES = load("check_contract_edges")
ARCHIVE = json.loads((EVALS / "execution-evidence.json").read_text())


class ExecutionArchiveTests(unittest.TestCase):
    def test_every_archived_byte_is_bound_to_its_fingerprint(self):
        for digest, content in ARCHIVE["blobs"].items():
            self.assertEqual(digest, hashlib.sha256(content.encode()).hexdigest())
        for run in ARCHIVE["runs"].values():
            for digest in run["files"].values():
                self.assertIn(digest, ARCHIVE["blobs"])

    def test_archived_outcomes_replay_including_known_counterexamples(self):
        for name, run in ARCHIVE["runs"].items():
            with self.subTest(run=name), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                for relative, digest in run["files"].items():
                    target = root / relative
                    self.assertTrue(target.resolve().is_relative_to(root.resolve()))
                    target.parent.mkdir(parents=True, exist_ok=True)
                    with target.open("x", encoding="utf-8") as stream:
                        stream.write(ARCHIVE["blobs"][digest])
                expected = json.loads((root / "replay.json").read_text())
                actual = REPLAY.replay(root)
                for field in ("case", "instruction_sha256", "observations", "changed_frozen_files", "artifact_checks_passed"):
                    self.assertEqual(expected[field], actual[field])
                if "post_hoc_contract_check" in run:
                    edge = EDGES.check(root / "workspace/pipeline.py")
                    self.assertEqual(run["post_hoc_contract_check"]["passed"], edge["passed"])
                    self.assertEqual(run["post_hoc_contract_check"]["candidate_sha256"], edge["candidate_sha256"])


if __name__ == "__main__":
    unittest.main()
