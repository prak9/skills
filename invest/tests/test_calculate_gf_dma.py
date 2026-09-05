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


if __name__ == "__main__":
    unittest.main()
