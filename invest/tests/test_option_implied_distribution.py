from __future__ import annotations

import importlib.util
import json
import math
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "calculate_option_implied_distribution.py"
SPEC = importlib.util.spec_from_file_location("option_implied_distribution", SCRIPT)
CALCULATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CALCULATOR)


class OptionImpliedDistributionTests(unittest.TestCase):
    def inputs(self, **overrides):
        data = {
            "quote_timestamp": "2026-10-11T16:00:00-04:00",
            "expiration": "2027-10-15",
            "spot": 100,
            "risk_free_rate": 0,
            "option_style": "european_equivalent",
            "price_basis": "arbitrage_free_mid_fit",
            "calls": [
                {"strike": 80, "call_price": 30},
                {"strike": 100, "call_price": 15},
                {"strike": 120, "call_price": 5},
            ],
        }
        data.update(overrides)
        return data

    def test_known_vertical_spreads_and_range_probabilities(self):
        result = CALCULATOR.calculate(self.inputs())
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["horizon_note"], "approximately_one_year")
        self.assertEqual([row["terminal_price_threshold"] for row in result["threshold_probabilities"]], [90, 110])
        self.assertEqual([row["probability_above"] for row in result["threshold_probabilities"]], [0.75, 0.5])
        self.assertEqual([row["probability"] for row in result["range_probabilities"]], [0.25, 0.25, 0.5])
        self.assertAlmostEqual(sum(row["probability"] for row in result["range_probabilities"]), 1)

    def test_rate_discounting_and_unsorted_strikes(self):
        raw = self.inputs(risk_free_rate=0.04)
        raw["calls"] = list(reversed(raw["calls"]))
        result = CALCULATOR.calculate(raw)
        expected = math.exp(0.04 * result["inputs"]["time_years_act_365_25"]) * 0.75
        self.assertAlmostEqual(result["threshold_probabilities"][0]["probability_above"], expected)

    def test_outside_one_year_window_is_labeled(self):
        result = CALCULATOR.calculate(self.inputs(expiration="2027-01-15"))
        self.assertEqual(result["horizon_note"], "outside_9_to_15_month_window")

    def test_rejects_raw_american_duplicate_and_bad_schema(self):
        cases = [
            {"option_style": "american"},
            {"calls": [{"strike": 80, "call_price": 30}, {"strike": 80, "call_price": 20}, {"strike": 100, "call_price": 10}]},
            {"calls": [{"strike": 80, "call_price": 30}, {"strike": 100, "call_price": 15}]},
            {"spot": 0},
            {"risk_free_rate": math.nan},
            {"expiration": "2026-10-10"},
            {"quote_timestamp": "2026-10-11T16:00:00"},
            {"extra": 1},
        ]
        for override in cases:
            with self.subTest(override=override), self.assertRaises(ValueError):
                CALCULATOR.calculate(self.inputs(**override))

    def test_rejects_vertical_and_convexity_arbitrage(self):
        too_steep = self.inputs(calls=[
            {"strike": 80, "call_price": 30},
            {"strike": 100, "call_price": 5},
            {"strike": 120, "call_price": 1},
        ])
        nonconvex = self.inputs(calls=[
            {"strike": 80, "call_price": 25},
            {"strike": 100, "call_price": 20},
            {"strike": 120, "call_price": 10},
        ])
        for data in (too_steep, nonconvex):
            with self.assertRaises(ValueError):
                CALCULATOR.calculate(data)

    def test_cli_emits_strict_json_and_errors_cleanly(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "input.json"
            path.write_text(json.dumps(self.inputs()), encoding="utf-8")
            args = [sys.executable, "-B", str(SCRIPT), str(path)]
            process = subprocess.run(args, capture_output=True, text=True)
            self.assertEqual(process.returncode, 0, process.stderr)
            self.assertEqual(json.loads(process.stdout)["status"], "ok")
            path.write_text(json.dumps(self.inputs(option_style="american")), encoding="utf-8")
            process = subprocess.run(args, capture_output=True, text=True)
            self.assertEqual(process.returncode, 2)
            self.assertEqual(process.stdout, "")
            self.assertIn("American", process.stderr)


if __name__ == "__main__":
    unittest.main()
