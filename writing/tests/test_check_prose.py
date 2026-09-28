from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts/check_prose.py"


class ProseCheckTests(unittest.TestCase):
    def check(self, text, *args):
        result = subprocess.run([sys.executable, "-B", str(SCRIPT), "-", *args],
                                input=text, text=True, capture_output=True)
        self.assertEqual(0, result.returncode, result.stderr)
        return json.loads(result.stdout)

    def test_pivot_variants_are_advisory_with_original_locations(self):
        for text in ("你以为只是省事，其实关乎未来。", "不是速度。而是态度。",
                     "表面是工具。实际上是命运。", "与其说方便，倒不如说伟大。"):
            with self.subTest(text=text):
                source = "正文如下。\n" + text
                result = self.check(source)
                self.assertEqual("review_suggested", result["status"])
                findings = [f for f in result["findings"] if f["category"] == "pivot_shape"]
                self.assertTrue(findings)
                for finding in findings:
                    self.assertEqual(2, finding["line"])
                    self.assertEqual(source[finding["start"]:finding["end"]], finding["excerpt"])
                    self.assertEqual("advisory", finding["severity"])

    def test_real_correction_is_never_a_hard_failure(self):
        result = self.check("这不是同比增长20%，而是提高20个百分点。")
        self.assertNotIn(result["status"], {"fail", "pass"})
        self.assertTrue(all(f["severity"] == "advisory" for f in result["findings"]))
        self.assertNotIn("ai_probability", result)

    def test_valid_punctuation_and_literal_technical_terms_are_not_banned(self):
        result = self.check("准备三项：配置、数据和日志。日志保留七天——含今天。\n"
                            "闭环控制保持水温；沉淀经过过滤后移出，版面已经对齐。不丢人。")
        self.assertEqual("no_findings", result["status"])

    def test_quotes_code_urls_and_frontmatter_preserve_offsets(self):
        prefix = ('---\ntitle: 你以为方便，其实伟大\n---\n'
                  '```text\n不是速度。而是态度。\n```\n'
                  '~~~~text\n你以为方便，其实伟大。\n~~~~\n'
                  '> 你以为方便，其实伟大。\n'
                  '他说：“不是速度，而是态度。”\n'
                  '这是「你以为方便，其实伟大」的原话。\n'
                  '`你以为方便，其实伟大`\n'
                  'https://example.com/你以为方便其实伟大\n'
                  '[来源](https://example.com/不是速度而是态度)\n')
        self.assertEqual([], self.check(prefix)["findings"])
        text = prefix + "你以为方便，其实伟大。"
        findings = self.check(text)["findings"]
        self.assertTrue(findings)
        self.assertTrue(all(f["line"] == prefix.count("\n") + 1 for f in findings))

    def test_link_label_is_prose_but_target_is_not(self):
        result = self.check("[你以为方便，其实伟大](https://example.com)")
        self.assertIn("pivot_shape", {f["category"] for f in result["findings"]})

    def test_unclosed_fence_protects_remaining_code(self):
        result = self.check("普通说明。\n~~~text\n你以为方便，其实伟大。")
        self.assertEqual([], result["findings"])

    def test_repetition_nominalization_and_parallelism_are_review_candidates(self):
        text = "记录能找回。记录能找回。\n团队完成了对流程的优化。\n我们看见方向，我们看见希望，我们看见未来。"
        categories = {f["category"] for f in self.check(text)["findings"]}
        self.assertTrue({"repeated_sentence", "nominalization", "parallel_shape"} <= categories)

    def test_equal_sentence_lengths_are_statistics_not_authorship(self):
        result = self.check("甲方登记。乙方签字。丙方复核。")
        self.assertEqual(3, result["metrics"]["sentence_count"])
        self.assertEqual(0.0, result["metrics"]["sentence_length_cv"])
        self.assertEqual("no_findings", result["status"])

    def test_empty_and_non_chinese_input_are_not_evaluated(self):
        for text in ("", "The wind is quiet.", "```\n中文代码\n```"):
            with self.subTest(text=text):
                result = self.check(text)
                self.assertEqual("not_evaluated", result["status"])
                self.assertEqual([], result["findings"])

    def test_genre_exceptions_are_not_prose_failures(self):
        for genre in ("fiction", "poetry", "dialogue", "technical"):
            with self.subTest(genre=genre):
                result = self.check("你以为是风，其实是雨。", "--genre", genre)
                self.assertEqual("not_evaluated", result["status"])
                self.assertEqual([], result["findings"])

    def test_file_is_read_only_and_matches_stdin(self):
        text = "团队完成了对流程的优化。"
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "draft.md"
            path.write_text(text, encoding="utf-8")
            result = subprocess.run([sys.executable, "-B", str(SCRIPT), str(path)],
                                    text=True, capture_output=True)
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertEqual(self.check(text), json.loads(result.stdout))
            self.assertEqual(text, path.read_text(encoding="utf-8"))

    def test_missing_file_is_an_execution_error(self):
        with tempfile.TemporaryDirectory() as directory:
            result = subprocess.run([sys.executable, "-B", str(SCRIPT), str(Path(directory) / "absent")],
                                    text=True, capture_output=True)
            self.assertEqual(2, result.returncode)
            self.assertTrue(result.stderr)


if __name__ == "__main__":
    unittest.main()
