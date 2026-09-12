from __future__ import annotations

import importlib.util
import json
import math
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "calculate_pe_implied_growth.py"
SPEC = importlib.util.spec_from_file_location("pe_implied_growth", SCRIPT)
CALCULATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CALCULATOR)


class PeImpliedGrowthTests(unittest.TestCase):
    def inputs(self, **overrides):
        return {"base_eps": 5, "years": 10, "cost_of_equity": 0.12,
                "cash_conversion": 0.8, "terminal_cash_conversion": 0.9,
                "terminal_growth": 0.03, "pe": 20, **overrides}

    def test_inverse_example_and_capital_efficiency_diagnostics(self):
        result = CALCULATOR.calculate(self.inputs())
        self.assertEqual(result["status"], "ok")
        self.assertAlmostEqual(result["growth"], 0.1323821032773166, places=9)
        self.assertAlmostEqual(result["valuation"]["price"], 100, places=7)
        self.assertAlmostEqual(result["valuation"]["terminal_value_share"], 0.5748532245, places=9)
        self.assertAlmostEqual(result["diagnostics"]["first_stage"]["required_incremental_equity_return"], 0.6619105164, places=8)
        self.assertAlmostEqual(result["diagnostics"]["terminal_stage"]["required_incremental_equity_return"], 0.3)
        self.assertLess(abs(result["solver"]["residual_pe"]), 2e-9)

    def test_forward_example(self):
        inputs = self.inputs(growth=0.08)
        del inputs["pe"]
        result = CALCULATOR.calculate(inputs)
        self.assertAlmostEqual(result["valuation"]["base_pe"], 13.745188421108189)
        self.assertAlmostEqual(result["valuation"]["price"], 68.72594210554095)

    def test_forward_pe_is_converted_using_supplied_eps_ratio(self):
        result = CALCULATOR.calculate(self.inputs(pe_basis="forward", forward_eps_ratio=1.2))
        self.assertEqual(result["target_base_pe"], 24)
        self.assertAlmostEqual(result["valuation"]["price"], 120, places=7)
        self.assertAlmostEqual(result["growth"], CALCULATOR.calculate(self.inputs(pe=24))["growth"])

    def test_one_at_a_time_sensitivities_keep_the_price_hurdle(self):
        cases = [({"cost_of_equity": 0.10}, 0.0920162997),
                 ({"cost_of_equity": 0.14}, 0.1686865606),
                 ({"cash_conversion": 0.60}, 0.1474963321)]
        result = CALCULATOR.calculate(self.inputs(scenarios=[
            {"name": str(index), "overrides": change} for index, (change, _) in enumerate(cases)
        ]))
        for scenario, (_, expected) in zip(result["scenarios"], cases):
            self.assertAlmostEqual(scenario["result"]["growth"], expected, places=9)
            self.assertEqual(scenario["result"]["target_base_pe"], 20)

    def test_duration_sensitivity_and_joint_scenario(self):
        result = CALCULATOR.calculate(self.inputs(scenarios=[
            {"name": "shorter", "overrides": {"years": 5}},
            {"name": "joint", "overrides": {"cost_of_equity": 0.14, "cash_conversion": 0.6}},
        ]))
        for scenario in result["scenarios"]:
            self.assertGreater(scenario["result"]["growth"], result["growth"])

    def test_decline_then_recovery_is_explicit(self):
        result = CALCULATOR.calculate(self.inputs(pe=5))
        self.assertAlmostEqual(result["growth"], -0.06720639397, places=9)
        self.assertTrue(result["diagnostics"]["contraction_then_terminal_recovery"])
        self.assertIsNone(result["diagnostics"]["first_stage"]["required_incremental_equity_return"])

    def test_no_reinvestment_does_not_create_fake_required_return(self):
        for growth in (0, 0.1):
            inputs = self.inputs(growth=growth, cash_conversion=1, terminal_cash_conversion=1)
            del inputs["pe"]
            result = CALCULATOR.calculate(inputs)
            self.assertEqual(result["status"], "ok")
            for stage in ("first_stage", "terminal_stage"):
                self.assertIsNone(result["diagnostics"][stage]["required_incremental_equity_return"])

    def test_q_equals_one_and_one_year_terminal_timing(self):
        inputs = self.inputs(growth=0.12, years=1)
        del inputs["pe"]
        result = CALCULATOR.calculate(inputs)
        self.assertAlmostEqual(result["valuation"]["base_pe"], 0.8 + 0.9 * 1.03 / 0.09)

    def test_terminal_only_and_finite_life_only_cash_flows(self):
        for c, ct in ((0, 0.9), (0.8, 0)):
            with self.subTest(c=c, ct=ct):
                result = CALCULATOR.calculate(self.inputs(cash_conversion=c, terminal_cash_conversion=ct))
                self.assertEqual(result["status"], "ok")
                self.assertAlmostEqual(result["valuation"]["terminal_value_share"], 1 if c == 0 else 0)

    def test_unbracketed_is_not_a_clipped_growth_or_impossibility_claim(self):
        result = CALCULATOR.calculate(self.inputs(growth_bounds=[-0.1, 0.1]))
        self.assertEqual(result["status"], "unbracketed")
        self.assertIsNone(result["growth"])
        self.assertIsNone(result["valuation"])
        self.assertIn("not proof", result["reason"])

    def test_known_round_trip_grid(self):
        for growth in (-0.5, 0, 0.12, 0.5):
            inputs = self.inputs(growth=growth)
            del inputs["pe"]
            forward = CALCULATOR.calculate(inputs)
            inverse = CALCULATOR.calculate(self.inputs(pe=forward["valuation"]["base_pe"]))
            self.assertAlmostEqual(inverse["growth"], growth, places=9)

    def test_invalid_domains_and_ambiguous_bases_are_rejected(self):
        cases = [{"base_eps": 0}, {"base_eps": -1}, {"pe": 0}, {"pe": None},
                 {"years": True}, {"years": 1.5}, {"years": 101},
                 {"cost_of_equity": 0.03}, {"cost_of_equity": 0},
                 {"terminal_growth": -1}, {"cash_conversion": -0.1},
                 {"cash_conversion": 1.1}, {"cash_conversion": 0, "terminal_cash_conversion": 0},
                 {"cost_of_equity": math.nan}, {"base_eps": math.inf},
                 {"pe_basis": "forward"}, {"forward_eps_ratio": 1.2},
                 {"pe_basis": "forward", "forward_eps_ratio": 0},
                 {"growth_bounds": [-1, 1]}, {"growth_bounds": [1, 0]},
                 {"growth": 0.08}, {"currency_guess": "USD"}]
        for override in cases:
            with self.subTest(override=override), self.assertRaises(ValueError):
                CALCULATOR.calculate(self.inputs(**override))
        for data in ([], {}, {key: value for key, value in self.inputs().items() if key != "base_eps"}):
            with self.subTest(data=data), self.assertRaises(ValueError):
                CALCULATOR.calculate(data)

    def test_invalid_scenario_is_not_silently_ignored(self):
        for scenarios in (None, [{"name": "changed", "overrides": {"pe": 10}}],
                          [{"name": "invalid", "overrides": {"cost_of_equity": 0.01}}]):
            with self.subTest(scenarios=scenarios), self.assertRaises(ValueError):
                CALCULATOR.calculate(self.inputs(scenarios=scenarios))

    def test_cli_returns_strict_json_and_invalid_input_fails_without_result(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "input.json"
            path.write_text(json.dumps(self.inputs()), encoding="utf-8")
            args = [sys.executable, "-B", str(SCRIPT), str(path)]
            process = subprocess.run(args, capture_output=True, text=True)
            self.assertEqual(process.returncode, 0, process.stderr)
            self.assertEqual(json.loads(process.stdout)["status"], "ok")
            path.write_text(json.dumps(self.inputs(cost_of_equity=0.03)), encoding="utf-8")
            process = subprocess.run(args, capture_output=True, text=True)
            self.assertEqual(process.returncode, 2)
            self.assertEqual(process.stdout, "")
            self.assertIn("cost_of_equity", process.stderr)


if __name__ == "__main__":
    unittest.main()
