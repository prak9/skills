#!/usr/bin/env python3
"""Wrap a validated WeChat fragment in a local page with a copy control."""

from __future__ import annotations

import argparse
import sys
from html import escape
from pathlib import Path

from validate_wechat import validate_html


TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{{TITLE}} · 微信公众号排版预览</title>
<style>
*{box-sizing:border-box}body{margin:0;background:#eef1f3;color:#20262c;font-family:-apple-system,BlinkMacSystemFont,"PingFang SC","Microsoft YaHei",sans-serif}.toolbar{position:sticky;top:0;z-index:10;display:flex;gap:16px;align-items:center;justify-content:space-between;padding:12px 18px;background:rgba(255,255,255,.96);border-bottom:1px solid #dfe4e8}.hint{margin:0;font-size:13px;line-height:1.5;color:#65717c}.copy{border:0;border-radius:8px;padding:10px 16px;background:#294d68;color:#fff;font:700 14px/1 inherit;cursor:pointer;white-space:nowrap}.copy:focus-visible{outline:3px solid #8fb6d1;outline-offset:2px}.stage{max-width:709px;margin:26px auto 56px;padding:0 16px}.status{min-height:22px;margin:8px auto 0;max-width:677px;padding:0 16px;color:#315342;font-size:13px}@media(max-width:520px){.toolbar{align-items:flex-start}.hint{max-width:210px}.stage{padding:0 8px}}
</style>
</head>
<body>
<header class="toolbar">
  <p class="hint">这里是本地预览。复制后仍需在微信公众号编辑器中检查一次。</p>
  <button class="copy" type="button" onclick="copyArticle()">复制正文</button>
</header>
<p class="status" id="copy-status" role="status" aria-live="polite"></p>
<main class="stage" id="copy-root">
{{CONTENT}}
</main>
<script>
function copyArticle(){
  var root=document.getElementById("copy-root");
  var status=document.getElementById("copy-status");
  var range=document.createRange();
  range.selectNodeContents(root);
  var selection=window.getSelection();
  selection.removeAllRanges();
  selection.addRange(range);
  var copied=false;
  try{copied=document.execCommand("copy");}catch(error){copied=false;}
  selection.removeAllRanges();
  status.textContent=copied?"已复制正文；请粘贴到公众号编辑器并打开手机预览。":"自动复制失败；请在正文区域手动全选并复制。";
}
</script>
</body>
</html>
"""


def build_preview(fragment: str, title: str) -> str:
    return TEMPLATE.replace("{{TITLE}}", escape(title)).replace("{{CONTENT}}", fragment.strip())


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="Validated HTML fragment")
    parser.add_argument("output", nargs="?", type=Path, help="Preview output path")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        fragment = args.input.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    errors, warnings = validate_html(fragment)
    if errors:
        print("ERROR: source fragment failed validation; preview was not written", file=sys.stderr)
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    output = args.output or args.input.with_name(f"{args.input.stem}-preview.html")
    try:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(build_preview(fragment, args.input.stem), encoding="utf-8")
    except OSError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print(f"Preview written: {output}")
    for warning in warnings:
        print(f"WARNING: {warning}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
