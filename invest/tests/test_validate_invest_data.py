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

    def test_bad_metric_types_return_structured_failures_in_linked_checks(self) -> None:
        for field in ("classification", "unit", "currency", "period", "basis"):
            for value in ([], {}):
                with self.subTest(field=field, value=value):
                    bad = self.metric("component", 100)
                    bad[field] = value
                    result = self.run_validation({
                        "metrics": [bad, self.metric("total", 100)],
                        "checks": {
                            "sums": [{"components": ["component"], "total": "total"}],
                            "basis_groups": [{"items": ["component", "total"], "fields": [field]}],
                        },
                    })
                    self.assertEqual("fail", result["status"])
                    self.assertTrue(any(item["code"] == f"invalid_{field}" for item in result["findings"]))

    def test_schema_version_requires_integer_one(self) -> None:
        for version in (True, 1.0, [], {}):
            with self.subTest(version=version):
                result = self.run_validation({"schema_version": version, "metrics": [self.metric("x", 1)]})
                self.assertEqual("fail", result["status"])
                self.assertTrue(any(item["code"] == "unsupported_schema" for item in result["findings"]))

    def test_v2_bounded_publication_time(self) -> None:
        metric = self.metric("revenue", 100)
        window = {"earliest": "2024-02-01T00:00:00+08:00",
                  "latest": "2024-02-02T00:00:00+08:00",
                  "reason": "Only the Hong Kong publication date is known"}
        metric["source"].update(published_at=window, available_at=window)
        for cutoff, expected in (("2024-02-02T01:00:00+08:00", "pass"),
                                 ("2024-02-01T12:00:00+08:00", "fail"),
                                 ("2024-01-31T12:00:00+08:00", "fail")):
            with self.subTest(cutoff=cutoff):
                result = self.run_validation({"schema_version": 2, "decision_time": cutoff, "metrics": [metric]})
                self.assertEqual(expected, result["status"])
        result = self.run_validation({"schema_version": 1, "metrics": [metric]})
        self.assertEqual("fail", result["status"])

    def test_v2_unknown_time_does_not_fabricate_precision(self) -> None:
        metric = self.metric("revenue", 100)
        metric["source"].update(published_at=None, available_at=None,
                                time_missing_reason="Only an undated original PDF is accessible")
        data = {"schema_version": 2, "metrics": [metric]}
        result = self.run_validation(data)
        self.assertEqual("pass", result["status"])
        self.assertTrue(any(f["code"] == "unknown_source_time" for f in result["findings"]))
        data["decision_time"] = "2024-02-02T00:00:00Z"
        self.assertEqual("fail", self.run_validation(data)["status"])
        del data["decision_time"]
        del metric["source"]["time_missing_reason"]
        self.assertEqual("fail", self.run_validation(data)["status"])

    def test_v2_invalid_time_windows(self) -> None:
        for window in ({"earliest": "2024-02-02T00:00:00Z", "latest": "2024-02-01T00:00:00Z", "reason": "date"},
                       {"earliest": "2024-02-01", "latest": "2024-02-02", "reason": "date"},
                       {"earliest": "2024-02-01T00:00:00Z", "latest": "2024-02-02T00:00:00Z"}):
            with self.subTest(window=window):
                metric = self.metric("r", 1)
                metric["source"]["published_at"] = window
                self.assertEqual("fail", self.run_validation({"schema_version": 2, "metrics": [metric]})["status"])

    def difference_data(self) -> dict:
        metrics = [self.metric("ytd9", 90), self.metric("ytd6", 50), self.metric("q3", 40)]
        for metric, start, end in zip(metrics, ("2023-01-01", "2023-01-01", "2023-07-01"),
                                      ("2023-09-30", "2023-06-30", "2023-09-30")):
            metric["period"] = f"{start}/{end}"
            metric["statement"] = {"concept": "operating_cash_flow", "kind": "flow", "start": start,
                                   "end": end, "scope": "consolidated", "accounting_standard": "US-GAAP",
                                   "version_basis": "original-unrestated", "security_basis": "not_applicable"}
        metrics[2]["derivation"] = {"operation": "subtract", "inputs": ["ytd9", "ytd6"]}
        return {"schema_version": 2, "metrics": metrics,
                "checks": {"period_differences": [{"cumulative": "ytd9", "prior_cumulative": "ytd6", "result": "q3"}]}}

    def test_same_basis_cumulative_cash_flow_can_be_differenced(self) -> None:
        result = self.run_validation(self.difference_data())
        self.assertEqual("pass", result["status"], result)
        self.assertEqual(1, result["checks_run"]["period_differences"])

    def test_nonadditive_metrics_cannot_be_differenced(self) -> None:
        for kind in ("instant", "ratio", "per_share", "weighted_average"):
            with self.subTest(kind=kind):
                data = self.difference_data()
                for metric in data["metrics"]:
                    metric["statement"]["kind"] = kind
                result = self.run_validation(data)
                self.assertEqual("fail", result["status"])
                self.assertTrue(any(f["code"] == "nonadditive_difference" for f in result["findings"]))

    def test_period_difference_rejects_incompatible_context_and_bad_results(self) -> None:
        for field, value in (("scope", "segment_a"), ("version_basis", "restated"),
                             ("security_basis", "ADS"), ("concept", "capex"),
                             ("accounting_standard", "IFRS"), ("start", "2023-02-01"),
                             ("end", "2023-12-31"), ("start", "bad-date")):
            with self.subTest(field=field, value=value):
                data = self.difference_data()
                data["metrics"][1]["statement"][field] = value
                self.assertEqual("fail", self.run_validation(data)["status"])
        for value in (None, 41):
            data = self.difference_data()
            data["metrics"][2]["value"] = value
            self.assertEqual("fail", self.run_validation(data)["status"])
        data = self.difference_data()
        del data["metrics"][2]["derivation"]
        self.assertEqual("fail", self.run_validation(data)["status"])

    def test_difference_is_not_silently_accepted_under_v1(self) -> None:
        data = self.difference_data()
        data["schema_version"] = 1
        result = self.run_validation(data)
        self.assertEqual("fail", result["status"])
        self.assertTrue(any(f["code"] == "unsupported_check" for f in result["findings"]))

    def test_difference_bad_result_window_or_structure_returns_findings(self) -> None:
        data = self.difference_data()
        data["metrics"][2]["statement"]["start"] = "2023-06-30"
        self.assertEqual("fail", self.run_validation(data)["status"])
        for checks in (None, {}, [None], [{"cumulative": [], "prior_cumulative": "x", "result": "q3"}]):
            with self.subTest(checks=checks):
                data = self.difference_data()
                data["checks"]["period_differences"] = checks
                self.assertEqual("fail", self.run_validation(data)["status"])
        for context in (None, [], {"kind": "flow"}):
            data = self.difference_data()
            data["metrics"][1]["statement"] = context
            self.assertEqual("fail", self.run_validation(data)["status"])

    def test_restatement_after_cutoff_cannot_enter_period_difference(self) -> None:
        data = self.difference_data()
        data["decision_time"] = "2024-02-02T00:00:00Z"
        data["metrics"][1]["source"]["available_at"] = "2024-03-01T00:00:00Z"
        result = self.run_validation(data)
        self.assertEqual("fail", result["status"])
        self.assertTrue(any(f["code"] == "point_in_time_violation" for f in result["findings"]))


if __name__ == "__main__":
    unittest.main()
