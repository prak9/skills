from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "validate_research", ROOT / "research-craft/scripts/validate_research.py"
)
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)
FIXTURE = ROOT / "research-craft/evals/report-package"


class ResearchPackageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "package"
        shutil.copytree(FIXTURE, self.root)

    def refresh_hashes(self):
        path = self.root / ".verify/review.json"
        receipt = json.loads(path.read_text())
        for name in receipt["input_hashes"]:
            source = self.root / name
            if source.is_file():
                receipt["input_hashes"][name] = hashlib.sha256(source.read_bytes()).hexdigest()
        path.write_text(json.dumps(receipt))

    def edit_row(self, filename, change):
        path = self.root / filename
        with path.open(newline="") as stream:
            reader = csv.DictReader(stream)
            fields, rows = reader.fieldnames, list(reader)
        change(rows)
        with path.open("w", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)
        self.refresh_hashes()

    def assert_issue(self, token):
        result = validator.validate(self.root)
        self.assertFalse(result["ok"], result)
        self.assertTrue(any(token in error for error in result["errors"]), result)

    def test_valid_synthetic_report_preserves_contested_conclusion(self):
        result = validator.validate(self.root)
        self.assertTrue(result["ok"], result)
        self.assertTrue(result["limits"])

    def test_honest_insufficient_result_needs_no_invented_sources(self):
        for name in ("sources.csv", "evidence.csv", "numbers.csv"):
            self.edit_row(name, lambda rows: rows.clear())
        def insufficient(rows):
            for row in rows:
                row.update(status="insufficient", confidence="low", evidence_ids="", dissent_ids="",
                           rationale="The fixture search returned no usable evidence.",
                           limitations="Cannot determine either requested result.")
        self.edit_row("claims.csv", insufficient)
        path = self.root / "research.json"
        data = json.loads(path.read_text())
        for question in data["questions"]:
            question.update(status="insufficient", reason="Attempted fixture lookup found no usable source; the conclusion remains unknown.")
        path.write_text(json.dumps(data))
        (self.root / "report.md").write_text(
            "# Synthetic insufficient result\n\n## Count change\n"
            "No usable evidence after fixture lookup; the count change is unknown. [C1](claims.csv)\n\n"
            "## Latency claim\nNo usable evidence after fixture lookup; latency is unknown. [C2](claims.csv)\n"
        )
        (self.root / "memo.md").write_text("Both requested results remain unknown after fixture lookup. [C1](claims.csv) [C2](claims.csv)\n")
        path = self.root / ".verify/review.json"
        data = json.loads(path.read_text())
        data["checks"] = [check for check in data["checks"] if check["kind"] != "access"]
        for check in data["checks"]:
            check.update(status="limited", reason="Synthetic no-source fixture: no affirmative finding is asserted.")
        path.write_text(json.dumps(data))
        self.refresh_hashes()
        result = validator.validate(self.root)
        self.assertTrue(result["ok"], result)
        self.assertTrue(result["limits"])

    def run_cli(self):
        return subprocess.run([sys.executable, str(SPEC.origin), str(self.root)],
                              capture_output=True, text=True, check=False)

    def test_cli_success_is_read_only_and_reports_scope(self):
        before = {str(path.relative_to(self.root)): path.read_bytes()
                  for path in self.root.rglob("*") if path.is_file()}
        result = self.run_cli()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("not independent", json.loads(result.stdout)["scope"])
        after = {str(path.relative_to(self.root)): path.read_bytes()
                 for path in self.root.rglob("*") if path.is_file()}
        self.assertEqual(before, after)

    def test_cli_violation_exit_status(self):
        self.edit_row("numbers.csv", lambda rows: rows[0].update(value="30"))
        result = self.run_cli()
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertFalse(json.loads(result.stdout)["ok"])

    def test_cli_malformed_input_exit_status(self):
        (self.root / "research.json").write_text("{invalid")
        result = self.run_cli()
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertFalse(json.loads(result.stdout)["ok"])

    def test_wrong_arithmetic_cannot_pass_with_fresh_receipt(self):
        self.edit_row("numbers.csv", lambda rows: rows[0].update(value="30"))
        self.assert_issue("arithmetic")

    def test_expression_cannot_execute_code(self):
        self.edit_row("numbers.csv", lambda rows: rows[0].update(formula="__import__('os').system('false')"))
        self.assert_issue("formula")

    def test_duplicate_claim_id(self):
        self.edit_row("claims.csv", lambda rows: rows.append(dict(rows[0])))
        self.assert_issue("duplicate")

    def test_unregistered_source(self):
        self.edit_row("evidence.csv", lambda rows: rows[0].update(source_id="s99"))
        self.assert_issue("source")

    def test_dissent_cannot_disappear(self):
        self.edit_row("claims.csv", lambda rows: rows[1].update(dissent_ids=""))
        self.assert_issue("dissent")

    def test_contested_claim_cannot_be_high_confidence(self):
        self.edit_row("claims.csv", lambda rows: rows[1].update(confidence="high"))
        self.assert_issue("confidence")

    def test_context_cannot_become_support(self):
        self.edit_row("evidence.csv", lambda rows: rows[0].update(relation="context"))
        self.assert_issue("support")

    def test_outline_cannot_drop_contested_findings(self):
        self.edit_row("outline.csv", lambda rows: rows.pop())
        self.assert_issue("outline")

    def test_open_question_blocks_complete_package(self):
        path = self.root / "research.json"
        data = json.loads(path.read_text())
        data["questions"][0]["status"] = "open"
        path.write_text(json.dumps(data))
        self.refresh_hashes()
        self.assert_issue("open")

    def test_stale_receipt_after_summary_edit(self):
        path = self.root / "memo.md"
        path.write_text(path.read_text() + "\nUnreviewed new assertion.\n")
        self.assert_issue("stale")

    def test_missing_semantic_axis(self):
        path = self.root / ".verify/review.json"
        data = json.loads(path.read_text())
        data["checks"] = [row for row in data["checks"] if row["kind"] != "qualifiers"]
        path.write_text(json.dumps(data))
        self.assert_issue("qualifiers")

    def test_path_cannot_escape_package(self):
        self.edit_row("sources.csv", lambda rows: rows[0].update(file="../outside.md"))
        self.assert_issue("path")

    def test_unknown_numeric_input_source(self):
        def mutate(rows):
            inputs = json.loads(rows[0]["inputs"])
            inputs["a"]["source_id"] = "s99"
            rows[0]["inputs"] = json.dumps(inputs)
        self.edit_row("numbers.csv", mutate)
        self.assert_issue("input source")

    def test_nonfinite_value_rejected(self):
        self.edit_row("numbers.csv", lambda rows: rows[0].update(value="NaN"))
        self.assert_issue("finite")

    def test_broken_report_link(self):
        path = self.root / "report.md"
        path.write_text(path.read_text() + "\n[missing](sources/missing.md)\n")
        self.refresh_hashes()
        self.assert_issue("link")

    def test_paraphrase_cannot_be_labeled_verbatim_quote(self):
        self.edit_row("evidence.csv", lambda rows: rows[0].update(text="The experiment proves the method is universally better."))
        self.assert_issue("quote")


if __name__ == "__main__":
    unittest.main()
