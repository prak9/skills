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
        self.assertEqual(15, len(self.cases))
        self.assertEqual(len(self.cases), len(self.by_id))
        for case in self.cases:
            with self.subTest(case=case["id"]):
                self.assertEqual("development", case["split"])
                self.assertEqual("invest", case["skill"])
                self.assertTrue(case["prompt"] and case["expected_behavior"])
                self.assertTrue(case["criteria"])

    def test_value_line_style_preserves_per_share_and_cash_definitions(self):
        x = self.by_id["snapshot-valueline-statistical-array"]["inputs"]
        common_profit = x["parent_net_profit"] - x["preferred_dividends"]
        cash_proxy = common_profit + x["depreciation_amortization"]
        fcf = x["cfo"] - x["cash_capex"]
        eps = common_profit / x["weighted_diluted_shares"]
        self.assert_numeric("snapshot-valueline-statistical-array", {
            "sales_per_share": x["revenue"] / x["year_end_common_shares"],
            "vl_style_cash_proxy_per_share": cash_proxy / x["year_end_common_shares"],
            "reported_diluted_eps": eps,
            "declared_dividends_per_share": (
                x["common_declared_dividends"] / x["year_end_common_shares"]
            ),
            "cash_capex_per_share": x["cash_capex"] / x["year_end_common_shares"],
            "book_value_per_share": x["common_equity_end"] / x["year_end_common_shares"],
            "fcf_proxy_per_share": fcf / x["year_end_common_shares"],
            "average_annual_pe": x["average_annual_price"] / eps,
            "current_price_over_reported_eps": x["current_price"] / eps,
            "retained_to_common_equity_end_basis": (
                common_profit - x["common_declared_dividends"]
            ) / x["common_equity_end"],
            "all_dividends_to_parent_profit": (
                x["common_declared_dividends"] + x["preferred_dividends"]
            ) / x["parent_net_profit"],
        })

    def test_value_line_style_metrics_are_not_silent_accounting_substitutes(self):
        x = self.by_id["snapshot-valueline-definition-boundaries"]["inputs"]
        shares = x["year_end_common_shares"]
        self.assert_numeric("snapshot-valueline-definition-boundaries", {
            "ebit_margin": x["ebit"] / x["revenue"],
            "ebitda_style_margin": (x["ebit"] + x["depreciation_amortization"]) / x["revenue"],
            "vl_style_cash_proxy_per_share": (
                x["parent_net_profit"] + x["depreciation_amortization"]
                - x["preferred_dividends"]
            ) / shares,
            "cfo_per_share": x["cfo"] / shares,
            "fcf_proxy_per_share": (x["cfo"] - x["cash_capex"]) / shares,
            "roic": x["ebit"] * (1 - x["operating_tax_rate"]) / x["average_capital"],
            "supplied_vl_total_capital_return": x["supplied_vl_total_capital_return"],
        })

    def test_value_line_current_year_stays_incomplete_until_actually_reported(self):
        case = self.by_id["snapshot-valueline-incomplete-year"]
        self.assertEqual("incomplete_reported_period", case["current_year_status"])
        self.assertIsNone(case["inputs"]["current_year_full_year_revenue"])
        self.assertIsNone(case["inputs"]["three_to_five_year_target"])

    def test_value_line_layout_does_not_expand_an_explicit_eps_calculation(self):
        x = self.by_id["snapshot-valueline-narrow-eps"]["inputs"]
        self.assert_numeric("snapshot-valueline-narrow-eps", {
            "eps": x["common_net_profit"] / x["weighted_diluted_shares"],
        })

    def test_generic_company_snapshot_has_reconstructible_group_roic(self):
        x = self.by_id["snapshot-implicit-group-roic"]["inputs"]
        opening = (x["total_equity_start"] + x["debt_start"]
                   - x["excess_cash_start"] - x["nonoperating_assets_start"])
        closing = (x["total_equity_end"] + x["debt_end"]
                   - x["excess_cash_end"] - x["nonoperating_assets_end"])
        nopat = x["ebit"] * (1 - x["operating_tax_rate"])
        self.assert_numeric("snapshot-implicit-group-roic", {
            "capital_start": opening, "capital_end": closing,
            "average_capital": (opening + closing) / 2,
            "nopat": nopat, "roic": nopat / ((opening + closing) / 2),
            "operating_margin": x["ebit"] / x["revenue"],
            "fcf_proxy": x["cfo"] - x["cash_capex"],
        })

    def test_missing_operating_tax_supports_only_a_conditional_roic_range(self):
        x = self.by_id["snapshot-roic-tax-range"]["inputs"]
        capital = (x["capital_start"] + x["capital_end"]) / 2
        low = x["ebit"] * (1 - x["tax_rate_high"])
        high = x["ebit"] * (1 - x["tax_rate_low"])
        self.assert_numeric("snapshot-roic-tax-range", {
            "average_capital": capital, "nopat_low": low,
            "nopat_high": high, "roic_low": low / capital,
            "roic_high": high / capital,
        })

    def test_unmatured_investment_remains_in_group_capital(self):
        x = self.by_id["snapshot-roic-investment-lag"]["inputs"]
        capital = (x["capital_start"] + x["capital_end"]) / 2
        self.assert_numeric("snapshot-roic-investment-lag", {
            "average_capital": capital, "group_roic": x["nopat"] / capital,
            "conditional_mature_incremental_roic": (
                x["guided_incremental_nopat"] / x["guided_incremental_capital"]
            ),
        })

    def test_bank_uses_equity_and_asset_returns_not_industrial_capital(self):
        x = self.by_id["snapshot-bank-capital-return-alternative"]["inputs"]
        self.assert_numeric("snapshot-bank-capital-return-alternative", {
            "roe": x["common_net_profit"] / x["average_common_equity"],
            "roa": x["net_profit"] / x["average_assets"],
        })

    def test_negative_operating_capital_does_not_produce_a_meaningful_roic(self):
        case = self.by_id["snapshot-roic-negative-capital"]
        x = case["inputs"]
        capital = (x["capital_start"] + x["capital_end"]) / 2
        self.assertLessEqual(capital, 0)
        self.assertEqual("not_meaningful", case["expected_roic_status"])
        self.assert_numeric("snapshot-roic-negative-capital", {
            "average_capital": capital,
            "nopat": x["ebit"] * (1 - x["operating_tax_rate"]),
            "operating_margin": x["ebit"] / x["revenue"],
        })

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
