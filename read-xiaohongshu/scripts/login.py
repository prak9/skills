#!/usr/bin/env python3
"""Establish a user-authorized Xiaohongshu browser session without exposing secrets."""

from __future__ import annotations

import argparse
import time

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright

from browser_common import CONFIG_ROOT, emit, has_login_session, launch_context, risk_reason


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--headed", action="store_true", help="Open a visible browser window")
    parser.add_argument("--timeout", type=int, default=300, help="Seconds to wait for user login")
    args = parser.parse_args()
    screenshot = CONFIG_ROOT / "login.png"

    with sync_playwright() as playwright:
        context = launch_context(playwright, headless=not args.headed)
        page = context.pages[0] if context.pages else context.new_page()
        try:
            page.goto("https://www.xiaohongshu.com/explore", wait_until="domcontentloaded", timeout=30_000)
            page.wait_for_timeout(2500)
            if reason := risk_reason(page):
                page.screenshot(path=str(screenshot), full_page=False)
                emit({"ok": False, "status": "security_block", "reason": reason, "screenshot": str(screenshot)})
                return 3
            if has_login_session(context):
                emit({"ok": True, "status": "already_logged_in", "url": page.url})
                return 0

            login_input = page.locator('input[placeholder*="登录"]')
            if login_input.count():
                login_input.first.click()
                page.wait_for_timeout(4000)
            else:
                page.goto("https://www.xiaohongshu.com/login", wait_until="domcontentloaded", timeout=30_000)
                page.wait_for_timeout(2500)

            if reason := risk_reason(page):
                page.screenshot(path=str(screenshot), full_page=False)
                emit({"ok": False, "status": "security_block", "reason": reason, "screenshot": str(screenshot)})
                return 3

            page.screenshot(path=str(screenshot), full_page=False)
            emit({"ok": False, "status": "login_required", "screenshot": str(screenshot)})
            deadline = time.monotonic() + args.timeout
            while time.monotonic() < deadline:
                if has_login_session(context):
                    page.screenshot(path=str(CONFIG_ROOT / "logged-in.png"), full_page=False)
                    emit({"ok": True, "status": "logged_in", "url": page.url})
                    return 0
                if reason := risk_reason(page):
                    emit({"ok": False, "status": "security_block", "reason": reason})
                    return 3
                time.sleep(2)
            emit({"ok": False, "status": "timeout", "screenshot": str(screenshot)})
            return 4
        except PlaywrightTimeoutError as exc:
            emit({"ok": False, "status": "navigation_timeout", "error": str(exc)})
            return 3
        finally:
            context.close()


if __name__ == "__main__":
    raise SystemExit(main())
