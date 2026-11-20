#!/usr/bin/env python3
"""One-command bootstrapper for hft-evolution-loop: refresh ledger/slices and inspect or init tree."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence


def run_bootstrap(
    *,
    py_root: Path,
    artifacts_dirs: Sequence[Path],
    campaign_dir: Path,
    campaign_id: Optional[str] = None,
    root_account: str = "dce_t2",
    symbols: Sequence[str] = ("eb", "eg", "pp", "l", "y", "pg"),
    max_nodes: Optional[int] = None,
    max_depth: Optional[int] = None,
    lookback_days: int = 5,
    top_k: int = 8,
) -> Dict[str, Any]:
    py_root = Path(py_root).resolve()
    if str(py_root) not in sys.path:
        sys.path.insert(0, str(py_root))

    from analyze.daily_metrics_ledger import build_daily_metrics_ledger, extract_failure_slices
    from exp.evolution_tree import init_campaign, update_budget

    cdir = Path(campaign_dir).resolve()
    cid = campaign_id or cdir.name
    tree_path = cdir / "tree.json"

    if not tree_path.is_file():
        tree = init_campaign(
            cdir,
            campaign_id=cid,
            root_account=root_account,
            symbols=symbols,
            max_nodes=10 if max_nodes is None else max_nodes,
            max_depth=3 if max_depth is None else max_depth,
        )
        initialized_now = True
    else:
        if max_nodes is not None or max_depth is not None:
            tree = update_budget(cdir, max_nodes=max_nodes, max_depth=max_depth)
        else:
            tree = json.loads(tree_path.read_text(encoding="utf-8"))
        initialized_now = False

    ledger = build_daily_metrics_ledger(
        [Path(d) for d in artifacts_dirs],
        accounts=[tree["root_account"]],
        symbols=tree["symbols"],
    )
    metrics_dir = cdir / "metrics"
    metrics_dir.mkdir(parents=True, exist_ok=True)
    ledger_path = metrics_dir / "daily_metrics_ledger.csv"
    slices_path = metrics_dir / "failure_slices.jsonl"

    ledger.to_csv(ledger_path, index=False)
    slices = extract_failure_slices(ledger, lookback_days=lookback_days, top_k=top_k)
    slices_body = "\n".join(json.dumps(s, ensure_ascii=False) for s in slices)
    slices_path.write_text((slices_body + "\n") if slices_body else "", encoding="utf-8")

    neg_path = cdir / "negative_index.jsonl"
    negatives: List[Dict[str, Any]] = []
    if neg_path.is_file():
        for line in neg_path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                negatives.append(json.loads(line))

    actionable_slices = [
        s for s in slices if s["failure_type"] != "SIM_REAL_RESIDUAL"
    ]
    remaining_nodes = max(0, int(tree["max_nodes"]) - int(tree["used_nodes"]))

    return {
        "campaign_id": tree["campaign_id"],
        "campaign_dir": str(cdir),
        "initialized_now": initialized_now,
        "root_account": tree["root_account"],
        "symbols": tree["symbols"],
        "budget": {
            "used_nodes": int(tree["used_nodes"]),
            "max_nodes": int(tree["max_nodes"]),
            "remaining_nodes": remaining_nodes,
            "max_depth": int(tree["max_depth"]),
        },
        "champions": tree["champions"],
        "metrics": {
            "ledger_path": str(ledger_path),
            "slices_path": str(slices_path),
            "ledger_rows": int(len(ledger)),
            "unique_dates": int(ledger["date"].nunique()) if not ledger.empty else 0,
        },
        "top_failure_slices": slices,
        "actionable_slice_count": len(actionable_slices),
        "negative_index_count": len(negatives),
        "recent_negatives": negatives[-5:],
        "ready_for_next_node": remaining_nodes > 0 and len(actionable_slices) > 0,
    }


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Bootstrap or resume an hft-evolution-loop campaign and print readiness briefing."
    )
    p.add_argument("--py-root", default="/home/x/py", help="Path to py repository root")
    p.add_argument(
        "--artifacts-dir",
        action="append",
        required=True,
        help="Path to result.py artifacts directory (repeatable)",
    )
    p.add_argument("--campaign-dir", required=True, help="Evolution campaign directory")
    p.add_argument("--campaign-id", default=None, help="Optional campaign ID (defaults to dir name)")
    p.add_argument("--root-account", default="dce_t2", help="Baseline account (default: dce_t2)")
    p.add_argument("--symbols", default="eb,eg,pp,l,y,pg", help="Comma-separated symbol pool")
    p.add_argument("--max-nodes", type=int, default=None, help="Max nodes budget (default 10 on init; overrides existing tree if specified)")
    p.add_argument("--max-depth", type=int, default=None, help="Max tree depth (default 3 on init; overrides existing tree if specified)")
    p.add_argument("--lookback-days", type=int, default=5)
    p.add_argument("--top-k", type=int, default=8)
    return p


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    briefing = run_bootstrap(
        py_root=Path(args.py_root),
        artifacts_dirs=[Path(d) for d in args.artifacts_dir],
        campaign_dir=Path(args.campaign_dir),
        campaign_id=args.campaign_id,
        root_account=args.root_account,
        symbols=[s.strip() for s in args.symbols.split(",") if s.strip()],
        max_nodes=args.max_nodes,
        max_depth=args.max_depth,
        lookback_days=args.lookback_days,
        top_k=args.top_k,
    )
    print(json.dumps(briefing, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
