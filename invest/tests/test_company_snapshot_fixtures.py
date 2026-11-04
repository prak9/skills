"""Check development-fixture arithmetic, not an agent's investment judgment."""

import json
from pathlib import Path
import unittest


PACKET = Path(__file__).resolve().parents[1] / "evals/company-snapshot-cases.jsonl"


class CompanySnapshotFixtureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases = [json.loads(line) for line in PACKET.read_text().splitlines()]
        cls.by_id = {case["id"]: case for case in cls.cases}

    def assert_numeric(self, case_id, calculated):
        expected = self.by_id[case_id]["numeric_checks"]
        self.assertEqual(set(expected), set(calculated))
        for key, value in calculated.items():
            with self.subTest(case=case_id, metric=key):
                self.assertAlmostEqual(expected[key], value, places=8)

    def test_case_packet_has_unique_scoped_development_requests(self):
        self.assertEqual(6, len(self.cases))
        self.assertEqual(len(self.cases), len(self.by_id))
        for case in self.cases:
            with self.subTest(case=case["id"]):
                self.assertEqual("development", case["split"])
                self.assertEqual("invest", case["skill"])
                self.assertTrue(case["prompt"] and case["expected_behavior"])
                self.assertTrue(case["criteria"])

    def test_snapshot_oracle_preserves_tax_capital_and_cash_bases(self):
        x = self.by_id["snapshot-standard-ratios"]["inputs"]
        nopat = x["ebit"] * (1 - x["operating_tax_rate"])
        capital = (x["capital_start"] + x["capital_end"]) / 2
        equity = (x["equity_start"] + x["equity_end"]) / 2
        unrestricted = x["cash"] - x["restricted_cash"]
        excess = unrestricted - x["required_cash"]
        fcf = x["cfo"] - x["cash_capex"]
        market_cap = x["price"] * x["current_shares"]
        eps = x["common_net_profit"] / x["weighted_diluted_shares"]
        self.assert_numeric("snapshot-standard-ratios", {
            "revenue_growth": x["revenue"] / x["revenue_prior"] - 1,
            "gross_margin": x["gross_profit"] / x["revenue"],
            "operating_margin": x["ebit"] / x["revenue"],
            "net_margin": x["common_net_profit"] / x["revenue"],
            "nopat": nopat, "average_capital": capital, "roic": nopat / capital,
            "roe": x["common_net_profit"] / equity,
            "unrestricted_cash": unrestricted, "excess_cash": excess,
            "net_debt_unrestricted_basis": x["debt"] - unrestricted,
            "fcf_proxy": fcf, "market_cap": market_cap, "eps": eps,
            "pe": x["price"] / eps, "pb": market_cap / x["equity_end"],
            "fcf_proxy_yield": fcf / market_cap,
            "adjusted_ev": market_cap + x["debt"] - excess,
        })

    def test_pretax_return_is_not_aftertax_roic(self):
        x = self.by_id["snapshot-pretax-is-not-roic"]["inputs"]
        capital = (x["capital_start"] + x["capital_end"]) / 2
        nopat = x["ebit"] * (1 - x["tax_rate"])
        self.assert_numeric("snapshot-pretax-is-not-roic", {
            "average_capital": capital, "pretax_return": x["ebit"] / capital,
            "nopat": nopat, "roic": nopat / capital,
        })

    def test_current_and_weighted_shares_do_not_cancel(self):
        x = self.by_id["snapshot-share-basis-reconciliation"]["inputs"]
        eps = x["common_net_profit"] / x["weighted_diluted_shares"]
        cap = x["price"] * x["current_shares"]
        self.assert_numeric("snapshot-share-basis-reconciliation", {
            "eps": eps, "market_cap": cap,
            "price_over_reported_eps": x["price"] / eps,
            "market_cap_over_profit": cap / x["common_net_profit"],
        })
        self.assertNotEqual(x["price"] / eps, cap / x["common_net_profit"])

    def test_operating_value_and_liquidation_are_different_states(self):
        x = self.by_id["snapshot-assets-not-added-twice"]["inputs"]
        excess = x["cash"] - x["required_cash"]
        value = x["operating_value"] + excess - x["debt"] - x["legal_claim"]
        liquidation = (x["cash"] + x["other_liquidation_recovery"] - x["debt"]
                       - x["legal_claim"] - x["closure_cost"])
        self.assert_numeric("snapshot-assets-not-added-twice", {
            "excess_cash": excess, "going_concern_equity": value,
            "liquidation_equity": liquidation,
            "discount_to_value": (value - x["equity_price"]) / value,
            "upside_from_price": value / x["equity_price"] - 1,
        })

    def test_small_revenue_exposure_can_have_large_profit_effect(self):
        x = self.by_id["snapshot-panic-exposure-is-not-revenue-share"]["inputs"]
        revenue = x["affected_revenue"] + x["other_revenue"]
        contribution = x["affected_revenue"] - x["affected_avoidable_cost"]
        profit = (revenue - x["affected_avoidable_cost"]
                  - x["other_avoidable_cost"] - x["fixed_cost"])
        stressed = profit - contribution
        self.assert_numeric("snapshot-panic-exposure-is-not-revenue-share", {
            "initial_operating_profit": profit, "stressed_operating_profit": stressed,
            "revenue_loss_ratio": x["affected_revenue"] / revenue,
            "profit_loss_ratio": (profit - stressed) / profit,
        })


if __name__ == "__main__":
    unittest.main()
