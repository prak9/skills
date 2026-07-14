from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


PLAN_SKILL_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = PLAN_SKILL_ROOT / "scripts" / "validate_plan.py"
EXAMPLE = PLAN_SKILL_ROOT / "examples" / "csv-export"
LITE_EXAMPLE = PLAN_SKILL_ROOT / "examples" / "lite-change"


class ValidatePlanTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.root = Path(self.temp_dir.name) / "project"
        shutil.copytree(EXAMPLE, self.root)

    def run_validator(self, *extra_args: str) -> tuple[subprocess.CompletedProcess[str], dict]:
        process = subprocess.run(
            [sys.executable, "-B", str(VALIDATOR), str(self.root), "--json", *extra_args],
            check=False,
            capture_output=True,
            text=True,
        )
        result = json.loads(process.stdout)
        return process, result

    def replace(self, relative_path: str, old: str, new: str, count: int = -1) -> None:
        path = self.root / relative_path
        text = path.read_text(encoding="utf-8")
        self.assertIn(old, text)
        path.write_text(text.replace(old, new, count), encoding="utf-8")

    def assert_rejected(self, *messages: str) -> dict:
        process, result = self.run_validator()
        self.assertNotEqual(0, process.returncode, process.stdout)
        self.assertFalse(result["ok"], result)
        errors = "\n".join(result["errors"])
        for message in messages:
            self.assertIn(message, errors)
        return result

    def mark_completed(self) -> None:
        self.replace("program.md", "- Overall status: `进行中`", "- Overall status: `完成`")
        self.replace(
            "program.md",
            "- Active task package: `tasks/TASK-001-add-export.md`",
            "- Active task package: `None`",
        )
        self.replace("program.md", "- Active plan node: `NODE-001`", "- Active plan node: `None`")
        self.replace("program.md", "- Latest evidence: RUN-001", "- Latest evidence: RUN-002")
        self.replace("program.md", "- Next checkpoint: CP-001", "- Next checkpoint: None")
        self.replace(
            "program.md",
            "| NODE-001 | `进行中` |",
            "| NODE-001 | `完成` |",
        )
        self.replace(
            "program.md",
            "- [ ] NODE-001 / tasks/TASK-001-add-export.md: CSV export",
            "- [x] NODE-001 / tasks/TASK-001-add-export.md: CSV export",
        )
        self.replace(
            "program.md",
            "| NODE-001 | `完成` | `tasks/TASK-001-add-export.md` | RUN-001 |",
            "| NODE-001 | `完成` | `tasks/TASK-001-add-export.md` | RUN-002 |",
        )
        self.replace(
            "program.md",
            "| History summary | pending | TASK-001 | memory.md#5-history-summaries | 2026-07-11 |",
            "| History summary | written | HIST-001 | memory.md#5-history-summaries | 2026-07-11 |",
        )
        self.replace("program.md", "- Next step: N-002 CLI flag", "- Next step: None")
        self.replace(
            "program.md",
            "- Next human decision: Review the exported sample at CP-001.",
            "- Next human decision: None",
        )
        task = "tasks/TASK-001-add-export.md"
        self.replace(task, "- Status: `进行中`", "- Status: `完成`")
        self.replace(task, "| N-002 | `待开始` |", "| N-002 | `完成` |")
        self.replace(
            task,
            "| N-002 | `完成` | N-001 | CLI 加 --csv 参数 | pytest tests/test_cli.py | 待运行 |",
            "| N-002 | `完成` | N-001 | CLI 加 --csv 参数 | pytest tests/test_cli.py | RUN-002 |",
        )
        self.replace(
            task,
            "| V-002 | N-002 | pytest tests/test_cli.py | 全部通过 | `待验证` | 待运行 |",
            "| V-002 | N-002 | pytest tests/test_cli.py | 全部通过 | `完成` | RUN-002 |",
        )
        self.replace(task, "- [ ]", "- [x]")
        self.replace(task, "待任务收尾时作答", "已根据对应问题复核，证据见 RUN-002")
        self.replace(
            task,
            "- Memory writeback: RUN-001 / F-001 已写入；完成时补 CHG 与 H 条目并跑提炼",
            "- Memory writeback: RUN-001 / RUN-002 / CHG-001 / HIST-001",
        )
        self.replace(task, "- Final result: 待完成", "- Final result: CLI CSV export verified end-to-end")
        self.replace(
            task,
            "- Output artifacts: `tasks/output/TASK-001-add-export/` 待 N-002 后刷新",
            "- Output artifacts: `tasks/output/TASK-001-add-export/` current",
        )
        self.replace(task, "- Completed: 待完成", "- Completed: 2026-07-11")
        self.replace(
            "memory.md",
            "| RUN-001 | 2026-07-11 | TASK-001 N-001 | test | Ran `pytest tests/test_export.py` with escaping cases. | passed | ci run 118 | N-002 | K-001 |",
            "| RUN-001 | 2026-07-11 | TASK-001 N-001 | test | Ran `pytest tests/test_export.py` with escaping cases. | passed | ci run 118 | N-002 | K-001 |\n| RUN-002 | 2026-07-11 | TASK-001 N-002 | test | Ran CLI and end-to-end export checks. | passed | ci run 119 | none | 不需要 |",
        )
        self.replace(
            "memory.md",
            "None yet; the first task package is still in progress.",
            "| ID | Time | Scope | Result | Key evidence | Lesson / later impact |\n|---|---|---|---|---|---|\n| HIST-001 | 2026-07-11 | TASK-001 | 完成 | RUN-001 / RUN-002 | CSV export is verified end-to-end. |",
        )

    def test_golden_example_passes(self) -> None:
        process, result = self.run_validator()

        self.assertEqual(0, process.returncode, process.stdout)
        self.assertTrue(result["ok"], result)
        self.assertEqual([], result["errors"])
        self.assertEqual([], result["warnings"])
        program = (self.root / "program.md").read_text(encoding="utf-8")
        self.assertNotRegex(program, r"(?m)^##\s+\d+\.")
        self.assertIn("| Node | Status | Task package | Evidence |", program)
        self.assertIn("| Node | Size | Dependencies | Acceptance | Updated |", program)

    def test_legacy_wide_node_status_still_passes(self) -> None:
        compact = """| Node | Status | Task package | Evidence |
|---|---|---|---|
| NODE-001 | `进行中` | `tasks/TASK-001-add-export.md` | RUN-001 |

### Node Details

| Node | Size | Dependencies | Acceptance | Updated |
|---|---|---|---|---|
| NODE-001 | `Medium` | None | A-001 | 2026-07-11 |"""
        legacy = """| Node | Phase | Status | Size | Task package | Output snapshot | Goal | Dependencies | Acceptance / Verification | Evidence | Updated |
|---|---|---|---|---|---|---|---|---|---|---|
| NODE-001 | Phase 1 | `进行中` | `Medium` | `tasks/TASK-001-add-export.md` | `tasks/output/TASK-001-add-export/` | CSV export works | None | A-001 | RUN-001 | 2026-07-11 |"""
        self.replace("program.md", compact, legacy)

        process, result = self.run_validator()

        self.assertEqual(0, process.returncode, process.stdout)
        self.assertTrue(result["ok"], result)

    def test_filled_lite_example_passes_strict_validation(self) -> None:
        process = subprocess.run(
            [
                sys.executable,
                "-B",
                str(VALIDATOR),
                str(LITE_EXAMPLE),
                "--json",
                "--strict",
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        result = json.loads(process.stdout)

        self.assertEqual(0, process.returncode, process.stdout)
        self.assertTrue(result["ok"], result)
        self.assertEqual("Lite", result["profile"])
        self.assertEqual([], result["warnings"])
        program = (LITE_EXAMPLE / "program.md").read_text(encoding="utf-8")
        self.assertIsNone(re.search(r"(?m)^##\s+\d+\.", program))
        self.assertIn("| Node | Status | Task package | Evidence |", program)

    def test_unresolved_profile_choice_is_rejected(self) -> None:
        self.replace("program.md", "- Profile: `Full`", "- Profile: `Lite / Full`")
        (self.root / "memory.md").unlink()

        self.assert_rejected("Profile")

    def test_invalid_top_level_statuses_are_rejected(self) -> None:
        self.replace("program.md", "- Overall status: `进行中`", "- Overall status: `done`")
        self.replace(
            "tasks/TASK-001-add-export.md",
            "- Status: `进行中`",
            "- Status: `done`",
        )

        self.assert_rejected("Overall status", "task package Status")

    def test_orphan_task_package_is_rejected(self) -> None:
        orphan = self.root / "tasks" / "TASK-002-orphan.md"
        orphan.write_text("# malformed orphan\n- Status: `完成`\n", encoding="utf-8")

        result = self.assert_rejected("not referenced by program.md")
        self.assertIn(str(orphan), result["checked"])

    def test_completed_task_requires_completed_nodes_red_team_and_writeback(self) -> None:
        self.replace("program.md", "- Overall status: `进行中`", "- Overall status: `完成`")
        self.replace(
            "program.md",
            "| NODE-001 | `进行中` |",
            "| NODE-001 | `完成` |",
        )
        self.replace(
            "tasks/TASK-001-add-export.md",
            "- Status: `进行中`",
            "- Status: `完成`",
        )
        self.replace("tasks/TASK-001-add-export.md", "- [ ]", "- [x]")

        self.assert_rejected("N-002", "V-002", "Red Team", "Completion Writeback")

    def test_loop_mode_requires_contract_and_matches_task_mode(self) -> None:
        self.replace("program.md", "- Plan mode: `Linear`", "- Plan mode: `Loop`")
        self.replace(
            "program.md",
            "Not applicable (Linear).",
            "L-001 exists, but the Loop contract is otherwise empty.",
        )

        self.assert_rejected("Loop Contract", "Plan mode mismatch")

    def test_valid_loop_contract_passes(self) -> None:
        self.replace("program.md", "- Plan mode: `Linear`", "- Plan mode: `Loop`")
        self.replace("program.md", "- Loop state: `Not applicable`", "- Loop state: `Plan`")
        self.replace("program.md", "- Loop iteration: `Not applicable`", "- Loop iteration: `1/3`")
        self.replace(
            "program.md",
            "### Loop Contract\n\nNot applicable (Linear).",
            """### Loop Contract

| Field | Content |
|---|---|
| Loop goal | Make CSV export pass end-to-end |
| Success criteria | A-001 passes |
| Failure signal | pytest failure |
| Verifier | pytest tests/test_export.py tests/test_cli.py |
| Max iterations | 3 |
| Reflect trigger | verifier failure |
| Iterate rule | change implementation, keep A-001 fixed |
| Stop / escalation condition | three failed iterations |
| Memory write rule | record failed runs in memory.md |
""",
        )
        self.replace(
            "program.md",
            "### Loop State\n\nNot applicable.",
            """### Loop State

| Iteration | Node | Step | Current hypothesis / plan delta | Verification | Latest result | Decision | Next |
|---|---|---|---|---|---|---|---|
| L-001 | NODE-001 | Plan | Implement CLI flag | pytest tests/test_cli.py | 待验证 | continue | N-002 |
""",
        )
        self.replace(
            "tasks/TASK-001-add-export.md",
            "- Plan mode: `Linear`",
            "- Plan mode: `Loop`\n- Loop budget: `3`",
        )
        self.replace(
            "tasks/TASK-001-add-export.md",
            "## Current Loop Attempt\n\n不适用（Linear）。",
            """## Current Loop Attempt

| Iteration | Loop step | Node | Attempt | Verification result | Reflection | Plan delta | Next |
|---|---|---|---|---|---|---|---|
| L-001 | Plan | N-002 | Add the CLI flag | 待验证 | Not run yet | None | Act |
""",
        )

        process, result = self.run_validator()

        self.assertEqual(0, process.returncode, process.stdout)
        self.assertTrue(result["ok"], result)
        self.assertEqual([], result["errors"])

    def test_valid_completed_plan_passes(self) -> None:
        self.mark_completed()

        process, result = self.run_validator()

        self.assertEqual(0, process.returncode, process.stdout)
        self.assertTrue(result["ok"], result)
        self.assertEqual([], result["errors"])

    def test_structural_abstraction_requires_complete_gate(self) -> None:
        self.replace(
            "tasks/TASK-001-add-export.md",
            "| Concept count / indirection | One exporter removes per-caller quoting branches and keeps one serialization concept; the CLI retains only argument and file-path handling. |",
            "| Concept count / indirection | pending |",
        )

        self.assert_rejected("Abstraction Gate is incomplete", "Concept count / indirection")

    def test_none_abstraction_requires_concrete_reason(self) -> None:
        self.replace(
            "tasks/TASK-001-add-export.md",
            "- Abstraction impact: `new`",
            "- Abstraction impact: `none`",
        )

        self.assert_rejected("Abstraction impact `none`", "N/A: <concrete reason>")

    def test_none_abstraction_rejects_leftover_gate_table(self) -> None:
        self.replace(
            "tasks/TASK-001-add-export.md",
            "- Abstraction impact: `new`",
            "- Abstraction impact: `none`",
        )
        self.replace(
            "tasks/TASK-001-add-export.md",
            "## Abstraction Gate\n\n| Field | Content |",
            "## Abstraction Gate\n\nN/A: This task changes no shared abstraction.\n\n| Field | Content |",
        )

        self.assert_rejected("must replace the unused gate table")

    def test_missing_abstraction_impact_warns_until_strict_validation(self) -> None:
        self.replace(
            "tasks/TASK-001-add-export.md",
            "- Abstraction impact: `new`\n",
            "",
        )

        normal_process, normal_result = self.run_validator()
        strict_process, strict_result = self.run_validator("--strict")

        self.assertEqual(0, normal_process.returncode, normal_process.stdout)
        self.assertTrue(normal_result["ok"], normal_result)
        self.assertIn("must declare Abstraction impact", "\n".join(normal_result["warnings"]))
        self.assertNotEqual(0, strict_process.returncode, strict_process.stdout)
        self.assertFalse(strict_result["ok"], strict_result)

    def test_modify_and_remove_abstractions_accept_complete_gate(self) -> None:
        for previous, impact in (("new", "modify"), ("modify", "remove")):
            self.replace(
                "tasks/TASK-001-add-export.md",
                f"- Abstraction impact: `{previous}`",
                f"- Abstraction impact: `{impact}`",
            )
            process, result = self.run_validator()
            self.assertEqual(0, process.returncode, process.stdout)
            self.assertTrue(result["ok"], result)

    def test_unknown_abstraction_impact_is_rejected(self) -> None:
        self.replace(
            "tasks/TASK-001-add-export.md",
            "- Abstraction impact: `new`",
            "- Abstraction impact: `maybe`",
        )

        self.assert_rejected("Abstraction impact must be exactly one of", "maybe")

    def test_program_waiting_acceptance_rejects_in_progress_node(self) -> None:
        self.replace("program.md", "- Overall status: `进行中`", "- Overall status: `待验收`")

        self.assert_rejected("Overall status is `待验收`", "`进行中`")

    def test_blocked_program_requires_concrete_current_blocker(self) -> None:
        self.replace("program.md", "- Overall status: `进行中`", "- Overall status: `阻塞`")
        self.replace(
            "program.md",
            "| NODE-001 | `进行中` |",
            "| NODE-001 | `阻塞` |",
        )
        self.replace(
            "tasks/TASK-001-add-export.md",
            "- Status: `进行中`",
            "- Status: `阻塞`",
        )

        self.assert_rejected("Overall status is `阻塞`", "Current blocker")

    def test_valid_waiting_acceptance_plan_passes(self) -> None:
        self.mark_completed()
        self.replace("program.md", "- Overall status: `完成`", "- Overall status: `待验收`")
        self.replace(
            "program.md",
            "| NODE-001 | `完成` |",
            "| NODE-001 | `待验收` |",
        )
        self.replace(
            "program.md",
            "- [x] NODE-001 / tasks/TASK-001-add-export.md: CSV export",
            "- [ ] NODE-001 / tasks/TASK-001-add-export.md: CSV export",
        )
        self.replace("program.md", "- Next checkpoint: None", "- Next checkpoint: CP-001")
        self.replace(
            "program.md",
            "- Next human decision: None",
            "- Next human decision: Review the exported sample at CP-001.",
        )
        self.replace(
            "tasks/TASK-001-add-export.md",
            "- Status: `完成`",
            "- Status: `待验收`",
        )

        process, result = self.run_validator()

        self.assertEqual(0, process.returncode, process.stdout)
        self.assertTrue(result["ok"], result)
        self.assertEqual([], result["errors"])

    def test_task_filename_id_must_match_h1_id(self) -> None:
        self.replace(
            "tasks/TASK-001-add-export.md",
            "# TASK-001: CSV 导出",
            "# TASK-999: CSV 导出",
        )

        self.assert_rejected("filename ID", "TASK-001", "TASK-999")

    def test_duplicate_atomic_node_id_is_rejected(self) -> None:
        self.replace(
            "tasks/TASK-001-add-export.md",
            "| N-002 | `待开始` |",
            "| N-001 | `待开始` |",
        )

        self.assert_rejected("duplicate atomic node ID", "N-001")

    def test_duplicate_verification_id_is_rejected(self) -> None:
        self.replace(
            "tasks/TASK-001-add-export.md",
            "| V-002 | N-002 |",
            "| V-001 | N-002 |",
        )

        self.assert_rejected("duplicate verification ID", "V-001")

    def test_duplicate_memory_primary_id_is_rejected(self) -> None:
        self.replace("memory.md", "| K-001 | implementation |", "| F-001 | implementation |")

        self.assert_rejected("duplicate memory ID", "F-001")

    def test_inline_code_pipe_in_table_cell_is_parsed_as_content(self) -> None:
        self.mark_completed()
        self.replace(
            "tasks/TASK-001-add-export.md",
            "| V-002 | N-002 | pytest tests/test_cli.py |",
            "| V-002 | N-002 | `printf 'a|b'` |",
        )

        process, result = self.run_validator()

        self.assertEqual(0, process.returncode, process.stdout)
        self.assertTrue(result["ok"], result)

    def test_malformed_table_row_with_unclosed_code_span_is_rejected(self) -> None:
        self.mark_completed()
        self.replace(
            "tasks/TASK-001-add-export.md",
            "| V-002 | N-002 | pytest tests/test_cli.py |",
            "| V-002 | N-002 | `printf 'a|b' |",
        )

        self.assert_rejected("column count", "V-002")

    def test_non_utf8_input_returns_structured_json_error(self) -> None:
        (self.root / "memory.md").write_bytes(b"\xff")

        process = subprocess.run(
            [sys.executable, "-B", str(VALIDATOR), str(self.root), "--json"],
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertNotEqual(0, process.returncode)
        self.assertTrue(process.stdout, process.stderr)
        result = json.loads(process.stdout)
        self.assertFalse(result["ok"])
        self.assertIn("not UTF-8", "\n".join(result["errors"]))

    def test_non_file_input_returns_structured_json_error(self) -> None:
        memory_path = self.root / "memory.md"
        memory_path.unlink()
        memory_path.mkdir()

        process = subprocess.run(
            [sys.executable, "-B", str(VALIDATOR), str(self.root), "--json"],
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertNotEqual(0, process.returncode)
        self.assertTrue(process.stdout, process.stderr)
        result = json.loads(process.stdout)
        self.assertFalse(result["ok"])
        self.assertIn("Cannot read", "\n".join(result["errors"]))

    def test_task_symlink_outside_project_root_is_rejected(self) -> None:
        task_path = self.root / "tasks" / "TASK-001-add-export.md"
        task_text = task_path.read_text(encoding="utf-8")
        outside = Path(self.temp_dir.name) / "outside-task.md"
        outside.write_text(task_text, encoding="utf-8")
        task_path.unlink()
        try:
            task_path.symlink_to(outside)
        except OSError as exc:
            self.skipTest(f"symlinks are unavailable: {exc}")

        self.assert_rejected("escapes the project root")

    def test_json_diagnostics_include_status_and_counts(self) -> None:
        process, result = self.run_validator()

        self.assertEqual(0, process.returncode, process.stdout)
        self.assertEqual("pass", result["status"])
        self.assertEqual(0, result["error_count"])
        self.assertEqual(0, result["warning_count"])

    def test_completion_memory_writeback_refs_must_exist(self) -> None:
        self.mark_completed()
        self.replace("memory.md", "RUN-002", "RUN-999")

        self.assert_rejected("Memory writeback", "RUN-002")

    def test_completed_program_requires_terminal_current_status(self) -> None:
        self.mark_completed()
        self.replace("program.md", "- Next step: None", "- Next step: N-002 CLI flag")

        self.assert_rejected("Current Status", "Next step")

    def test_completed_task_requires_nonempty_acceptance_checklist(self) -> None:
        self.mark_completed()
        self.replace(
            "tasks/TASK-001-add-export.md",
            "- [x] --csv 参数生成文件，内容与查询结果一致",
            "- --csv 参数生成文件，内容与查询结果一致",
        )
        self.replace(
            "tasks/TASK-001-add-export.md",
            "- [x] 含逗号、引号、换行的字段转义正确",
            "- 含逗号、引号、换行的字段转义正确",
        )

        self.assert_rejected("Acceptance criteria", "no checklist items")

    def test_completed_task_requires_at_least_one_atomic_node(self) -> None:
        self.mark_completed()
        self.replace(
            "tasks/TASK-001-add-export.md",
            "| N-001 | `完成` | None | 写 exporter 模块与转义用例 | pytest tests/test_export.py | RUN-001 |\n",
            "",
        )
        self.replace(
            "tasks/TASK-001-add-export.md",
            "| N-002 | `完成` | N-001 | CLI 加 --csv 参数 | pytest tests/test_cli.py | RUN-002 |\n",
            "",
        )

        self.assert_rejected("Atomic Implementation Plan", "no atomic nodes")

    def test_full_completed_task_requires_verification_rows(self) -> None:
        self.mark_completed()
        self.replace(
            "tasks/TASK-001-add-export.md",
            "| V-001 | N-001 | pytest tests/test_export.py | 全部通过含转义用例 | `完成` | RUN-001 |\n",
            "",
        )
        self.replace(
            "tasks/TASK-001-add-export.md",
            "| V-002 | N-002 | pytest tests/test_cli.py | 全部通过 | `完成` | RUN-002 |\n",
            "",
        )

        self.assert_rejected("Verification Matrix", "no verification rows")

    def test_completed_verification_row_requires_evidence_column(self) -> None:
        self.mark_completed()
        self.replace(
            "tasks/TASK-001-add-export.md",
            "| Check | Covers | Method/command | Pass condition | Status | Evidence |",
            "| Check | Covers | Method/command | Pass condition | Status |",
        )

        self.assert_rejected("V-001", "evidence column")

    def test_pending_english_writeback_value_is_not_concrete(self) -> None:
        self.mark_completed()
        self.replace(
            "tasks/TASK-001-add-export.md",
            "- Final result: CLI CSV export verified end-to-end",
            "- Final result: pending",
        )

        self.assert_rejected("Completion Writeback", "Final result")

    def test_task_plan_node_must_match_program_mapping(self) -> None:
        self.replace(
            "tasks/TASK-001-add-export.md",
            "- Plan node: NODE-001",
            "- Plan node: NODE-999",
        )

        self.assert_rejected("Plan node mismatch")

    def test_duplicate_node_status_mapping_is_rejected(self) -> None:
        row = "| NODE-001 | `进行中` | `tasks/TASK-001-add-export.md` | RUN-001 |"
        duplicate = (
            row
            + "\n| NODE-002 | `进行中` | `tasks/TASK-001-add-export.md` | None |"
        )
        self.replace("program.md", row, duplicate)

        self.assert_rejected("multiple Node Status rows")

    def test_node_dependency_cycle_is_rejected(self) -> None:
        self.replace(
            "program.md",
            "| NODE-001 | `Medium` | None | A-001 |",
            "| NODE-001 | `Medium` | NODE-001 | A-001 |",
        )

        self.assert_rejected("dependency cycle")

    def test_closed_hypothesis_requires_evidence(self) -> None:
        self.replace(
            "program.md",
            "| F-001 / `src/query.py` REPL check |",
            "| None |",
        )

        self.assert_rejected("H-001", "evidence")

    def test_hypothesis_cannot_close_with_generic_completed_status(self) -> None:
        self.replace(
            "program.md",
            "| H-001 | supported |",
            "| H-001 | 完成 |",
        )

        self.assert_rejected("H-001", "verdict")

    def test_active_plan_node_must_match_active_task(self) -> None:
        self.replace("program.md", "- Active plan node: `NODE-001`", "- Active plan node: `NODE-999`")

        self.assert_rejected("Active plan node")

    def test_active_task_package_cannot_already_be_terminal(self) -> None:
        self.mark_completed()
        self.replace("program.md", "- Overall status: `完成`", "- Overall status: `进行中`")
        self.replace(
            "program.md",
            "- Active task package: `None`",
            "- Active task package: `tasks/TASK-001-add-export.md`",
        )
        self.replace("program.md", "- Active plan node: `None`", "- Active plan node: `NODE-001`")

        self.assert_rejected("Active task package", "terminal status")

    def test_task_list_checkbox_must_match_node_status(self) -> None:
        self.replace(
            "program.md",
            "- [ ] NODE-001 / tasks/TASK-001-add-export.md: CSV export",
            "- [x] NODE-001 / tasks/TASK-001-add-export.md: CSV export",
        )

        self.assert_rejected("Task List")

    def test_lite_profile_accepts_one_linear_task_without_memory(self) -> None:
        self.replace("program.md", "- Profile: `Full`", "- Profile: `Lite`")
        (self.root / "memory.md").unlink()

        process, result = self.run_validator()

        self.assertEqual(0, process.returncode, process.stdout)
        self.assertTrue(result["ok"], result)
        self.assertEqual("Lite", result["profile"])

    def test_lite_memory_is_optional_but_must_be_valid_when_present(self) -> None:
        self.replace("program.md", "- Profile: `Full`", "- Profile: `Lite`")
        (self.root / "memory.md").write_text("# Memory\n\nbroken\n", encoding="utf-8")

        self.assert_rejected("memory.md", "missing required")

    def test_lite_profile_with_more_than_three_tasks_requires_full(self) -> None:
        self.replace("program.md", "- Profile: `Full`", "- Profile: `Lite`")
        (self.root / "memory.md").unlink()
        source_task = (self.root / "tasks" / "TASK-001-add-export.md").read_text(encoding="utf-8")
        base_row = "| NODE-001 | `进行中` | `tasks/TASK-001-add-export.md` | RUN-001 |"
        rows = [base_row]
        tasks = ["- [ ] NODE-001 / tasks/TASK-001-add-export.md: CSV export"]
        for number in range(2, 5):
            suffix = f"{number:03d}"
            task_text = source_task.replace("TASK-001-add-export", f"TASK-{suffix}-add-export")
            task_text = task_text.replace("TASK-001", f"TASK-{suffix}")
            task_text = task_text.replace("NODE-001", f"NODE-{suffix}")
            (self.root / "tasks" / f"TASK-{suffix}-add-export.md").write_text(
                task_text,
                encoding="utf-8",
            )
            rows.append(
                base_row.replace("NODE-001", f"NODE-{suffix}").replace(
                    "TASK-001-add-export",
                    f"TASK-{suffix}-add-export",
                )
            )
            tasks.append(f"- [ ] NODE-{suffix} / tasks/TASK-{suffix}-add-export.md: CSV export")
        self.replace("program.md", base_row, "\n".join(rows))
        self.replace(
            "program.md",
            "- [ ] NODE-001 / tasks/TASK-001-add-export.md: CSV export",
            "\n".join(tasks),
        )

        self.assert_rejected("upgrade to `Full`")

    def test_strict_mode_fails_on_warnings(self) -> None:
        self.replace("memory.md", "None yet;", "<stale> None yet;")

        normal_process, normal_result = self.run_validator()
        strict_process, strict_result = self.run_validator("--strict")

        self.assertEqual(0, normal_process.returncode, normal_process.stdout)
        self.assertTrue(normal_result["ok"], normal_result)
        self.assertTrue(normal_result["warnings"])
        self.assertNotEqual(0, strict_process.returncode, strict_process.stdout)
        self.assertFalse(strict_result["ok"], strict_result)

    def test_output_pointer_must_be_correct_in_output_artifacts_section(self) -> None:
        self.replace(
            "tasks/TASK-001-add-export.md",
            "tasks/output/TASK-001-add-export/",
            "tasks/output/TASK-999-wrong/",
            count=3,
        )

        self.assert_rejected("Output Artifacts")

    def test_reincluded_output_directory_is_not_considered_ignored(self) -> None:
        (self.root / ".gitignore").write_text(
            "/tasks/output/\n!/tasks/output/\n!/tasks/output/**\n",
            encoding="utf-8",
        )

        self.assert_rejected("not ignored")

    @unittest.skipUnless(shutil.which("git"), "git is required for the tracked-output check")
    def test_tracked_output_artifact_is_rejected(self) -> None:
        output = self.root / "tasks" / "output" / "TASK-001-add-export" / "out.csv"
        output.parent.mkdir(parents=True)
        output.write_text("value\n", encoding="utf-8")
        subprocess.run(["git", "init", "-q", str(self.root)], check=True)
        subprocess.run(
            ["git", "-C", str(self.root), "add", "-f", "tasks/output/TASK-001-add-export/out.csv"],
            check=True,
        )

        self.assert_rejected("tracked by git")


if __name__ == "__main__":
    unittest.main()
