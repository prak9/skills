from __future__ import annotations

import importlib.util
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd


SKILL_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = SKILL_ROOT / "scripts" / "model_tuning_diagnostics.py"
SPEC = importlib.util.spec_from_file_location("model_tuning_diagnostics", SCRIPT)
diagnostics = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(diagnostics)


class ModelTuningDiagnosticsTests(unittest.TestCase):
    @staticmethod
    def write_bundle(directory: Path, start: str, end: str, *, pot: str = "0.3", manifest: str | None = None) -> None:
        directory.mkdir(parents=True, exist_ok=True)
        suffix = f"{start}-{end}"
        (directory / f"trades_{suffix}.csv").write_text(
            "account,sym,dorn,pnl,enter_d,enter_reald\n"
            "sim,eb,day,10,-2,-2\nsim,eb,day,10,-1,-1\n"
            "sim,eb,day,10,1,1\nsim,eb,day,10,2,2\n"
            "real,eb,day,5,1,1\n", encoding="utf-8",
        )
        (directory / f"winress_{suffix}.csv").write_text(
            "account,s,t,pot,dret,y,fg,sg\n"
            f"sim,eb,day,{pot},0.1,y.test_5,1,1\n"
            "real,eb,day,0.2,0.05,y.test_5,1,1\n", encoding="utf-8",
        )
        (directory / f"signals_{suffix}.csv").write_text(
            "account,sym,dorn,dir,dfactor,r_dfactor,feegate_r\n"
            "sim,eb,day,sell,-2,-2,0.1\nsim,eb,day,sell,-1,-1,0.1\n"
            "sim,eb,day,buy,1,1,0.1\nsim,eb,day,buy,2,2,0.1\n",
            encoding="utf-8",
        )
        if manifest:
            (directory / f"bundle_{suffix}.json").write_text(
                json.dumps({"status": manifest, "range": suffix}), encoding="utf-8",
            )

    def test_cli_from_actual_artifacts_layout_to_json_output(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for day in (1, 2, 3):
                self.write_bundle(root / "202609" / "artifacts", f"2026090{day}", f"2026090{day + 1}", manifest="READY")
            output = root / "diagnostics.json"
            process = subprocess.run(
                [sys.executable, "-B", str(SCRIPT), "--results-root", str(root),
                 "--account", "sim", "--real-account", "real", "--lookback", "3",
                 "--min-trades", "3", "--include-signals", "--output", str(output)],
                check=False, capture_output=True, text=True,
            )
            self.assertEqual(0, process.returncode, process.stderr)
            report = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(3, report["meta"]["bundle_count"])
            self.assertEqual(["20260901", "20260902", "20260903"], report["meta"]["dates"])
            self.assertEqual(3, report["meta"]["daily_rows_total"])
            self.assertEqual("identity_unverified", report["meta"]["identity_status"])
            self.assertEqual("identity_unverified", report["cells"][0]["identity_status"])
            self.assertEqual("all_tick", report["cells"][0]["prediction_basis"])
            self.assertEqual("monitor_no_model_change", report["cells"][0]["route"])
            self.assertTrue(all(item["manifest"] for item in report["inputs"]))

    def test_discovery_supports_root_month_and_legacy_layouts(self) -> None:
        for layout in (".", "202609", "202609/artifacts", "legacy"):
            with self.subTest(layout=layout), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                self.write_bundle(root / layout, "20260901", "20260902")
                bundles = diagnostics.discover_bundles(root, None, 3)
                self.assertEqual(["20260901"], [bundle["date"] for bundle in bundles])

    def test_duplicate_copies_do_not_displace_dates_in_lookback(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.write_bundle(root / "202609", "20260901", "20260902")
            for layout in ("202609", "202609/artifacts", "backup"):
                self.write_bundle(root / layout, "20260902", "20260903")
            bundles = diagnostics.discover_bundles(root, None, 2)
            self.assertEqual(["20260901", "20260902"], [bundle["date"] for bundle in bundles])

    def test_conflicting_same_date_bundles_require_resolution(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.write_bundle(root / "202609", "20260901", "20260902")
            self.write_bundle(root / "backup", "20260901", "20260902", pot="-0.3")
            with self.assertRaisesRegex(ValueError, "conflicting.*20260901"):
                diagnostics.discover_bundles(root, None, 3)

    def test_discovery_excludes_weekly_incomplete_and_unready_bundles(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            directory = root / "202609"
            self.write_bundle(directory, "20260901", "20260902")
            self.write_bundle(directory, "20260901", "20260908")
            self.write_bundle(directory, "20260902", "20260903", manifest="BUILDING")
            self.write_bundle(directory, "20260903", "20260904")
            (directory / "winress_20260903-20260904.csv").unlink()
            bundles = diagnostics.discover_bundles(root, "20260904", 20)
            self.assertEqual(["20260901"], [bundle["date"] for bundle in bundles])

    @staticmethod
    def daily(**overrides) -> pd.DataFrame:
        row = {
            "sym": "eb", "session": "day", "observable_contract": "y=test|fg=1|sg=1",
            "sim_trade_n": 200, "signal_trade_n": 200, "sim_pnl": 100,
            "trade_hit": 0.8, "trade_spearman": 0.3, "direction_capture": 0.4,
            "sim_pot": 0.3, "all_tick_n": 1000, "all_tick_nonzero_hit": 0.6,
            "all_tick_spearman": 0.3, "all_tick_direction_capture": 0.4,
            "real_dret": 0.1, **overrides,
        }
        return pd.DataFrame([{**row, "date": f"2026090{day}"} for day in range(1, 6)])

    def summarize(self, **overrides) -> dict:
        return diagnostics.summarize_cells(self.daily(**overrides), 3, 100)[0]

    def test_missing_sim_economics_is_insufficient(self) -> None:
        for pot in (np.nan, np.inf, -np.inf):
            with self.subTest(pot=pot):
                result = self.summarize(sim_pot=pot)
                self.assertEqual("insufficient", result["route"])
                self.assertEqual("missing", result["sim_economics_status"])
                self.assertEqual(0, result["sim_pot_days"])
                self.assertIn("缺失", result["route_reason"])

    def test_l1_weak_l3_strong_checks_selection_and_capacity(self) -> None:
        result = self.summarize(all_tick_nonzero_hit=0.4, all_tick_spearman=-0.1, all_tick_direction_capture=-0.1)
        self.assertEqual("inspect_gate_coverage_capacity", result["route"])
        self.assertEqual("weak", result["all_tick_prediction_status"])
        self.assertEqual("healthy", result["trade_prediction_status"])

    def test_l1_strong_l3_weak_checks_policy_even_with_positive_pot(self) -> None:
        result = self.summarize(trade_hit=0.4, trade_spearman=-0.1, direction_capture=-0.1)
        self.assertEqual("inspect_policy_cost_exit", result["route"])

    def test_l1_and_l3_weak_generate_model_candidate(self) -> None:
        result = self.summarize(
            trade_hit=0.4, trade_spearman=-0.1, direction_capture=-0.1,
            all_tick_nonzero_hit=0.4, all_tick_spearman=-0.1, all_tick_direction_capture=-0.1,
        )
        self.assertEqual("model_or_label_candidate", result["route"])

    def test_missing_or_thin_l3_cannot_be_overridden_by_strong_l1(self) -> None:
        for overrides in ({"signal_trade_n": 0}, {"signal_trade_n": 1}, {"trade_hit": np.nan, "trade_spearman": np.nan, "direction_capture": np.nan}):
            with self.subTest(overrides=overrides):
                self.assertEqual("insufficient", self.summarize(**overrides)["route"])

    def test_healthy_and_deployment_controls(self) -> None:
        self.assertEqual("monitor_no_model_change", self.summarize()["route"])
        self.assertEqual("deployment_gap_unresolved", self.summarize(real_dret=-0.1)["route"])
        self.assertEqual("inspect_policy_cost_exit", self.summarize(sim_pot=-0.1)["route"])

    def test_documented_prediction_example_executes(self) -> None:
        source = (SKILL_ROOT / "references" / "deep-attribution.md").read_text(encoding="utf-8")
        blocks = re.findall(r"```python\n(.*?)```", source, re.DOTALL)
        example = next(block for block in blocks if "direction_capture =" in block)
        namespace = {"pd": pd, "np": np, "signals": pd.DataFrame({
            "sym": ["eb", "eb"], "dorn": ["day", "day"],
            "dfactor": [-1.0, 2.0], "r_dfactor": [-2.0, 3.0],
        })}
        exec(example, namespace)
        self.assertEqual(1.0, namespace["direction_capture"].iloc[0])


if __name__ == "__main__":
    unittest.main()
