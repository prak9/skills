#!/usr/bin/env python3
"""Shared local-session helpers for the optional Xiaohongshu browser extension."""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any
from urllib.parse import urljoin, urlsplit, urlunsplit


CONFIG_ROOT = Path(
    os.environ.get("XHS_READER_CONFIG", Path.home() / ".config" / "read-xiaohongshu")
).expanduser()
VENV_DIR = CONFIG_ROOT / "venv"
PROFILE_DIR = CONFIG_ROOT / "browser-profile"
NOTE_ID_RE = re.compile(r"/(?:explore|discovery/item)/([0-9a-f]{16,32})(?:/|$)", re.I)
RISK_MARKERS = (
    "IP存在风险",
    "安全限制",
    "error_code=300012",
    "/website-login/error",
    "/website-login/captcha",
)


def ensure_private_dirs() -> None:
    for path in (CONFIG_ROOT, PROFILE_DIR):
        path.mkdir(parents=True, exist_ok=True)
        path.chmod(0o700)


def emit(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, ensure_ascii=False), flush=True)


def find_chromium_executable(playwright: Any) -> str:
    configured = os.environ.get("PLAYWRIGHT_BROWSERS_PATH")
    roots = [Path(configured)] if configured else []
    roots.extend(
        [
            Path.home() / ".cache" / "ms-playwright",
            Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache")) / "ms-playwright",
        ]
    )
    candidates: list[Path] = []
    for root in roots:
        candidates.extend(root.glob("chromium-*/chrome-linux64/chrome"))
        candidates.extend(root.glob("chromium-*/chrome-linux/chrome"))
        candidates.extend(root.glob("chromium-*/chrome-mac/Chromium.app/Contents/MacOS/Chromium"))
    default = Path(playwright.chromium.executable_path)
    if default.is_file() and "headless_shell" not in str(default):
        candidates.append(default)
    existing = sorted({path.resolve() for path in candidates if path.is_file()}, reverse=True)
    if not existing:
        raise RuntimeError("Chromium is not installed; run setup_browser.py --install")
    return str(existing[0])


def launch_context(playwright: Any, *, headless: bool) -> Any:
    ensure_private_dirs()
    return playwright.chromium.launch_persistent_context(
        str(PROFILE_DIR),
        headless=headless,
        executable_path=find_chromium_executable(playwright),
        viewport={"width": 1440, "height": 1000},
        locale="zh-CN",
        timezone_id="Asia/Shanghai",
    )


def risk_reason(page: Any) -> str | None:
    combined = f"{page.url}\n{page.locator('body').inner_text()[:3000]}"
    return next((marker for marker in RISK_MARKERS if marker in combined), None)


def has_login_session(context: Any) -> bool:
    return any(cookie.get("name") == "web_session" and cookie.get("value") for cookie in context.cookies())


def canonical_note_url(value: str) -> tuple[str, str] | None:
    absolute = urljoin("https://www.xiaohongshu.com", value)
    parsed = urlsplit(absolute)
    host = (parsed.hostname or "").lower().rstrip(".")
    if parsed.scheme not in {"http", "https"} or not (host == "xiaohongshu.com" or host.endswith(".xiaohongshu.com")):
        return None
    match = NOTE_ID_RE.search(parsed.path)
    if not match:
        return None
    note_id = match.group(1).lower()
    canonical = urlunsplit(("https", "www.xiaohongshu.com", f"/explore/{note_id}", parsed.query, ""))
    return note_id, canonical
