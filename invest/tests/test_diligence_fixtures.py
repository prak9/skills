"""Check the development packet, not the model's investment judgment."""

from __future__ import annotations

import json
import unittest
from pathlib import Path


PACKET = Path(__file__).resolve().parents[1] / "evals" / "diligence-cases.jsonl"


class DiligenceFixtureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.cases = [json.loads(line) for line in PACKET.read_text().splitlines()]
        cls.by_id = {case["id"]: case for case in cls.cases}

    def test_packet_has_unique_development_cases_and_semantic_criteria(self) -> None:
        self.assertEqual(len(self.cases), len(self.by_id))
        for case in self.cases:
            with self.subTest(case=case["id"]):
                self.assertEqual("development", case["split"])
                self.assertTrue(case["prompt"].strip())
                self.assertTrue(case["expected_behavior"].strip())
                self.assertTrue(case["criteria"])
                self.assertTrue(all(item.strip() for item in case["criteria"]))

    def assert_numeric(self, case_id: str, calculated: dict[str, float]) -> None:
        expected = self.by_id[case_id]["numeric_checks"]
        self.assertEqual(set(expected), set(calculated))
        for name, value in calculated.items():
            with self.subTest(case=case_id, metric=name):
                self.assertAlmostEqual(expected[name], value, places=8)

    def test_numeric_oracles_follow_the_supplied_economics(self) -> None:
        prior_payout = (20 + 80) * .25
        current_payout = 40 * .40 + 70 * .25
        prior_contribution = 100 - prior_payout - 100 * .20 - 15 - 20
        current_contribution = 110 - current_payout - 110 * .20 - 20 - 20
        self.assert_numeric("depth-mix-and-economics", {
            "prior_creator_payout": prior_payout,
            "current_creator_payout": current_payout,
            "prior_contribution": prior_contribution,
            "current_contribution": current_contribution,
            "contribution_change": current_contribution - prior_contribution,
        })

        baseline = 1.6 / .10 + 2
        finite_increment = sum(.6 / 1.1**year for year in range(1, 5))
        conditional = baseline + finite_increment
        self.assert_numeric("depth-supported-price-gap", {
            "baseline_value": baseline,
            "incremental_pv": finite_increment,
            "conditional_value": conditional,
            "value_gap": conditional / 18 - 1,
        })
        # The case must distinguish a four-year contract from a perpetuity.
        self.assertGreater(.6 / .10, finite_increment)

        prior_profit = 100 * .30 - 15
        forward_profit = 130 * .22 - 19
        self.assert_numeric("depth-predictable-price-not-guaranteed", {
            "prior_operating_profit": prior_profit,
            "forward_operating_profit": forward_profit,
            "profit_change": forward_profit - prior_profit,
        })
        value = (5 - 1) / .10
        self.assert_numeric("depth-negative-variant", {
            "conditional_value": value,
            "value_gap": value / 50 - 1,
        })


if __name__ == "__main__":
    unittest.main()
