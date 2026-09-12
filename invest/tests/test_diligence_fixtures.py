"""Check the development packet, not the model's investment judgment."""

from __future__ import annotations

import json
import unittest
from pathlib import Path


PACKET = Path(__file__).resolve().parents[1] / "evals" / "diligence-cases.jsonl"
SOURCE_PACKET = PACKET.with_name("source-diligence-cases.jsonl")
DAYU_PACKET = PACKET.with_name("dayu-diligence-cases.jsonl")
EARNINGS_PACKET = PACKET.with_name("earnings-continuity-cases.jsonl")


class DiligenceFixtureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.cases = [
            json.loads(line)
            for packet in (PACKET, SOURCE_PACKET, DAYU_PACKET, EARNINGS_PACKET)
            for line in packet.read_text().splitlines()
        ]
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

    def test_cloud_cost_oracle_uses_billed_hours_not_mfu(self) -> None:
        capacity_hours = 100 * 100
        billed_hours = capacity_hours * .60
        revenue = billed_hours * 2
        ebitda = revenue - billed_hours * .2 - 9000
        ebit = ebitda - 3000
        pretax = ebit - 1000
        self.assert_numeric("source-ai-cloud-cost-bases", {
            "revenue": revenue,
            "ebitda": ebitda,
            "ebit": ebit,
            "pretax_profit": pretax,
            "pretax_breakeven_billed_utilization": (
                (9000 + 3000 + 1000) / (capacity_hours * (2 - .2))
            ),
        })

    def test_source_repair_preserves_a_valid_derived_ratio(self) -> None:
        self.assert_numeric("dayu-repair-locator-preserve-analysis", {
            "gross_margin": 300 / 1000,
        })

    def test_extracted_period_and_scale_require_original_context(self) -> None:
        q3_revenue_millions = 900 - 500
        self.assert_numeric("dayu-extraction-confidence-is-not-evidence", {
            "q3_revenue_millions": q3_revenue_millions,
            "q3_revenue_billions": q3_revenue_millions / 1000,
        })

    def test_four_quarter_oracle_tracks_profit_and_cash_not_just_revenue(self) -> None:
        revenue = [100, 120, 130, 150]
        gross_profit = [40, 42, 39, 42]
        cfo = [30, 26, 20, 18]
        cash_capex = [25, 40, 65, 80]
        self.assert_numeric("earnings-four-periods-not-five-documents", {
            "fy_revenue": sum(revenue),
            "fy_gross_margin": sum(gross_profit) / sum(revenue),
            "fy_cfo_less_cash_capex": sum(cfo) - sum(cash_capex),
            "q4_gross_margin": gross_profit[-1] / revenue[-1],
        })


if __name__ == "__main__":
    unittest.main()
