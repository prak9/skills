from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = SKILL_ROOT / "scripts" / "validate_invest_data.py"


class InvestDataContractTests(unittest.TestCase):
    def run_validation(self, data: dict) -> dict:
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
    def metric(metric_id: str, value: float | None, *, available_at: str = "2024-02-01T12:00:00Z") -> dict:
        return {
            "id": metric_id,
            "name": metric_id,
            "value": value,
            "unit": "USD million",
            "currency": "USD",
            "period": "FY2023",
            "basis": "GAAP",
            "classification": "reported_fact",
            "source": {
                "reference": "https://example.com/filing",
                "document_type": "10-K",
                "published_at": "2024-02-01T10:00:00Z",
                "available_at": available_at,
                "locator": "p. 42",
            },
            "missing_reason": "not disclosed" if value is None else None,
        }

    def test_valid_contract_checks_sum_growth_and_probability(self) -> None:
        data = {
            "schema_version": 1,
            "as_of": "2024-02-02T00:00:00Z",
            "decision_time": "2024-02-02T00:00:00Z",
            "metrics": [
                self.metric("segment_a", 60),
                self.metric("segment_b", 40),
                self.metric("revenue", 100),
                self.metric("revenue_prior", 80),
                {**self.metric("bull_probability", 0.3), "unit": "decimal", "currency": None},
                {**self.metric("base_probability", 0.5), "unit": "decimal", "currency": None},
                {**self.metric("bear_probability", 0.2), "unit": "decimal", "currency": None},
            ],
            "checks": {
                "sums": [
                    {"name": "segment sum", "components": ["segment_a", "segment_b"], "total": "revenue"}
                ],
                "growth_rates": [
                    {"name": "revenue growth", "prior": "revenue_prior", "current": "revenue", "expected": 0.25}
                ],
                "probability_groups": [
                    {
                        "name": "scenario probabilities",
                        "items": ["bull_probability", "base_probability", "bear_probability"],
                    }
                ],
            },
        }

        result = self.run_validation(data)

        self.assertEqual("pass", result["status"])
        self.assertEqual([], result["findings"])

    def test_missing_value_requires_reason_and_is_not_zero(self) -> None:
        metric = self.metric("capex", None)
        metric["missing_reason"] = ""
        result = self.run_validation({"schema_version": 1, "metrics": [metric]})

        self.assertEqual("fail", result["status"])
        self.assertTrue(any(item["code"] == "missing_reason_required" for item in result["findings"]))

    def test_later_available_source_fails_historical_point_in_time(self) -> None:
        data = {
            "schema_version": 1,
            "decision_time": "2024-02-02T00:00:00Z",
            "metrics": [self.metric("revenue", 100, available_at="2024-02-03T00:00:00Z")],
        }

        result = self.run_validation(data)

        self.assertEqual("fail", result["status"])
        self.assertTrue(any(item["code"] == "point_in_time_violation" for item in result["findings"]))

    def test_mixed_basis_sum_is_rejected_before_arithmetic(self) -> None:
        gaap = self.metric("gaap_revenue", 60)
        adjusted = self.metric("adjusted_revenue", 40)
        adjusted["basis"] = "Adjusted"
        total = self.metric("total_revenue", 100)
        data = {
            "schema_version": 1,
            "metrics": [gaap, adjusted, total],
            "checks": {
                "sums": [
                    {
                        "name": "invalid mixed sum",
                        "components": ["gaap_revenue", "adjusted_revenue"],
                        "total": "total_revenue",
                    }
                ]
            },
        }

        result = self.run_validation(data)

        self.assertEqual("fail", result["status"])
        self.assertTrue(any(item["code"] == "incompatible_basis" for item in result["findings"]))

    def test_declared_basis_group_detects_mixed_currency(self) -> None:
        usd = self.metric("revenue_usd", 100)
        eur = self.metric("revenue_eur", 100)
        eur["currency"] = "EUR"
        data = {
            "schema_version": 1,
            "metrics": [usd, eur],
            "checks": {
                "basis_groups": [
                    {
                        "name": "revenue comparability",
                        "items": ["revenue_usd", "revenue_eur"],
                        "fields": ["unit", "currency", "basis"],
                    }
                ]
            },
        }

        result = self.run_validation(data)

        self.assertEqual("fail", result["status"])
        self.assertTrue(any(item["code"] == "incompatible_basis" for item in result["findings"]))


if __name__ == "__main__":
    unittest.main()
