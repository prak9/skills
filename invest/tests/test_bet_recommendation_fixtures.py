"""Check betting-fixture arithmetic, not live forecasts or agent behavior."""

from __future__ import annotations

import json
from pathlib import Path
import unittest


PACKET = Path(__file__).resolve().parents[1] / "evals/bet-recommendation-cases.jsonl"


class BetRecommendationFixtureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.cases = [json.loads(line) for line in PACKET.read_text().splitlines()]
        cls.by_id = {case["id"]: case for case in cls.cases}

    def assert_numeric(self, case_id: str, calculated: dict[str, float]) -> None:
        expected = self.by_id[case_id]["numeric_checks"]
        self.assertEqual(set(expected), set(calculated))
        for name, value in calculated.items():
            with self.subTest(case=case_id, metric=name):
                self.assertAlmostEqual(expected[name], value, places=8)

    def test_packet_has_unique_scoped_cases(self) -> None:
        self.assertEqual(13, len(self.cases))
        self.assertEqual(len(self.cases), len(self.by_id))
        for case in self.cases:
            with self.subTest(case=case["id"]):
                self.assertEqual("development", case["split"])
                self.assertEqual("invest", case["skill"])
                self.assertTrue(case["prompt"] and case["expected_behavior"])
                self.assertTrue(case["criteria"])

    def test_book_example_has_positive_expectation_but_high_loss_probability(self) -> None:
        x = self.by_id["bet-book-probability-versus-odds"]["inputs"]
        ev = x["p"] * x["gain"] - (1 - x["p"]) * x["loss"]
        self.assert_numeric("bet-book-probability-versus-odds", {
            "expected_profit": ev,
            "expected_return": ev / x["stake"],
            "break_even_probability": x["loss"] / (x["gain"] + x["loss"]),
            "loss_probability": 1 - x["p"],
            "net_odds": x["gain"] / x["loss"],
            "decimal_odds": 1 + x["gain"] / x["loss"],
        })

    def test_three_states_use_entry_cost_and_net_terminal_wealth(self) -> None:
        x = self.by_id["bet-three-state-net-hurdle"]["inputs"]
        outlay = x["price"] + x["entry_cost"]
        wealth = [price + x["distribution"] - x["exit_cost"] for price in x["terminal_prices"]]
        returns = [amount / outlay - 1 for amount in wealth]
        mean = sum(p * r for p, r in zip(x["probabilities"], returns))
        self.assert_numeric("bet-three-state-net-hurdle", {
            "initial_outlay": outlay,
            "bull_return": returns[0], "base_return": returns[1], "bear_return": returns[2],
            "expected_return": mean,
            "expected_excess": mean - x["hurdle_return"],
            "loss_probability": sum(p for p, r in zip(x["probabilities"], returns) if r < 0),
        })
        self.assertAlmostEqual(sum(x["probabilities"]), 1)

    def test_unknown_probability_yields_thresholds_not_an_estimated_mean(self) -> None:
        x = self.by_id["bet-unidentified-probability"]["inputs"]
        self.assertIsNone(x["supported_probability"])
        total = x["gain"] + x["loss"]
        self.assert_numeric("bet-unidentified-probability", {
            "zero_ev_probability": x["loss"] / total,
            "hurdle_probability": (x["loss"] + x["hurdle_gain"]) / total,
            "ev_at_p03": .3 * total - x["loss"],
            "ev_at_p04": .4 * total - x["loss"],
            "ev_at_p06": .6 * total - x["loss"],
        })

    def test_high_win_rate_can_still_have_negative_expectation(self) -> None:
        x = self.by_id["bet-high-win-negative-ev"]["inputs"]
        self.assert_numeric("bet-high-win-negative-ev", {
            "expected_profit": x["p"] * x["gain"] - (1 - x["p"]) * x["loss"],
            "break_even_probability": x["loss"] / (x["gain"] + x["loss"]),
        })

    def test_loss_budget_limits_total_weight_not_only_the_next_order(self) -> None:
        x = self.by_id["bet-risk-cap-is-not-target"]["inputs"]
        loss_cap = max(0, (x["loss_budget"] - x["other_joint_loss"]) / x["issuer_stress_loss"])
        cap = min(loss_cap, x["concentration_cap"], x["liquidity_cap"], x["funding_cap"])
        capacity = max(0, cap - x["current_weight"])
        self.assert_numeric("bet-risk-cap-is-not-target", {
            "expected_return": x["p"] * x["upside_return"] - (1 - x["p"]) * x["downside_loss"],
            "loss_cap": loss_cap, "total_weight_cap": cap, "incremental_capacity": capacity,
            "incremental_currency_capacity": capacity * x["nav"],
            "joint_loss_at_cap": x["other_joint_loss"] + cap * x["issuer_stress_loss"],
        })

    def test_quote_change_can_reverse_edge_without_changing_probabilities(self) -> None:
        x = self.by_id["bet-price-only-edge-update"]["inputs"]
        wealth = x["p"] * x["bull_wealth"] + (1 - x["p"]) * x["bear_wealth"]
        spread = x["bull_wealth"] - x["bear_wealth"]
        self.assert_numeric("bet-price-only-edge-update", {
            "expected_terminal_wealth": wealth,
            "old_expected_return": wealth / x["old_price"] - 1,
            "new_expected_return": wealth / x["new_price"] - 1,
            "old_zero_ev_probability": (x["old_price"] - x["bear_wealth"]) / spread,
            "new_zero_ev_probability": (x["new_price"] - x["bear_wealth"]) / spread,
            "hurdle_price_limit": wealth / (1 + x["hurdle_return"]),
        })

    def test_positive_ev_does_not_resolve_a_funding_deadline(self) -> None:
        x = self.by_id["bet-positive-ev-funding-veto"]["inputs"]
        self.assert_numeric("bet-positive-ev-funding-veto", {
            "expected_profit": x["p"] * x["gain"] - (1 - x["p"]) * x["loss"],
            "cash_shortfall": x["near_term_debt_due"] - x["available_cash"],
        })
        self.assertLess(x["months_until_debt_due"], x["months_until_payoff"])

    def test_narrow_eps_request_remains_narrow(self) -> None:
        x = self.by_id["bet-narrow-calculation-control"]["inputs"]
        self.assert_numeric("bet-narrow-calculation-control", {
            "eps": x["common_profit"] / x["weighted_diluted_shares"],
        })

    def test_sequential_posterior_updates_reach_the_same_bet_payoffs(self) -> None:
        x = self.by_id["bayes-sequential-evidence-to-bet"]["inputs"]
        p = x["prior_probability"]
        posteriors = []
        for likelihood_a, likelihood_b in x["conditional_likelihoods"]:
            p = p * likelihood_a / (p * likelihood_a + (1 - p) * likelihood_b)
            posteriors.append(p)
        ev = [prob * x["gain"] - (1 - prob) * x["loss"] for prob in posteriors]
        self.assert_numeric("bayes-sequential-evidence-to-bet", {
            "posterior_1": posteriors[0], "posterior_2": posteriors[1], "posterior_3": posteriors[2],
            "ev_1": ev[0], "ev_2": ev[1], "ev_3": ev[2],
            "zero_ev_probability": x["loss"] / (x["gain"] + x["loss"]),
            "hurdle_probability": (x["loss"] + x["hurdle_gain"]) / (x["gain"] + x["loss"]),
        })

    def test_conditional_likelihood_prevents_double_credit_for_a_shared_cause(self) -> None:
        x = self.by_id["bayes-conditional-evidence-not-independent"]["inputs"]
        p = x["prior_probability"]
        a, b = x["first_likelihoods"]
        posterior = p * a / (p * a + (1 - p) * b)
        a, b = x["next_conditional_likelihoods"]
        next_posterior = posterior * a / (posterior * a + (1 - posterior) * b)
        a, b = x["next_marginal_likelihoods"]
        naive = posterior * a / (posterior * a + (1 - posterior) * b)
        self.assert_numeric("bayes-conditional-evidence-not-independent", {
            "posterior_after_first": posterior, "posterior_after_next": next_posterior,
        })
        self.assertNotAlmostEqual(next_posterior, naive)

    def test_repeated_reports_of_one_observation_are_counted_once(self) -> None:
        x = self.by_id["bayes-mirrored-reports-one-observation"]["inputs"]
        seen = set()
        p = x["prior_probability"]
        for event in x["originating_observations"]:
            if event in seen:
                continue
            seen.add(event)
            a, b = x["likelihoods"]
            p = p * a / (p * a + (1 - p) * b)
        self.assert_numeric("bayes-mirrored-reports-one-observation", {
            "posterior": p, "independent_observations": len(seen),
        })

    def test_missing_prior_or_likelihood_is_not_a_numeric_zero(self) -> None:
        self.assertIsNone(self.by_id["bayes-missing-prior-no-reconstruction"]["inputs"]["prior_probability"])
        self.assertIsNone(self.by_id["bayes-good-news-no-likelihood-basis"]["inputs"]["supported_likelihood_ratio"])


if __name__ == "__main__":
    unittest.main()
