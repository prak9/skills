from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = SKILL_ROOT / "scripts" / "calculate_gf_dma.py"


class GfDmaCalculatorTests(unittest.TestCase):
    def run_score(self, data: dict) -> dict:
        with tempfile.TemporaryDirectory() as directory:
            input_path = Path(directory) / "input.json"
            input_path.write_text(json.dumps(data), encoding="utf-8")
            process = subprocess.run(
                [sys.executable, "-B", str(SCRIPT), str(input_path)],
                check=False,
                capture_output=True,
                text=True,
            )
        self.assertEqual(0, process.returncode, process.stderr)
        return json.loads(process.stdout)

    @staticmethod
    def valid_input() -> dict:
        return {
            "growth_match": {
                "fundamental_speed_63d": 0.20,
                "dma_speeds_63d": {"50": 0.20, "100": 0.18},
            },
            "divergence": {
                "d20": 0.04,
                "d50": 0.08,
                "d100": 0.15,
                "d200": 0.25,
                "z20": 1.5,
                "fundamentals_stable_or_improving": True,
                "revisions_nonnegative": True,
            },
            "parallel": {
                "price_daily_slope_5d": 0.0011,
                "dma50_daily_slope_5d": 0.0010,
            },
            "revision": {
                "revenue_30d": 0.03,
                "eps_30d": 0.04,
                "guide_vs_consensus": 0.02,
            },
        }

    def test_valid_input_produces_reproducible_modules_but_no_aggregate(self) -> None:
        first = self.run_score(self.valid_input())
        second = self.run_score(self.valid_input())

        self.assertEqual(first, second)
        self.assertFalse(first["aggregate_enabled"])
        self.assertEqual("gf-dma-v1", first["heuristic_version"])
        self.assertIsNone(first["health_score"])
        self.assertEqual("N/A", first["state"])
        self.assertEqual([], first["missing_modules"])
        self.assertTrue(all(module["score"] is not None for module in first["modules"].values()))

    def test_two_negative_slopes_are_not_treated_as_healthy_parallelism(self) -> None:
        data = self.valid_input()
        data["parallel"] = {
            "price_daily_slope_5d": -0.001,
            "dma50_daily_slope_5d": -0.001,
        }

        result = self.run_score(data)

        self.assertFalse(result["aggregate_enabled"])
        self.assertIsNone(result["health_score"])
        self.assertIsNone(result["modules"]["parallel"]["score"])
        self.assertIn("positive", result["modules"]["parallel"]["reason"])

    def test_near_zero_dma_slope_returns_na(self) -> None:
        data = self.valid_input()
        data["parallel"]["dma50_daily_slope_5d"] = 0.000001

        result = self.run_score(data)

        self.assertFalse(result["aggregate_enabled"])
        self.assertIsNone(result["modules"]["parallel"]["score"])
        self.assertIn("near zero", result["modules"]["parallel"]["reason"])

    def test_impossible_price_divergences_return_na(self) -> None:
        for field in ("d20", "d50", "d100", "d200"):
            for value in (-1.0, -1.1):
                with self.subTest(field=field, value=value):
                    data = self.valid_input()
                    data["divergence"][field] = value
                    module = self.run_score(data)["modules"]["divergence"]
                    self.assertIsNone(module["score"])
                    self.assertIn(field, module["reason"])

    def test_divergence_and_atr_distance_must_share_sign_and_zero(self) -> None:
        for d20, z20 in ((0.04, -1.5), (-0.04, 1.5), (0, 1.5), (0.04, 0)):
            with self.subTest(d20=d20, z20=z20):
                data = self.valid_input()
                data["divergence"].update(d20=d20, z20=z20)
                module = self.run_score(data)["modules"]["divergence"]
                self.assertIsNone(module["score"])
                self.assertIn("d20", module["reason"])
                self.assertIn("z20", module["reason"])

    def test_valid_negative_and_zero_divergence_are_scorable(self) -> None:
        for d20, z20 in ((-0.99, -100), (0, 0)):
            with self.subTest(d20=d20, z20=z20):
                data = self.valid_input()
                data["divergence"].update(d20=d20, z20=z20)
                self.assertIsNotNone(self.run_score(data)["modules"]["divergence"]["score"])

    def test_five_day_slopes_cannot_represent_zero_or_negative_prices(self) -> None:
        for field in ("price_daily_slope_5d", "dma50_daily_slope_5d"):
            for value in (-0.2, -0.3):
                with self.subTest(field=field, value=value):
                    data = self.valid_input()
                    data["parallel"][field] = value
                    module = self.run_score(data)["modules"]["parallel"]
                    self.assertIsNone(module["score"])
                    self.assertIn(field, module["reason"])


if __name__ == "__main__":
    unittest.main()
