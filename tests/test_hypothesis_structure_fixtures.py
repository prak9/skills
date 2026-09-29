"""Validate development examples, not an agent's research behavior."""

import json
from pathlib import Path
import unittest


class HypothesisStructureFixtureTests(unittest.TestCase):
    def test_packet_and_missing_outcome_bounds(self):
        packet = Path(__file__).with_name("hypothesis-structure-cases.jsonl")
        cases = [json.loads(line) for line in packet.read_text().splitlines()]
        self.assertEqual(len(cases), len({case["id"] for case in cases}))
        for case in cases:
            self.assertEqual("development", case["split"])
            self.assertEqual("research-craft", case["skill"])
            self.assertTrue(case["prompt"])
            self.assertTrue(case["expected_behavior"])
            self.assertTrue(case["criteria"])
        missing = next(case for case in cases if case["id"] == "hypothesis-missing-followup")
        self.assertEqual(missing["numeric_checks"], {
            "complete_case_rate": 40 / 80,
            "all_event_lower_bound": 40 / 100,
            "all_event_upper_bound": (40 + 20) / 100,
        })


if __name__ == "__main__":
    unittest.main()
