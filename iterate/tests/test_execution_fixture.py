import hashlib
import json
from pathlib import Path
import runpy
import subprocess
import sys
import tempfile
import unittest


FIXTURE = Path(__file__).resolve().parents[1] / "evals" / "fixtures" / "pipeline"
BASELINE = (FIXTURE / "pipeline.py").read_text(encoding="utf-8")


class ExecutionFixtureTests(unittest.TestCase):
    def candidate(self, source):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        path = Path(temporary.name) / "pipeline.py"
        path.write_text(source, encoding="utf-8")
        return path

    def probe(self, candidate, dataset):
        result = subprocess.run(
            [sys.executable, "-B", str(FIXTURE / "probe.py"), "--candidate", str(candidate),
             "--dataset", dataset], capture_output=True, text=True, timeout=10, check=False)
        self.assertIn(result.returncode, (0, 1), result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(result.returncode, 0 if report["correctness"] else 1)
        self.assertEqual(report["candidate_sha256"], hashlib.sha256(candidate.read_bytes()).hexdigest())
        self.assertEqual(report["dataset_id"], dataset + "-v1")
        return report

    def test_baseline_contract_and_call_independence(self):
        process = runpy.run_path(str(FIXTURE / "pipeline.py"))["process"]
        rows = ['{"id":"a","amount":-3,"category":" Straße "}', '{"id":"b"}',
                '{"id":"bool","amount":true}', '{"id":"null","category":null}',
                '[]', '{', None, '{"id":7}', '{"id":"float","amount":1.0}']
        rows.append(rows[0])
        untouched = list(rows)
        expected = [{"id": "a", "amount": -3, "category": 1},
                    {"id": "b", "amount": 0, "category": -1},
                    {"id": "a", "amount": -3, "category": 1}]
        self.assertEqual(process(rows, ["other", "strasse"]), expected)
        expected[0]["category"] = expected[2]["category"] = 0
        self.assertEqual(process(rows, ["strasse"]), expected)
        self.assertEqual(rows, untouched)
        self.assertEqual(process([], []), [])
        self.assertEqual(process(['{"id":"a"}'], []), [{"id": "a", "amount": 0, "category": -1}])

    def test_probe_baseline_is_correct_deterministic_and_version_bound(self):
        candidate = self.candidate(BASELINE)
        expected = {"small": {"decode": 664, "lookup": 1450},
                    "wide": {"decode": 2392, "lookup": 29098}}
        for name in ("small", "wide"):
            with self.subTest(dataset=name):
                first = self.probe(candidate, name)
                self.assertTrue(first["correctness"])
                self.assertEqual(first, self.probe(candidate, name))
                self.assertEqual(first["work"], expected[name])
        old = self.probe(candidate, "small")
        candidate.write_text(BASELINE + "\n# New source revision.\n", encoding="utf-8")
        new = self.probe(candidate, "small")
        self.assertNotEqual(old["candidate_sha256"], new["candidate_sha256"])
        self.assertEqual(old["work"], new["work"])

    def test_probe_rejects_incorrect_and_crashing_candidates(self):
        for source in (BASELINE.replace("category.strip().casefold()", "category.strip()"),
                       'def process(records, categories):\n    raise RuntimeError("broken")\n'):
            candidate = self.candidate(source)
            for name in ("small", "wide"):
                with self.subTest(dataset=name, candidate=source[:30]):
                    self.assertFalse(self.probe(candidate, name)["correctness"])

    def test_first_gain_leaves_a_second_independent_mechanism(self):
        parsed_once = BASELINE.replace(
            "if not isinstance(json.loads(raw), dict):",
            "item = json.loads(raw)\n            if not isinstance(item, dict):",
        ).replace("json.loads(raw).get", "item.get")
        indexed = parsed_once.replace(
            "    results = []", "    index = {name: i for i, name in enumerate(categories)}\n    results = []"
        ).replace("next((i for i, name in enumerate(categories) if name == category), -1)",
                  "index.get(category, -1)")
        candidates = [self.candidate(source) for source in (BASELINE, parsed_once, indexed)]
        for name in ("small", "wide"):
            with self.subTest(dataset=name):
                base, first, second = [self.probe(candidate, name) for candidate in candidates]
                self.assertTrue(all(result["correctness"] for result in (base, first, second)))
                self.assertLess(first["work"]["decode"], base["work"]["decode"])
                self.assertEqual(first["work"]["lookup"], base["work"]["lookup"])
                self.assertEqual(second["work"]["decode"], first["work"]["decode"])
                self.assertLess(second["work"]["lookup"], first["work"]["lookup"])


if __name__ == "__main__":
    unittest.main()
