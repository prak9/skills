#!/usr/bin/env python3
"""Build cross-day, completed-trade model-tuning diagnostics from result bundles.

This is a routing aid, not a parameter selector.  It intentionally excludes weekly
files, does not infer opportunity coverage, and does not claim REAL/SIM pairing.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


DAILY_RE = re.compile(r"^trades_(\d{8})-(\d{8})\.csv$")
SIM_METRICS = (
    "pot", "costcov", "dret", "tn", "avgnwt", "prec", "ic", "alpha", "fg", "sg",
)
REAL_METRICS = ("pot", "costcov", "dret", "tn", "avgnwt", "hitr")


def _date(value: str) -> datetime:
    return datetime.strptime(value, "%Y%m%d")


def discover_bundles(root: Path, end: str | None, lookback: int) -> list[dict[str, Any]]:
    cutoff = _date(end) if end else None
    bundles: list[dict[str, Any]] = []
    for trades in root.glob("*/trades_*.csv"):
        match = DAILY_RE.match(trades.name)
        if not match:
            continue
        start_raw, end_raw = match.groups()
        start_dt, end_dt = _date(start_raw), _date(end_raw)
        if (end_dt - start_dt).days != 1 or (cutoff and end_dt > cutoff):
            continue
        winress = trades.with_name(f"winress_{start_raw}-{end_raw}.csv")
        if winress.exists():
            signals = trades.with_name(f"signals_{start_raw}-{end_raw}.csv")
            bundles.append({
                "date": start_raw,
                "end": end_raw,
                "trades": trades,
                "winress": winress,
                "signals": signals if signals.exists() else None,
            })
    bundles.sort(key=lambda item: item["date"])
    return bundles[-lookback:]


def _numeric(frame: pd.DataFrame, columns: tuple[str, ...] | list[str]) -> None:
    for column in columns:
        if column in frame:
            frame[column] = pd.to_numeric(frame[column], errors="coerce")


def _safe_ratio(numerator: float, denominator: float) -> float:
    if not np.isfinite(numerator) or not np.isfinite(denominator) or abs(denominator) < 1e-15:
        return np.nan
    return float(numerator / denominator)


def _corr(left: pd.Series, right: pd.Series, method: str) -> float:
    if len(left) < 2 or left.nunique() < 2 or right.nunique() < 2:
        return np.nan
    return float(left.corr(right, method=method))


def _trade_rows(frame: pd.DataFrame, account: str, date: str) -> pd.DataFrame:
    subset = frame[frame["account"].eq(account)].copy()
    rows: list[dict[str, Any]] = []
    for (sym, session), group in subset.groupby(["sym", "dorn"], dropna=False):
        pnl = group["pnl"].dropna()
        valid = group.dropna(subset=["enter_d", "enter_reald"]).copy()
        pred, realized = valid["enter_d"], valid["enter_reald"]
        hit_mask = pred.mul(realized).gt(0)
        pred_sq = float(pred.mul(pred).sum())
        abs_real = float(realized.abs().sum())
        pred_med = float(pred.abs().median()) if len(valid) else np.nan
        real_med = float(realized.abs().median()) if len(valid) else np.nan
        rows.append({
            "date": date,
            "sym": str(sym),
            "session": str(session),
            "sim_trade_n": int(len(group)),
            "signal_trade_n": int(len(valid)),
            "trade_hit": float(hit_mask.mean()) if len(valid) else np.nan,
            "trade_pearson": _corr(pred, realized, "pearson"),
            "trade_spearman": _corr(pred, realized, "spearman"),
            "direction_capture": _safe_ratio(
                float(realized.mul(np.sign(pred)).sum()), abs_real),
            "calibration_slope": _safe_ratio(float(pred.mul(realized).sum()), pred_sq),
            "abs_scale_ratio": _safe_ratio(pred_med, real_med),
            "sim_pnl": float(pnl.sum()) if len(pnl) else np.nan,
            "pnl_p10": float(pnl.quantile(0.1)) if len(pnl) else np.nan,
            "pnl_median": float(pnl.median()) if len(pnl) else np.nan,
            "pnl_p90": float(pnl.quantile(0.9)) if len(pnl) else np.nan,
            "pnl_hit": float(valid.loc[hit_mask, "pnl"].sum()) if len(valid) else np.nan,
            "pnl_miss": float(valid.loc[~hit_mask, "pnl"].sum()) if len(valid) else np.nan,
            "ppt_hit": float(valid.loc[hit_mask, "pnl"].mean()) if hit_mask.any() else np.nan,
            "ppt_miss": float(valid.loc[~hit_mask, "pnl"].mean()) if (~hit_mask).any() else np.nan,
        })
    return pd.DataFrame(rows)


def _real_trade_rows(frame: pd.DataFrame, account: str) -> pd.DataFrame:
    subset = frame[frame["account"].eq(account)].copy()
    rows: list[dict[str, Any]] = []
    for (sym, session), group in subset.groupby(["sym", "dorn"], dropna=False):
        pnl = group["pnl"].dropna()
        rows.append({
            "sym": str(sym),
            "session": str(session),
            "real_trade_n": int(len(group)),
            "real_pnl": float(pnl.sum()) if len(pnl) else np.nan,
            "real_ppt": float(pnl.mean()) if len(pnl) else np.nan,
        })
    return pd.DataFrame(rows)


def _winress_rows(frame: pd.DataFrame, account: str, metrics: tuple[str, ...], prefix: str) -> pd.DataFrame:
    subset = frame[frame["account"].eq(account)].copy()
    if subset.empty:
        return pd.DataFrame(columns=["sym", "session"])
    present = [column for column in metrics if column in subset]
    _numeric(subset, present)
    grouped = subset.groupby(["s", "t"], as_index=False)[present].median(numeric_only=True)
    if prefix == "sim_" and "y" in subset:
        labels = subset.groupby(["s", "t"], as_index=False)["y"].agg(
            lambda values: ",".join(sorted({str(value) for value in values.dropna()})))
        grouped = grouped.merge(labels, on=["s", "t"], how="left")
    grouped = grouped.rename(columns={"s": "sym", "t": "session"})
    rename = {column: f"{prefix}{column}" for column in present}
    if "y" in grouped:
        rename["y"] = "sim_y"
    return grouped.rename(columns=rename)


def _contract_value(value: Any) -> str:
    if value is None or (isinstance(value, float) and not np.isfinite(value)):
        return "NA"
    if isinstance(value, (float, np.floating)):
        return f"{float(value):.8g}"
    return str(value)


def load_bundle(bundle: dict[str, Any], account: str, real_account: str) -> pd.DataFrame:
    required = ["account", "sym", "dorn", "pnl", "enter_d", "enter_reald"]
    header = pd.read_csv(bundle["trades"], nrows=0).columns.tolist()
    missing = [column for column in required if column not in header]
    if missing:
        raise ValueError(f"{bundle['trades']}: missing columns {missing}")
    trades = pd.read_csv(bundle["trades"], usecols=required).reset_index(drop=True)
    _numeric(trades, ["pnl", "enter_d", "enter_reald"])
    trades["sym"] = trades["sym"].astype(str)
    trades["dorn"] = trades["dorn"].astype(str)

    winress = pd.read_csv(bundle["winress"]).reset_index(drop=True)
    sim = _trade_rows(trades, account, bundle["date"])
    real = _real_trade_rows(trades, real_account)
    sim_w = _winress_rows(winress, account, SIM_METRICS, "sim_")
    real_w = _winress_rows(winress, real_account, REAL_METRICS, "real_")
    for extra in (real, sim_w, real_w):
        if not extra.empty:
            sim = sim.merge(extra, on=["sym", "session"], how="left")
    sim["observable_contract"] = [
        "|".join((
            f"y={_contract_value(y)}",
            f"fg={_contract_value(fg)}",
            f"sg={_contract_value(sg)}",
        ))
        for y, fg, sg in zip(
            sim.get("sim_y", pd.Series([None] * len(sim))),
            sim.get("sim_fg", pd.Series([np.nan] * len(sim))),
            sim.get("sim_sg", pd.Series([np.nan] * len(sim))),
        )
    ]

    if "real_trade_n" in sim:
        sim["real_sim_trade_ratio"] = [
            _safe_ratio(real_n, sim_n)
            for real_n, sim_n in zip(sim["real_trade_n"], sim["sim_trade_n"])
        ]
    if "real_pnl" in sim:
        sim["pnl_capture_descriptive"] = [
            _safe_ratio(real_pnl, sim_pnl)
            for real_pnl, sim_pnl in zip(sim["real_pnl"], sim["sim_pnl"])
        ]
    if {"real_dret", "sim_dret"}.issubset(sim.columns):
        sim["real_minus_sim_dret"] = sim["real_dret"] - sim["sim_dret"]
        sim["dret_capture_descriptive"] = [
            _safe_ratio(real_dret, sim_dret)
            for real_dret, sim_dret in zip(sim["real_dret"], sim["sim_dret"])
        ]
    return sim


def _prediction_stats(group: pd.DataFrame, prefix: str) -> dict[str, Any]:
    valid = group.dropna(subset=["dfactor", "r_dfactor"]).copy()
    pred, realized = valid["dfactor"], valid["r_dfactor"]
    hit = pred.mul(realized).gt(0)
    nonzero = pred.ne(0) & realized.ne(0)
    pred_sq = float(pred.mul(pred).sum())
    abs_real = float(realized.abs().sum())
    pred_med = float(pred.abs().median()) if len(valid) else np.nan
    real_med = float(realized.abs().median()) if len(valid) else np.nan
    return {
        f"{prefix}_n": int(len(valid)),
        f"{prefix}_hit": float(hit.mean()) if len(valid) else np.nan,
        f"{prefix}_nonzero_hit": float(hit[nonzero].mean()) if nonzero.any() else np.nan,
        f"{prefix}_target_zero_rate": float(realized.eq(0).mean()) if len(valid) else np.nan,
        f"{prefix}_pearson": _corr(pred, realized, "pearson"),
        f"{prefix}_spearman": _corr(pred, realized, "spearman"),
        f"{prefix}_direction_capture": _safe_ratio(
            float(realized.mul(np.sign(pred)).sum()), abs_real),
        f"{prefix}_calibration_slope": _safe_ratio(
            float(pred.mul(realized).sum()), pred_sq),
        f"{prefix}_abs_scale_ratio": _safe_ratio(pred_med, real_med),
    }


def _margin_monotonicity(group: pd.DataFrame) -> tuple[float, float]:
    valid = group.dropna(subset=["dfactor", "r_dfactor", "feegate_r"]).copy()
    if len(valid) < 100:
        return np.nan, np.nan
    valid["margin"] = valid["dfactor"].abs() - valid["feegate_r"].abs()
    valid["aligned_real"] = np.sign(valid["dfactor"]) * valid["r_dfactor"]
    try:
        valid["bucket"] = pd.qcut(valid["margin"], 5, labels=False, duplicates="drop")
    except ValueError:
        return np.nan, np.nan
    curve = valid.groupby("bucket")["aligned_real"].mean().dropna()
    if len(curve) < 3:
        return np.nan, np.nan
    monotonicity = float(pd.Series(curve.index, dtype=float).corr(
        pd.Series(curve.values, dtype=float), method="spearman"))
    top_bottom = float(curve.iloc[-1] - curve.iloc[0])
    return monotonicity, top_bottom


def load_signal_bundle(bundle: dict[str, Any], account: str) -> pd.DataFrame:
    path = bundle.get("signals")
    if path is None:
        return pd.DataFrame()
    columns = ["account", "sym", "dorn", "dir", "dfactor", "r_dfactor", "feegate_r"]
    parts = []
    for chunk in pd.read_csv(path, usecols=columns, chunksize=500_000):
        chunk = chunk[chunk["account"].eq(account)].drop(columns=["account"])
        if len(chunk):
            parts.append(chunk)
    if not parts:
        return pd.DataFrame()
    frame = pd.concat(parts, ignore_index=True)
    _numeric(frame, ["dfactor", "r_dfactor", "feegate_r"])
    rows: list[dict[str, Any]] = []
    for (sym, session), group in frame.groupby(["sym", "dorn"], sort=True):
        eligible = group[group["dir"].isin(["buy", "sell"])]
        monotonicity, top_bottom = _margin_monotonicity(group)
        row = {
            "date": bundle["date"],
            "sym": str(sym),
            "session": str(session),
            **_prediction_stats(group, "all_tick"),
            **_prediction_stats(eligible, "eligible"),
            "eligibility_rate": _safe_ratio(float(len(eligible)), float(len(group))),
            "margin_monotonicity": monotonicity,
            "margin_top_bottom_realized": top_bottom,
        }
        rows.append(row)
    return pd.DataFrame(rows)


def _median(group: pd.DataFrame, column: str) -> float:
    if column not in group:
        return np.nan
    values = pd.to_numeric(group[column], errors="coerce").dropna()
    return float(values.median()) if len(values) else np.nan


def _positive_rate(group: pd.DataFrame, column: str) -> float:
    if column not in group:
        return np.nan
    values = pd.to_numeric(group[column], errors="coerce").dropna()
    return float(values.gt(0).mean()) if len(values) else np.nan


def _zero_rate(group: pd.DataFrame, column: str) -> float:
    if column not in group:
        return np.nan
    values = pd.to_numeric(group[column], errors="coerce").dropna()
    return float(values.abs().lt(1e-12).mean()) if len(values) else np.nan


def _loo_min_median(group: pd.DataFrame, column: str) -> float:
    if column not in group:
        return np.nan
    values = pd.to_numeric(group[column], errors="coerce").dropna().reset_index(drop=True)
    if len(values) < 3:
        return np.nan
    return float(min(values.drop(index).median() for index in values.index))


def _route(summary: dict[str, Any], min_days: int, min_trades: int) -> tuple[str, str]:
    basis = summary["prediction_basis"]
    if summary["prediction_days"] < min_days or summary["prediction_n"] < min_trades:
        return "insufficient", f"同合同日期或 {basis} 预测样本不足"
    weak = summary["route_prediction_weak_day_rate"]
    strong = summary["route_prediction_strong_day_rate"]
    pot = summary["sim_pot_median"]
    pot_pos = summary["sim_pot_positive_day_rate"]
    sim_good = np.isfinite(pot) and pot > 0 and np.isfinite(pot_pos) and pot_pos >= 0.6
    if np.isfinite(weak) and weak >= 0.6:
        if basis == "all_tick":
            return "model_or_label_candidate", "全 tick 预测跨日偏弱"
        return "verify_model_or_label_on_all_tick", "完成交易子集预测跨日偏弱，先用全 tick 验证是否同源"
    if np.isfinite(strong) and strong >= 0.6 and not sim_good:
        return "inspect_policy_cost_exit", f"{basis} 预测健康但 SIM 成本后经济性弱"
    real_days = summary["real_days"]
    real_dret = summary["real_dret_median"]
    real_pos = summary["real_dret_positive_day_rate"]
    real_weak = real_days >= min_days and (
        (np.isfinite(real_dret) and real_dret <= 0)
        or (np.isfinite(real_pos) and real_pos < 0.5)
    )
    if np.isfinite(strong) and strong >= 0.6 and sim_good and real_weak:
        return "deployment_gap_unresolved", f"{basis} 预测与 SIM 经济性健康但 REAL 弱；需要逐决策 telemetry"
    if np.isfinite(strong) and strong >= 0.6 and sim_good:
        return "monitor_no_model_change", f"{basis} 预测与 SIM 成本后经济性均健康，没有日报证据支持改模型"
    return "mixed_more_data", "预测与经济证据冲突或稳定性不足"


def summarize_cells(daily: pd.DataFrame, min_days: int, min_trades: int) -> list[dict[str, Any]]:
    summaries: list[dict[str, Any]] = []
    if "observable_contract" not in daily:
        daily = daily.copy()
        daily["observable_contract"] = "unknown"
    for (sym, session, contract), group in daily.groupby(
            ["sym", "session", "observable_contract"], sort=True):
        pnl_abs = pd.to_numeric(group["sim_pnl"], errors="coerce").abs().dropna()
        concentration = _safe_ratio(float(pnl_abs.max()), float(pnl_abs.sum())) if len(pnl_abs) else np.nan
        signal_valid = group[pd.to_numeric(group["signal_trade_n"], errors="coerce").gt(0)].copy()
        weak_mask = (
            pd.to_numeric(signal_valid["trade_hit"], errors="coerce").lt(0.55)
            | pd.to_numeric(signal_valid["trade_spearman"], errors="coerce").le(0)
            | pd.to_numeric(signal_valid["direction_capture"], errors="coerce").le(0)
        )
        strong_mask = (
            pd.to_numeric(signal_valid["trade_hit"], errors="coerce").ge(0.65)
            & pd.to_numeric(signal_valid["trade_spearman"], errors="coerce").gt(0)
            & pd.to_numeric(signal_valid["direction_capture"], errors="coerce").gt(0)
        )
        all_tick_valid = group[pd.to_numeric(
            group.get("all_tick_n", pd.Series(index=group.index, dtype=float)),
            errors="coerce").gt(0)].copy()
        all_tick_weak = (
            pd.to_numeric(all_tick_valid.get("all_tick_nonzero_hit"), errors="coerce").le(0.5)
            | pd.to_numeric(all_tick_valid.get("all_tick_spearman"), errors="coerce").le(0)
            | pd.to_numeric(all_tick_valid.get("all_tick_direction_capture"), errors="coerce").le(0)
        ) if len(all_tick_valid) else pd.Series(dtype=bool)
        all_tick_strong = (
            pd.to_numeric(all_tick_valid.get("all_tick_nonzero_hit"), errors="coerce").gt(0.5)
            & pd.to_numeric(all_tick_valid.get("all_tick_spearman"), errors="coerce").gt(0)
            & pd.to_numeric(all_tick_valid.get("all_tick_direction_capture"), errors="coerce").gt(0)
        ) if len(all_tick_valid) else pd.Series(dtype=bool)
        use_all_tick = len(all_tick_valid) >= min_days
        prediction_basis = "all_tick" if use_all_tick else "completed_trade"
        prediction_n = int(pd.to_numeric(
            all_tick_valid["all_tick_n"] if use_all_tick else signal_valid["signal_trade_n"],
            errors="coerce").fillna(0).sum())
        route_weak = all_tick_weak if use_all_tick else weak_mask
        route_strong = all_tick_strong if use_all_tick else strong_mask
        real_days = int(pd.to_numeric(group.get("real_dret"), errors="coerce").notna().sum()) \
            if "real_dret" in group else 0
        summary = {
            "sym": str(sym),
            "session": str(session),
            "observable_contract": str(contract),
            "n_days": int(group["date"].nunique()),
            "dates": sorted(group["date"].astype(str).unique().tolist()),
            "sim_trade_n": int(pd.to_numeric(group["sim_trade_n"], errors="coerce").fillna(0).sum()),
            "signal_trade_n": int(pd.to_numeric(group["signal_trade_n"], errors="coerce").fillna(0).sum()),
            "real_days": real_days,
            "real_trade_n": int(pd.to_numeric(group.get("real_trade_n"), errors="coerce").fillna(0).sum())
                if "real_trade_n" in group else 0,
            "prediction_basis": prediction_basis,
            "prediction_days": int(len(all_tick_valid) if use_all_tick else len(signal_valid)),
            "prediction_n": prediction_n,
            "evidence_tier": "explore_candidate" if group["date"].nunique() >= 5
                else "early_candidate" if group["date"].nunique() >= 3 else "observation",
            "trade_hit_median": _median(group, "trade_hit"),
            "trade_pearson_median": _median(group, "trade_pearson"),
            "trade_spearman_median": _median(group, "trade_spearman"),
            "direction_capture_median": _median(group, "direction_capture"),
            "calibration_slope_median": _median(group, "calibration_slope"),
            "abs_scale_ratio_median": _median(group, "abs_scale_ratio"),
            "sim_pot_median": _median(group, "sim_pot"),
            "sim_pot_positive_day_rate": _positive_rate(group, "sim_pot"),
            "sim_pot_loo_min_median": _loo_min_median(group, "sim_pot"),
            "sim_dret_median": _median(group, "sim_dret"),
            "sim_avgnwt_median": _median(group, "sim_avgnwt"),
            "sim_prec_median": _median(group, "sim_prec"),
            "sim_ic_median": _median(group, "sim_ic"),
            "sim_alpha_median": _median(group, "sim_alpha"),
            "sim_alpha_zero_day_rate": _zero_rate(group, "sim_alpha"),
            "sim_fg_median": _median(group, "sim_fg"),
            "sim_sg_median": _median(group, "sim_sg"),
            "all_tick_n": int(pd.to_numeric(group.get("all_tick_n"), errors="coerce").fillna(0).sum())
                if "all_tick_n" in group else 0,
            "all_tick_hit_median": _median(group, "all_tick_hit"),
            "all_tick_nonzero_hit_median": _median(group, "all_tick_nonzero_hit"),
            "all_tick_target_zero_rate_median": _median(group, "all_tick_target_zero_rate"),
            "all_tick_spearman_median": _median(group, "all_tick_spearman"),
            "all_tick_direction_capture_median": _median(group, "all_tick_direction_capture"),
            "all_tick_calibration_slope_median": _median(group, "all_tick_calibration_slope"),
            "all_tick_abs_scale_ratio_median": _median(group, "all_tick_abs_scale_ratio"),
            "eligible_n": int(pd.to_numeric(group.get("eligible_n"), errors="coerce").fillna(0).sum())
                if "eligible_n" in group else 0,
            "eligible_hit_median": _median(group, "eligible_hit"),
            "eligible_nonzero_hit_median": _median(group, "eligible_nonzero_hit"),
            "eligible_target_zero_rate_median": _median(group, "eligible_target_zero_rate"),
            "eligible_spearman_median": _median(group, "eligible_spearman"),
            "eligible_direction_capture_median": _median(group, "eligible_direction_capture"),
            "eligibility_rate_median": _median(group, "eligibility_rate"),
            "margin_monotonicity_median": _median(group, "margin_monotonicity"),
            "margin_top_bottom_realized_median": _median(group, "margin_top_bottom_realized"),
            "real_dret_median": _median(group, "real_dret"),
            "real_dret_positive_day_rate": _positive_rate(group, "real_dret"),
            "real_sim_trade_ratio_median": _median(group, "real_sim_trade_ratio"),
            "pnl_abs_max_day_concentration": concentration,
            "prediction_weak_day_rate": float(weak_mask.mean()) if len(signal_valid) else np.nan,
            "prediction_strong_day_rate": float(strong_mask.mean()) if len(signal_valid) else np.nan,
            "all_tick_prediction_weak_day_rate": float(all_tick_weak.mean()) if len(all_tick_valid) else np.nan,
            "all_tick_prediction_strong_day_rate": float(all_tick_strong.mean()) if len(all_tick_valid) else np.nan,
            "route_prediction_weak_day_rate": float(route_weak.mean()) if len(route_weak) else np.nan,
            "route_prediction_strong_day_rate": float(route_strong.mean()) if len(route_strong) else np.nan,
        }
        if "sim_pot" in group and pd.to_numeric(group["sim_pot"], errors="coerce").notna().any():
            worst_index = pd.to_numeric(group["sim_pot"], errors="coerce").idxmin()
            summary["worst_sim_pot_date"] = str(group.loc[worst_index, "date"])
        else:
            summary["worst_sim_pot_date"] = None
        summary["route"], summary["route_reason"] = _route(summary, min_days, min_trades)
        summaries.append(summary)
    return summaries


def _clean(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _clean(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_clean(item) for item in value]
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating, float)):
        return None if not math.isfinite(float(value)) else float(value)
    return value


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def attach_model_artifacts(cells: list[dict[str, Any]], model_root: Path) -> Counter:
    statuses: Counter = Counter()
    for cell in cells:
        base = model_root / cell["session"] / cell["sym"] / "XZ_ID.csv"
        params = Path(str(base) + ".params")
        if not params.exists():
            cell["artifact"] = {"status": "missing", "params": str(params)}
            cell["actionability"] = "artifact_missing"
            statuses["missing"] += 1
            continue
        first = params.read_text(encoding="utf-8", errors="replace").splitlines()[0]
        parts = first.split("|")
        try:
            horizon = int(parts[1])
            alpha = float(parts[2])
            target = parts[3]
            artifact_y = f"y.{target}_{horizon}"
        except (IndexError, ValueError):
            horizon, alpha, target, artifact_y = None, None, None, None
        report_y = cell["observable_contract"].split("|", 1)[0].removeprefix("y=")
        match = artifact_y == report_y
        cfg = Path(str(base) + ".cfg")
        cell["artifact"] = {
            "status": "match" if match else "contract_mismatch",
            "model_path": str(base),
            "model_sha256": _sha256(base) if base.exists() else None,
            "params_path": str(params),
            "params_sha256": _sha256(params),
            "mtime": datetime.fromtimestamp(params.stat().st_mtime).isoformat(),
            "target": target,
            "horizon": horizon,
            "alpha": alpha,
            "choose_type": parts[4] if len(parts) > 4 else None,
            "model_type": parts[8] if len(parts) > 8 else None,
            "train_size": parts[11] if len(parts) > 11 else None,
            "alpha_lo": parts[12] if len(parts) > 12 else None,
            "alpha_hi": parts[13] if len(parts) > 13 else None,
            "cfg": cfg.read_text(encoding="utf-8", errors="replace").strip() if cfg.exists() else None,
            "report_y": report_y,
            "artifact_y": artifact_y,
        }
        cell["actionability"] = "current_contract" if match else "historical_report_contract_only"
        statuses[cell["artifact"]["status"]] += 1
    return statuses


def build_report(args: argparse.Namespace) -> dict[str, Any]:
    bundles = discover_bundles(Path(args.results_root), args.end, args.lookback)
    if not bundles:
        raise SystemExit("no complete daily trades+winress bundles found")
    daily = pd.concat(
        [load_bundle(bundle, args.account, args.real_account) for bundle in bundles],
        ignore_index=True,
    )
    histories = []
    for (sym, session, contract), group in daily.groupby(
            ["sym", "session", "observable_contract"], sort=True):
        histories.append({
            "sym": str(sym),
            "session": str(session),
            "observable_contract": str(contract),
            "first_date": str(group["date"].min()),
            "last_date": str(group["date"].max()),
            "n_days": int(group["date"].nunique()),
        })
    selected = daily
    if not args.all_contracts:
        latest = (daily.sort_values("date")
                  .drop_duplicates(["sym", "session"], keep="last")
                  [["sym", "session", "observable_contract"]]
                  .rename(columns={"observable_contract": "latest_contract"}))
        selected = daily.merge(latest, on=["sym", "session"], how="left")
        selected = selected[selected["observable_contract"].eq(selected["latest_contract"])].drop(
            columns=["latest_contract"])
    signal_dates: list[str] = []
    if args.include_signals:
        selected_dates = set(selected["date"].astype(str))
        signal_frames = []
        for bundle in bundles:
            if bundle["date"] in selected_dates and bundle.get("signals") is not None:
                signal_frame = load_signal_bundle(bundle, args.account)
                if len(signal_frame):
                    signal_frames.append(signal_frame)
                    signal_dates.append(bundle["date"])
        if signal_frames:
            signal_daily = pd.concat(signal_frames, ignore_index=True)
            selected = selected.merge(
                signal_daily, on=["date", "sym", "session"], how="left")
    cells = summarize_cells(selected, args.min_days, args.min_trades)
    artifact_statuses: Counter = Counter()
    if args.model_root:
        artifact_statuses = attach_model_artifacts(cells, Path(args.model_root))
    routes = Counter(cell["route"] for cell in cells)
    return _clean({
        "meta": {
            "account": args.account,
            "real_account": args.real_account,
            "bundle_count": len(bundles),
            "dates": [bundle["date"] for bundle in bundles],
            "identity_status": (
                "grouped by report y/fg/sg; current artifact hashes attached, report-time hashes unavailable"
                if args.model_root else
                "grouped by report y/fg/sg; model artifact hashes not checked"
            ),
            "contract_scope": "all" if args.all_contracts else "latest observable contract per cell",
            "daily_rows_total": int(len(daily)),
            "daily_rows_selected": int(len(selected)),
            "signals_requested": bool(args.include_signals),
            "signal_dates_loaded": signal_dates,
            "model_root": args.model_root,
            "artifact_status_counts": dict(sorted(artifact_statuses.items())),
            "route_counts": dict(sorted(routes.items())),
            "caveats": [
                "routes use all-tick signals when loaded for >=min_days; otherwise completed SIM trades",
                "0.55/0.65 hit and 0.60 positive-day cutoffs are routing heuristics, not promotion thresholds",
                "real_sim_trade_ratio is a non-paired completed-trade count ratio, not coverage",
                "REAL/SIM capture values are descriptive and do not identify execution causes",
                "rows are split by observable y/fg/sg; verify model artifact/config hashes before decisions",
                "model-root artifacts are current files and may post-date historical report bundles",
                "routes generate hypotheses only; fixed held-out evaluator decides parameters",
            ],
        },
        "inputs": [
            {key: str(value) if isinstance(value, Path) else value for key, value in bundle.items()}
            for bundle in bundles
        ],
        "contract_history": histories,
        "cells": cells,
        "daily": selected.to_dict(orient="records"),
    })


def self_test() -> None:
    rows: list[dict[str, Any]] = []
    for day in ("20260701", "20260702", "20260703"):
        rows.extend([
            {
                "date": day, "sym": "eb", "session": "day", "sim_trade_n": 50,
                "signal_trade_n": 50, "trade_hit": 0.8, "trade_pearson": 0.3,
                "trade_spearman": 0.3, "direction_capture": 0.4,
                "calibration_slope": 1.0, "abs_scale_ratio": 1.0, "sim_pnl": 100,
                "all_tick_n": 1000, "all_tick_hit": 0.58, "all_tick_nonzero_hit": 0.6,
                "all_tick_spearman": 0.3, "all_tick_direction_capture": 0.4,
                "sim_pot": 0.3, "sim_dret": 0.01, "sim_avgnwt": 0.4,
                "sim_prec": 0.8, "sim_ic": 0.3, "real_trade_n": 20,
                "real_dret": -0.01, "real_sim_trade_ratio": 0.4,
            },
            {
                "date": day, "sym": "pg", "session": "night", "sim_trade_n": 50,
                "signal_trade_n": 50, "trade_hit": 0.45, "trade_pearson": -0.1,
                "trade_spearman": -0.1, "direction_capture": -0.2,
                "calibration_slope": -0.2, "abs_scale_ratio": 1.5, "sim_pnl": -80,
                "all_tick_n": 1000, "all_tick_hit": 0.45, "all_tick_nonzero_hit": 0.45,
                "all_tick_spearman": -0.1, "all_tick_direction_capture": -0.2,
                "sim_pot": -0.2, "sim_dret": -0.01, "sim_avgnwt": -0.3,
                "sim_prec": 0.45, "sim_ic": -0.1, "real_trade_n": 0,
                "real_dret": np.nan, "real_sim_trade_ratio": 0,
            },
            {
                "date": day, "sym": "c", "session": "day", "sim_trade_n": 50,
                "signal_trade_n": 50, "trade_hit": 0.9, "trade_pearson": 0.3,
                "trade_spearman": 0.3, "direction_capture": 0.5,
                "calibration_slope": 1.0, "abs_scale_ratio": 1.0, "sim_pnl": -50,
                "all_tick_n": 1000, "all_tick_hit": 0.05, "all_tick_nonzero_hit": 0.9,
                "all_tick_spearman": 0.3, "all_tick_direction_capture": 0.5,
                "sim_pot": -0.3, "sim_dret": -0.01, "sim_avgnwt": -0.2,
                "sim_prec": 0.9, "sim_ic": 0.3, "real_trade_n": 0,
                "real_dret": np.nan, "real_sim_trade_ratio": 0,
            },
        ])
    cells = {(row["sym"], row["session"]): row for row in summarize_cells(pd.DataFrame(rows), 3, 100)}
    assert cells[("eb", "day")]["route"] == "deployment_gap_unresolved"
    assert cells[("pg", "night")]["route"] == "model_or_label_candidate"
    assert cells[("c", "day")]["route"] == "inspect_policy_cost_exit"
    assert cells[("eb", "day")]["real_sim_trade_ratio_median"] == 0.4
    print("self-test: PASS")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results-root", default="/home/x/www/results")
    parser.add_argument("--account", default="dce_t1")
    parser.add_argument("--real-account", default="dce_ht1028")
    parser.add_argument("--end", help="exclusive report end date, YYYYMMDD")
    parser.add_argument("--lookback", type=int, default=20)
    parser.add_argument("--min-days", type=int, default=3)
    parser.add_argument("--min-trades", type=int, default=100)
    parser.add_argument("--all-contracts", action="store_true")
    parser.add_argument("--include-signals", action="store_true")
    parser.add_argument("--model-root", help="current model root, e.g. latest_models_t1")
    parser.add_argument("--output")
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.self_test:
        self_test()
        return
    report = build_report(args)
    payload = json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False)
    if args.output:
        output = Path(args.output)
        output.write_text(payload + "\n", encoding="utf-8")
        print(json.dumps({"output": str(output), **report["meta"]}, ensure_ascii=False, indent=2))
    else:
        print(payload)


if __name__ == "__main__":
    main()
