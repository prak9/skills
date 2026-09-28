from __future__ import annotations

import importlib.util
from pathlib import Path
import tempfile
import unittest


EVALS = Path(__file__).resolve().parents[1] / "evals"
SPEC = importlib.util.spec_from_file_location("check_contract_edges", EVALS / "check_contract_edges.py")
EDGES = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(EDGES)


class ContractEdgeTests(unittest.TestCase):
    def test_reference_accepts_unhashable_string_records(self):
        result = EDGES.check(EVALS / "fixtures/pipeline/pipeline.py")
        self.assertTrue(result["passed"])

    def test_caching_must_not_narrow_the_string_input_contract(self):
        with tempfile.TemporaryDirectory() as temporary:
            candidate = Path(temporary) / "candidate.py"
            candidate.write_text(
                "def process(records, categories):\n"
                "    cache = {}\n"
                "    for raw in records:\n"
                "        cache[raw] = None\n"
                "    return []\n"
            )
            result = EDGES.check(candidate)
            self.assertFalse(result["passed"])
            self.assertEqual("TypeError", result["error_type"])


if __name__ == "__main__":
    unittest.main()
