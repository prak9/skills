#!/usr/bin/env python3
"""Collect a bounded, ordered list of liked note URLs from an authorized session."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright

from browser_common import (
    CONFIG_ROOT,
    canonical_note_url,
    emit,
    has_login_session,
    launch_context,
    risk_reason,
)


def collect_visible(page: Any) -> list[dict[str, str]]:
    rows = page.locator('a[href*="/explore/"], a[href*="/discovery/item/"]').evaluate_all(
        """els => els.map(a => ({
          href: a.href || a.getAttribute('href') || '',
          text: (a.innerText || a.getAttribute('title') || a.parentElement?.innerText || '').trim()
        }))"""
    )
    notes: list[dict[str, str]] = []
    for row in rows:
        normalized = canonical_note_url(row.get("href", ""))
        if not normalized:
            continue
        note_id, url = normalized
        notes.append({"note_id": note_id, "url": url, "title_hint": row.get("text", "")[:200]})
    return notes


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile-url", required=True, help="The logged-in user's own profile URL")
    parser.add_argument("--max-notes", type=int, default=10)
    parser.add_argument("--max-scrolls", type=int, default=30)
    parser.add_argument("--delay-ms", type=int, default=1500)
    parser.add_argument("--out", default=str(CONFIG_ROOT / "pending-likes.json"))
    args = parser.parse_args()
    if not 1 <= args.max_notes <= 200:
        parser.error("--max-notes must be between 1 and 200")
    output = Path(args.out).expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.parent.chmod(0o700)

    with sync_playwright() as playwright:
        context = launch_context(playwright, headless=True)
        page = context.pages[0] if context.pages else context.new_page()
        try:
            page.goto(args.profile_url, wait_until="domcontentloaded", timeout=30_000)
            page.wait_for_timeout(2500)
            if reason := risk_reason(page):
                emit({"ok": False, "status": "security_block", "reason": reason})
                return 3
            if not has_login_session(context):
                emit({"ok": False, "status": "login_required"})
                return 3

            likes = page.get_by_text("赞过", exact=True)
            if not likes.count():
                page.screenshot(path=str(CONFIG_ROOT / "likes-tab-missing.png"), full_page=False)
                emit({"ok": False, "status": "likes_tab_missing", "screenshot": str(CONFIG_ROOT / "likes-tab-missing.png")})
                return 4
            likes.first.click()
            page.wait_for_timeout(2000)

            found: dict[str, dict[str, str]] = {}
            stale_rounds = 0
            for _ in range(args.max_scrolls):
                if reason := risk_reason(page):
                    emit({"ok": False, "status": "security_block", "reason": reason})
                    return 3
                if not has_login_session(context):
                    emit({"ok": False, "status": "login_required"})
                    return 3
                before = len(found)
                for note in collect_visible(page):
                    found.setdefault(note["note_id"], note)
                    if len(found) >= args.max_notes:
                        break
                if len(found) >= args.max_notes:
                    break
                stale_rounds = stale_rounds + 1 if len(found) == before else 0
                if stale_rounds >= 3:
                    break
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                page.wait_for_timeout(args.delay_ms)
                if reason := risk_reason(page):
                    emit({"ok": False, "status": "security_block", "reason": reason})
                    return 3
                if not has_login_session(context):
                    emit({"ok": False, "status": "login_required"})
                    return 3

            notes = list(found.values())[: args.max_notes]
            payload = {
                "schema_version": 1,
                "collected_at": datetime.now(timezone.utc).isoformat(),
                "profile_url": args.profile_url,
                "count": len(notes),
                "notes": notes,
            }
            temporary = output.with_suffix(output.suffix + ".tmp")
            temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            temporary.replace(output)
            page.screenshot(path=str(CONFIG_ROOT / "likes-collected.png"), full_page=False)
            emit({"ok": True, "status": "collected", "count": len(notes), "manifest": str(output)})
            return 0
        except PlaywrightTimeoutError as exc:
            emit({"ok": False, "status": "navigation_timeout", "error": str(exc)})
            return 3
        finally:
            context.close()


if __name__ == "__main__":
    raise SystemExit(main())
