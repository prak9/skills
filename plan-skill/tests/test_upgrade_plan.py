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
