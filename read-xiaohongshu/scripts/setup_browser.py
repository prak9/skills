#!/usr/bin/env python3
"""Check or install an isolated Playwright runtime for authorized account access."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import venv
from pathlib import Path

from browser_common import CONFIG_ROOT, VENV_DIR


def venv_python() -> Path:
    return VENV_DIR / ("Scripts/python.exe" if os.name == "nt" else "bin/python")


def browser_roots() -> list[Path]:
    configured = os.environ.get("PLAYWRIGHT_BROWSERS_PATH")
    roots = [Path(configured)] if configured else []
    roots.append(Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache")) / "ms-playwright")
    roots.append(Path.home() / ".cache" / "ms-playwright")
    return roots


def browser_installed() -> bool:
    return any(
        list(root.glob("chromium-*/chrome-linux*/chrome"))
        or list(root.glob("chromium-*/chrome-mac/Chromium.app/Contents/MacOS/Chromium"))
        for root in browser_roots()
    )


def status() -> dict[str, object]:
    python = venv_python()
    playwright = False
    version = None
    if python.is_file():
        result = subprocess.run(
            [str(python), "-c", "import importlib.metadata; print(importlib.metadata.version('playwright'))"],
            capture_output=True,
            text=True,
            check=False,
        )
        playwright = result.returncode == 0
        version = result.stdout.strip() or None
    return {
        "ready": playwright and browser_installed(),
        "config_root": str(CONFIG_ROOT),
        "venv_python": str(python),
        "playwright": playwright,
        "playwright_version": version,
        "chromium": browser_installed(),
    }


def install() -> None:
    CONFIG_ROOT.mkdir(parents=True, exist_ok=True)
    CONFIG_ROOT.chmod(0o700)
    if not venv_python().is_file():
        venv.EnvBuilder(with_pip=True).create(VENV_DIR)
    python = venv_python()
    subprocess.run(
        [str(python), "-m", "pip", "install", "--upgrade", "playwright>=1.50,<2"], check=True
    )
    subprocess.run([str(python), "-m", "playwright", "install", "chromium"], check=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--check", action="store_true")
    group.add_argument("--install", action="store_true")
    args = parser.parse_args()
    if args.install:
        install()
    result = status()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ready"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
