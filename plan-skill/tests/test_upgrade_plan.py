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
INITIALIZER = PLAN_SKILL_ROOT / "scripts" / "init_plan.py"
UPGRADER = PLAN_SKILL_ROOT / "scripts" / "upgrade_plan.py"
VALIDATOR = PLAN_SKILL_ROOT / "scripts" / "validate_plan.py"
sys.path.insert(0, str(PLAN_SKILL_ROOT / "scripts"))

from upgrade_plan import (  # noqa: E402
    inline_node_records,
    prepare_reflection_rows,
    validate_project,
)


class UpgradePlanTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.root = Path(self.temp_dir.name) / "project"
        process = subprocess.run(
            [
                sys.executable,
                "-B",
                str(INITIALIZER),
                str(self.root),
                "--title",
                "Upgrade Test",
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(0, process.returncode, process.stdout + process.stderr)

    def run_upgrader(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "-B", str(UPGRADER), str(self.root), *args],
            check=False,
            capture_output=True,
            text=True,
        )

    def replace(self, path: Path, old: str, new: str) -> None:
        text = path.read_text(encoding="utf-8")
        self.assertIn(old, text)
        path.write_text(text.replace(old, new), encoding="utf-8")

    def validate(self) -> dict:
        process = subprocess.run(
            [sys.executable, "-B", str(VALIDATOR), str(self.root), "--json"],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(0, process.returncode, process.stdout + process.stderr)
        return json.loads(process.stdout)

    def test_upgrade_preserves_lite_content_and_existing_memory(self) -> None:
        program_path = self.root / "program.md"
        self.replace(program_path, "<observable problem>", "UNIQUE LITE PROBLEM")
        self.replace(
            program_path,
            "<observable result>",
            "UNIQUE LITE SUCCESS",
        )
        self.replace(
            program_path,
            "<repo instructions, rules, skills, or specs that apply across this work; or None>",
            "STRATEGIC SAFETY DEFAULT",
        )
        self.replace(
            program_path,
            "<project-specific outcome or quality to optimize when valid solutions differ>",
            "TACTICAL LATENCY OBJECTIVE",
        )
        self.replace(
            program_path,
            "<required method, interface, threshold, or process and why; or None>",
            "IMPERATIVE API BOUND",
        )
        memory = (PLAN_SKILL_ROOT / "assets" / "memory-starter.template.md").read_text(
            encoding="utf-8"
        )
        memory = memory.replace("<Project Name>", "Upgrade Test").replace(
            "None yet.",
            "D-001: Keep the accepted CLI contract. Evidence: issue-17.",
            1,
        )
        (self.root / "memory.md").write_text(memory, encoding="utf-8")

        process = self.run_upgrader()

        self.assertEqual(0, process.returncode, process.stdout + process.stderr)
        program = program_path.read_text(encoding="utf-8")
        task_path = self.root / "tasks" / "TASK-001-upgrade-test.md"
        task = task_path.read_text(encoding="utf-8")
        upgraded_memory = (self.root / "memory.md").read_text(encoding="utf-8")
        self.assertIn("- Profile: `Full`", program)
        self.assertIn("- Execution readiness: `Not required`", program)
        self.assertIn("- Clean state: `Not due`", program)
        self.assertIn("- Last clean: `Not run`", program)
        self.assertIn("UNIQUE LITE PROBLEM", program)
        self.assertIn("UNIQUE LITE SUCCESS", program)
        self.assertIn("UNIQUE LITE SUCCESS", task)
        self.assertIn("STRATEGIC SAFETY DEFAULT", program)
        self.assertIn("TACTICAL LATENCY OBJECTIVE", program)
        self.assertIn("IMPERATIVE API BOUND", program)
        self.assertIn("Inherit `program.md`; overrides: None", task)
        self.assertIn("D-001", upgraded_memory)
        self.assertIn("D-002", upgraded_memory)
        result = self.validate()
        self.assertEqual("Full", result["profile"])
        self.assertEqual([], result["errors"])

    def test_upgrade_without_memory_creates_lean_full_state(self) -> None:
        process = self.run_upgrader()

        self.assertEqual(0, process.returncode, process.stdout + process.stderr)
        memory_path = self.root / "memory.md"
        task_path = self.root / "tasks" / "TASK-001-upgrade-test.md"
        self.assertTrue(memory_path.is_file())
        self.assertTrue(task_path.is_file())
        self.assertIn("## Decisions", memory_path.read_text(encoding="utf-8"))
        self.assertIn("D-001", memory_path.read_text(encoding="utf-8"))
        generated = [self.root / "program.md", task_path, memory_path]
        placeholder_count = sum(
            len(re.findall(r"<[^>\n]+>", path.read_text(encoding="utf-8")))
            for path in generated
        )
        self.assertLessEqual(placeholder_count, 24)
        result = self.validate()
        self.assertEqual("Full", result["profile"])
        self.assertEqual([], result["errors"])

    def test_upgrade_does_not_add_a_human_approval(self) -> None:
        process = self.run_upgrader()

        self.assertEqual(0, process.returncode, process.stdout + process.stderr)
        program = (self.root / "program.md").read_text(encoding="utf-8")
        self.assertRegex(program, r"\| CP-001 \| NODE-001 \| [^\n]+ \| no \|")

    def test_upgrade_preserves_an_explicit_pending_human_decision(self) -> None:
        self.replace(
            self.root / "program.md",
            "- Next human decision: `None`",
            "- Next human decision: `Owner must approve the release after verification`",
        )

        process = self.run_upgrader()

        self.assertEqual(0, process.returncode, process.stdout + process.stderr)
        program = (self.root / "program.md").read_text(encoding="utf-8")
        self.assertIn(
            "Next human decision: Owner must approve the release after verification", program
        )
        self.assertRegex(program, r"\| CP-001 \| NODE-001 \| [^\n]+ \| yes \|")

    def test_upgrade_creates_task_from_inline_node(self) -> None:
        program_path = self.root / "program.md"
        self.replace(
            program_path,
            "<smallest useful step>",
            "Validate timeout at the CLI boundary",
        )

        process = self.run_upgrader()

        self.assertEqual(0, process.returncode, process.stdout + process.stderr)
        task = (self.root / "tasks" / "TASK-001-upgrade-test.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("Validate timeout at the CLI boundary", task)
        self.assertIn("## Completion Review", task)
        self.assertEqual([], self.validate()["errors"])

    def test_upgrade_preserves_lite_reflection_log(self) -> None:
        program_path = self.root / "program.md"
        self.replace(
            program_path,
            "| NODE-001 | `待开始` | <smallest useful step> | <command or scenario> | None | Pending |",
            "| NODE-001 | `进行中` | Inspect the boundary | pytest tests/test_cli.py | RUN-007 | R-007 |",
        )
        self.replace(
            program_path,
            "| ID | Scope | Evidence | Wrong / changed | Right / preserve | Next rule |\n|---|---|---|---|---|---|\n",
            (
                "| ID | Scope | Evidence | Wrong / changed | Right / preserve | Next rule |\n"
                "|---|---|---|---|---|---|\n"
                "| R-007 | NODE-001 | RUN-007 | The first boundary assumption was wrong. | The existing parser contract should stay. | Inspect callers before changing the parser. |\n"
            ),
        )

        process = self.run_upgrader()

        self.assertEqual(0, process.returncode, process.stdout + process.stderr)
        task = (self.root / "tasks" / "TASK-001-upgrade-test.md").read_text(
            encoding="utf-8"
        )
        memory = (self.root / "memory.md").read_text(encoding="utf-8")
        self.assertIn("RUN-007 | R-007", task)
        self.assertIn("| R-007 | NODE-001 | RUN-007 |", memory)

    def test_dry_run_reports_changes_without_writing(self) -> None:
        before = (self.root / "program.md").read_text(encoding="utf-8")

        process = self.run_upgrader("--dry-run")

        self.assertEqual(0, process.returncode, process.stdout + process.stderr)
        self.assertIn("Would upgrade", process.stdout)
        self.assertEqual(before, (self.root / "program.md").read_text(encoding="utf-8"))
        self.assertFalse((self.root / "memory.md").exists())
        self.assertFalse((self.root / "tasks").exists())

    def test_invalid_lite_plan_is_rejected_without_writes(self) -> None:
        program_path = self.root / "program.md"
        self.replace(program_path, "| NODE-001 | `待开始` |", "| NODE-001 | `done` |")
        before_program = program_path.read_text(encoding="utf-8")

        process = self.run_upgrader()

        self.assertNotEqual(0, process.returncode)
        self.assertIn("invalid", process.stderr.lower())
        self.assertEqual(before_program, program_path.read_text(encoding="utf-8"))
        self.assertFalse((self.root / "memory.md").exists())
        self.assertFalse((self.root / "tasks").exists())

    def test_already_full_plan_is_rejected(self) -> None:
        self.replace(self.root / "program.md", "- Profile: `Lite`", "- Profile: `Full`")

        process = self.run_upgrader()

        self.assertNotEqual(0, process.returncode)
        self.assertIn("already Full", process.stderr)


class UpgradePlanExampleTests(unittest.TestCase):
    def test_completed_lite_plan_upgrades_to_valid_completed_full_plan(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "lite-change"
            shutil.copytree(PLAN_SKILL_ROOT / "examples" / "lite-change", root)
            program_path = root / "program.md"
            text = program_path.read_text(encoding="utf-8")
            for old, new in (
                ("- Overall status: `进行中`", "- Overall status: `完成`"),
                ("- Active plan node: `NODE-001`", "- Active plan node: `None`"),
                ("- Latest evidence: `None`", "- Latest evidence: `RUN-001`"),
                ("- Next step: `NODE-001`", "- Next step: `None`"),
                ("| NODE-001 | `进行中` |", "| NODE-001 | `完成` |"),
                (
                    "| None | Pending |",
                    "| RUN-001 | None: verifier passed with no material learning |",
                ),
            ):
                self.assertIn(old, text)
                text = text.replace(old, new)
            program_path.write_text(text, encoding="utf-8")
            self.assertEqual([], validate_project(root)["errors"])

            process = subprocess.run(
                [sys.executable, "-B", str(UPGRADER), str(root)],
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(0, process.returncode, process.stdout + process.stderr)
            validation = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(VALIDATOR),
                    str(root),
                    "--strict",
                    "--json",
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(0, validation.returncode, validation.stdout + validation.stderr)
            self.assertEqual([], json.loads(validation.stdout)["errors"])
            program = program_path.read_text(encoding="utf-8")
            task = (root / "tasks" / "TASK-001-cli-timeout-validation.md").read_text(
                encoding="utf-8"
            )
            self.assertIn("- Overall status: `完成`", program)
            self.assertIn("- Active task package: `None`", program)
            self.assertIn("- Next step: `None`", program)
            self.assertIn("- Next checkpoint: `None`", program)
            self.assertIn("- Last clean: `N/A: Lite plan predates Clean metadata", program)
            self.assertIn("- Status: `完成`", task)
            self.assertEqual(2, task.count("- [x]"))
            self.assertIn("- Evidence: RUN-001", task)
            self.assertIn("- Remaining work: None", task)
            self.assertRegex(task, r"- Completed: \d{4}-\d{2}-\d{2}")

    def test_waiting_acceptance_lite_plan_preserves_pending_owner_decision(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "lite-change"
            shutil.copytree(PLAN_SKILL_ROOT / "examples" / "lite-change", root)
            program_path = root / "program.md"
            text = program_path.read_text(encoding="utf-8")
            for old, new in (
                ("- Overall status: `进行中`", "- Overall status: `待验收`"),
                ("- Latest evidence: `None`", "- Latest evidence: `RUN-001`"),
                ("- Next checkpoint: `None`", "- Next checkpoint: `CP-001`"),
                (
                    "- Next human decision: `None`",
                    "- Next human decision: `Owner must accept the verified CLI behavior`",
                ),
                ("| NODE-001 | `进行中` |", "| NODE-001 | `待验收` |"),
                (
                    "| None | Pending |",
                    "| RUN-001 | None: verifier passed with no material learning |",
                ),
            ):
                self.assertIn(old, text)
                text = text.replace(old, new)
            program_path.write_text(text, encoding="utf-8")
            self.assertEqual([], validate_project(root)["errors"])

            process = subprocess.run(
                [sys.executable, "-B", str(UPGRADER), str(root)],
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(0, process.returncode, process.stdout + process.stderr)
            validation = subprocess.run(
                [sys.executable, "-B", str(VALIDATOR), str(root), "--strict", "--json"],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(0, validation.returncode, validation.stdout + validation.stderr)
            task = (root / "tasks" / "TASK-001-cli-timeout-validation.md").read_text(
                encoding="utf-8"
            )
            self.assertIn("- Status: `待验收`", task)
            self.assertEqual(2, task.count("- [x]"))
            self.assertIn("- Completed: pending explicit owner decision", task)

    def test_valid_lite_routine_completion_does_not_gain_a_reflection(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "lite-change"
            shutil.copytree(PLAN_SKILL_ROOT / "examples" / "lite-change", root)
            program_path = root / "program.md"
            no_trigger = "None: routine pass produced no durable learning"
            text = program_path.read_text(encoding="utf-8").replace(
                "\n\n## Reflection Log",
                "\n| NODE-002 | `完成` | Verify the existing timeout parser | "
                "pytest tests/test_cli.py -k timeout | Fixture test run: 4 passed | "
                f"{no_trigger} |\n\n## Reflection Log",
            )
            program_path.write_text(text, encoding="utf-8")
            self.assertEqual([], validate_project(root)["errors"])
            nodes = inline_node_records(text)

            rows = prepare_reflection_rows(nodes, text, None, "2026-09-05")

            self.assertEqual([], rows)
            self.assertEqual(no_trigger, nodes[1]["reflection"])

    def test_legacy_missing_reflection_keeps_compatibility_record(self) -> None:
        nodes = [{
            "node": "NODE-001",
            "status": "完成",
            "reflection": "Pending",
            "evidence": "legacy run",
        }]

        rows = prepare_reflection_rows(nodes, "", None, "2026-09-05")

        self.assertEqual("R-001", nodes[0]["reflection"])
        self.assertEqual(1, len(rows))
        self.assertIn("Legacy Lite reflection details were not recorded", rows[0])

    def test_filled_lite_example_upgrades_without_losing_domain_content(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "lite-change"
            shutil.copytree(PLAN_SKILL_ROOT / "examples" / "lite-change", root)

            process = subprocess.run(
                [sys.executable, "-B", str(UPGRADER), str(root)],
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(0, process.returncode, process.stdout + process.stderr)
            program = (root / "program.md").read_text(encoding="utf-8")
            task = (root / "tasks" / "TASK-001-cli-timeout-validation.md").read_text(
                encoding="utf-8"
            )
            self.assertIn("Reject zero and negative timeout values", program)
            self.assertIn("- Clean state: `Not due`", program)
            self.assertIn("- Last clean: `Not run`", program)
            self.assertIn("Do not change retry or request semantics", task)
            validation = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(VALIDATOR),
                    str(root),
                    "--strict",
                    "--json",
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(0, validation.returncode, validation.stdout + validation.stderr)
            self.assertEqual([], json.loads(validation.stdout)["errors"])


if __name__ == "__main__":
    unittest.main()
