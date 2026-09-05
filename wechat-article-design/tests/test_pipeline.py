from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from html.parser import HTMLParser
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = SKILL_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from render_wechat import load_theme, render_document  # noqa: E402
from validate_wechat import validate_html  # noqa: E402
from wrap_preview import build_preview  # noqa: E402


SAMPLE = """---
title: 一次可靠的发布
author: 林舟
---

开头保留原文，并突出 **可靠性** 与 ==验证闭环==。

边界表达式 A < B & C 也必须原样保留。

## 先明确目标

> 生成得快，不等于交付得稳。

### 最小流程

1. 读取原文
2. 生成片段
3. 校验结果

```python
def publish(article):
    return article.validate()
```

![流程示意](https://example.com/flow.png)
"""


class PipelineTests(unittest.TestCase):
    def test_fenced_comments_never_become_the_article_title(self) -> None:
        class Paragraphs(HTMLParser):
            def __init__(self) -> None:
                super().__init__()
                self.paragraphs = []
                self.current = None

            def handle_starttag(self, tag, attrs) -> None:
                if tag == "p":
                    self.current = ""

            def handle_data(self, data) -> None:
                if self.current is not None:
                    self.current += data

            def handle_endtag(self, tag) -> None:
                if tag == "p" and self.current is not None:
                    self.paragraphs.append(self.current.replace("\u00a0", " ").replace("\u200b", ""))
                    self.current = None

        theme, _ = load_theme("ink")
        code = "# Actual code comment\n\tvalue  = '<literal> & **bold**'\n\n  # nested comment"
        for fence in ("```", "````", "~~~"):
            for metadata, heading, expected in (
                ("---\ntitle: Correct Title\n---\n", "", "Correct Title"),
                ("", "\n# Real H1\n", "Real H1"),
                ("---\ntitle: Metadata\n---\n", "\n# Real H1\n", "Real H1"),
                ("", "", "Fallback"),
            ):
                with self.subTest(fence=fence, expected=expected, metadata=metadata):
                    fragment = render_document(
                        metadata + fence + "sh\n" + code + "\n" + fence + heading,
                        theme,
                        "Fallback",
                    )
                    parser = Paragraphs()
                    parser.feed(fragment)
                    self.assertEqual([expected, "SH", *code.expandtabs(4).split("\n")], parser.paragraphs)
                    self.assertEqual(([], []), validate_html(fragment))

    def test_only_matching_fence_can_close_code(self) -> None:
        theme, _ = load_theme("ink")
        fragment = render_document(
            "````sh\n```\n~~~\n````python\n# literal\n`````\n# Article", theme
        )
        for literal in ("```", "~~~", "````python", "# literal"):
            self.assertIn(f'<span leaf="">{literal}</span>', fragment)
        self.assertIn('<span leaf="">Article</span>', fragment)

    def test_unclosed_fence_is_rejected_even_when_it_contains_h1(self) -> None:
        theme, _ = load_theme("ink")
        for fence in ("```", "````", "~~~"):
            with self.subTest(fence=fence), self.assertRaisesRegex(ValueError, "代码块缺少结束"):
                render_document(fence + "sh\n# still code", theme)

    def test_renderer_output_passes_validator_and_preserves_content(self) -> None:
        theme, _ = load_theme("moss")
        fragment = render_document(SAMPLE, theme)

        errors, warnings = validate_html(fragment)

        self.assertEqual([], errors)
        self.assertEqual([], warnings)
        self.assertIn("一次可靠的发布", fragment)
        self.assertIn("林舟", fragment)
        self.assertIn("生成得快，不等于交付得稳。", fragment)
        self.assertIn("A &lt; B &amp; C", fragment)
        self.assertIn("读取原文", fragment)
        self.assertIn("def publish(article):", fragment)
        self.assertIn("https://example.com/flow.png", fragment)
        self.assertIn('<span leaf="">', fragment)
        self.assertNotIn("<div", fragment)
        self.assertNotIn("<style", fragment)
        self.assertNotIn(" class=", fragment)

    def test_validator_rejects_unsafe_and_unwrapped_markup(self) -> None:
        fragment = (
            '<section style="position:absolute">'
            '<p class="lead">未包裹<script>alert(1)</script></p>'
            "</section>"
        )

        errors, _ = validate_html(fragment)
        joined = "\n".join(errors)

        self.assertIn("定位", joined)
        self.assertIn("class", joined)
        self.assertIn("<script>", joined)
        self.assertIn("未放在", joined)

    def test_renderer_rejects_unsafe_links(self) -> None:
        theme, _ = load_theme("ink")
        with self.assertRaisesRegex(ValueError, "URL"):
            render_document("# 标题\n\n[点这里](javascript:alert(1))", theme)

    def test_relative_images_are_visible_as_delivery_warnings(self) -> None:
        theme, _ = load_theme("ink")
        fragment = render_document("# 标题\n\n![](images/local.png)", theme)

        errors, warnings = validate_html(fragment)

        self.assertEqual([], errors)
        self.assertTrue(any("相对路径" in warning for warning in warnings))

    def test_custom_theme_inherits_defaults_and_enforces_contrast(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            valid_path = Path(directory) / "brand.json"
            valid_path.write_text(
                json.dumps(
                    {
                        "name": "深海",
                        "accent": "#416B7A",
                        "accent_dark": "#244653",
                        "accent_soft": "#EAF1F3",
                    }
                ),
                encoding="utf-8",
            )
            theme, slug = load_theme(theme_file=valid_path)
            self.assertEqual("brand", slug)
            self.assertEqual("#FFFFFF", theme["canvas"])

            invalid_path = Path(directory) / "faint.json"
            invalid_path.write_text(
                json.dumps({"name": "太淡", "text": "#EEEEEE", "canvas": "#FFFFFF"}),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "4.5:1"):
                load_theme(theme_file=invalid_path)

    def test_cli_pipeline_writes_valid_fragment_and_copy_preview(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "article.md"
            fragment = root / "article.html"
            preview = root / "preview.html"
            source.write_text(SAMPLE, encoding="utf-8")

            render = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPTS / "render_wechat.py"),
                    str(source),
                    "--theme",
                    "ink",
                    "-o",
                    str(fragment),
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(0, render.returncode, render.stderr)

            validate = subprocess.run(
                [sys.executable, str(SCRIPTS / "validate_wechat.py"), str(fragment)],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(0, validate.returncode, validate.stdout + validate.stderr)
            self.assertIn("PASS", validate.stdout)

            wrap = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPTS / "wrap_preview.py"),
                    str(fragment),
                    str(preview),
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(0, wrap.returncode, wrap.stdout + wrap.stderr)
            preview_text = preview.read_text(encoding="utf-8")
            self.assertIn('id="copy-root"', preview_text)
            self.assertIn(fragment.read_text(encoding="utf-8").strip(), preview_text)

    def test_preview_builder_does_not_modify_fragment(self) -> None:
        theme, _ = load_theme("paper")
        fragment = render_document("# 标题\n\n正文。", theme)
        preview = build_preview(fragment, "标题")

        self.assertIn(fragment.strip(), preview)
        self.assertIn("copyArticle()", preview)
        self.assertEqual([], validate_html(fragment)[0])

    def test_preview_cli_refuses_an_invalid_fragment(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "invalid.html"
            preview = root / "preview.html"
            source.write_text("<section><p>未包裹</p></section>", encoding="utf-8")

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPTS / "wrap_preview.py"),
                    str(source),
                    str(preview),
                ],
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(1, result.returncode)
            self.assertFalse(preview.exists())


if __name__ == "__main__":
    unittest.main()
