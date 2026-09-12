from __future__ import annotations

import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INVESTMENT_SKILL = "invest"

# Skills whose content was folded into a surviving skill. A live reference to one
# of these names is a dangling pointer for anyone following the instructions.
REMOVED_SKILLS = (
    "judgment-craft",
    "define-problem",
    "alpha-research",
    "linux-perf",
    "performance-patterns",
)


# Files a SKILL.md points at inside its own bundle. Bare filenames are excluded:
# several skills name files they create at runtime (`memory.md`, `manifest.json`).
BUNDLED_DIRS = ("references", "assets", "scripts", "evals", "agents")
PATH_IN_BACKTICKS = re.compile(
    r"`((?:" + "|".join(BUNDLED_DIRS) + r")/[A-Za-z0-9_./-]+)`"
)
MARKDOWN_LINK = re.compile(r"\]\(([^)]+)\)")


def skill_dirs() -> list[Path]:
    return sorted(
        d
        for d in ROOT.iterdir()
        if not d.name.startswith(".") and (d / "SKILL.md").is_file()
    )


def skill_text(name: str) -> str:
    return (ROOT / name / "SKILL.md").read_text(encoding="utf-8")


def reference_text(name: str, filename: str) -> str:
    return (ROOT / name / "references" / filename).read_text(encoding="utf-8")


def description(name: str) -> str:
    match = re.search(r"^description:\s*(.+)$", skill_text(name), flags=re.MULTILINE)
    if match is None:
        raise AssertionError(f"{name} has no one-line description")
    return match.group(1).strip().strip('"')


class SkillContractTests(unittest.TestCase):
    def test_claude_links_to_the_canonical_instruction_source(self) -> None:
        agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
        claude = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
        # Validate the instruction entry point, not one version's prose.
        self.assertTrue(agents.strip())
        self.assertIn("AGENTS.md", MARKDOWN_LINK.findall(claude))
        self.assertIn("single source", claude)

    def test_overlapping_skill_descriptions_have_explicit_boundaries(self) -> None:
        decision_description = description("decision")
        writing_description = description("writing")
        review_description = description("code-review-craft")
        research_description = description("research-craft")

        self.assertIn("不用于普通股票研究", decision_description)
        self.assertIn("文本本身是主要交付物", writing_description)
        self.assertIn("不要仅因其他领域任务", writing_description)
        self.assertIn("do not invoke merely because", review_description)
        self.assertIn("模型迁移", research_description)
        self.assertIn("不用于普通事实检索", research_description)

    def test_code_comprehension_avoids_duplicate_instruction_contracts(self) -> None:
        protocol = reference_text("code-review-craft", "comprehension-protocol.md")
        self.assertIn("applicable instruction chain once", protocol)
        self.assertIn("do not read duplicate aliases", protocol)

    def test_specialized_equity_modes_do_not_claim_bare_tickers(self) -> None:
        text = skill_text(INVESTMENT_SKILL)
        gf_dma = reference_text(INVESTMENT_SKILL, "mode-c-gf-dma.md")
        self.assertIn("Do not trigger Modes B, C, or E from a bare ticker", text)
        self.assertIn(
            "Do not trigger from a bare ticker or generic stock-analysis request",
            gf_dma,
        )

    def test_investment_skill_requires_explicit_external_mutation(self) -> None:
        text = skill_text(INVESTMENT_SKILL)
        self.assertNotIn("install with `pip install edgartools`", text)
        self.assertNotIn('set_identity("name@example.com")', text)
        self.assertIn("does not authorize a Notion write", text)

    def test_buy_side_memos_do_not_default_to_notion_writes(self) -> None:
        text = skill_text(INVESTMENT_SKILL)
        self.assertIn("## Notion Delivery", text)
        self.assertNotIn("archive to the Notion page or database named `Invest`", text)
        self.assertIn("Notion archive pending", text)

    def test_gf_dma_keeps_modules_but_disables_uncalibrated_aggregate(self) -> None:
        text = reference_text(INVESTMENT_SKILL, "mode-c-gf-dma.md")

        self.assertIn("currently always `N/A`", text)
        self.assertNotIn("HealthScore = 0.40*S_GrowthMatch", text)
        self.assertNotIn("If gross profit or EPS is missing", text)
        self.assertIn("EPS missing", text)
        self.assertIn("scripts/calculate_gf_dma.py", text)
        self.assertIn("uncalibrated heuristic", text)

    def test_invest_links_a_point_in_time_numeric_data_contract(self) -> None:
        text = skill_text(INVESTMENT_SKILL)
        contract = reference_text(INVESTMENT_SKILL, "data-contract.md")
        self.assertIn("references/data-contract.md", text)
        self.assertIn("scripts/validate_invest_data.py", text)
        self.assertIn("available_at", contract)
        self.assertIn("missing_reason", contract)
        self.assertIn("point-in-time validation", contract)

    def test_invest_is_a_compact_router_with_on_demand_modes(self) -> None:
        text = skill_text(INVESTMENT_SKILL)
        self.assertLessEqual(len(text.splitlines()), 190)
        for filename in (
            "mode-a-buy-side.md",
            "mode-b-bayesian-growth.md",
            "mode-c-gf-dma.md",
            "mode-d-serenity-alpha.md",
            "mode-e-tam-adj-peg.md",
        ):
            self.assertIn(f"references/{filename}", text)
            self.assertTrue((ROOT / INVESTMENT_SKILL / "references" / filename).is_file())

    def test_cross_skill_handoff_preserves_upstream_decisions(self) -> None:
        for name in ("decision", "invest", "plan-skill", "writing"):
            text = skill_text(name)
            with self.subTest(skill=name):
                self.assertIn("do not rerun upstream work", text.lower())
                self.assertIn("do not invoke all four", text.lower())

    def test_writing_translation_modes_allow_natural_reparagraphing(self) -> None:
        translation = reference_text("writing", "translation-guardrails.md")
        self.assertIn("Structure-aligned", translation)
        self.assertIn("Natural translation", translation)
        self.assertIn("Localization", translation)
        self.assertNotIn("不合并或拆分段落、列表项和表格单元", translation)

    def test_writing_declares_edit_levels_and_semantic_fidelity_checks(self) -> None:
        text = skill_text("writing")
        levels = reference_text("writing", "editing-levels.md")
        self.assertIn("references/editing-levels.md", text)
        for level in ("Proofread", "Polish", "Restructure", "Rewrite"):
            self.assertIn(level, levels)
        for protected in ("主体", "数字", "否定", "条件", "因果强度", "可能性", "来源归属"):
            self.assertIn(protected, levels)
        self.assertIn("scripts/check_semantic_fidelity.py", text)

    def test_decision_v2_contract_preserves_unknowns_and_tests_stability(self) -> None:
        text = skill_text("decision")
        rubric = reference_text("decision", "scoring-rubric.md")
        self.assertIn("eligible / ineligible / unresolved", text)
        self.assertIn('"schema_version": 2', rubric)
        self.assertIn("`null`", rubric)
        self.assertIn("不重新归一化", rubric)
        self.assertIn("首选是否翻转", rubric)

    def test_plan_optional_evidence_snapshot_keeps_legacy_plans_compatible(self) -> None:
        text = skill_text("plan-skill")
        reference = reference_text("plan-skill", "evidence-validity.md")
        self.assertIn("references/evidence-validity.md", text)
        self.assertIn("never created by default", text)
        self.assertIn("skip `init_plan.py`", text)
        self.assertIn("Old plans keep", reference)
        for status in ("valid_in_recorded_scope", "stale", "evidence_missing", "uncheckable"):
            self.assertIn(status, reference)

    def test_core_skill_behavior_suite_has_24_cases_and_holdouts(self) -> None:
        all_cases = []
        for skill in ("decision", "writing", "invest", "plan-skill"):
            path = ROOT / skill / "evals" / "behavior-cases.jsonl"
            cases = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
            with self.subTest(skill=skill):
                self.assertEqual(6, len(cases))
                self.assertEqual(2, sum(case["split"] == "acceptance" for case in cases))
                self.assertTrue(all(case["skill"] == skill for case in cases))
                self.assertTrue(all("expected_behavior" in case for case in cases))
                self.assertTrue(all("cost_limits" in case for case in cases))
                self.assertTrue(
                    all(
                        {
                            "max_reference_reads",
                            "max_followup_questions",
                            "max_external_mutations",
                            "max_operations",
                        }
                        <= set(case["cost_limits"])
                        for case in cases
                    )
                )
            all_cases.extend(cases)
        self.assertEqual(24, len(all_cases))
        self.assertEqual(24, len({case["id"] for case in all_cases}))

    def test_instruction_migration_suite_has_routing_negatives_and_holdouts(self) -> None:
        path = ROOT / "tests" / "instruction-migration-cases.jsonl"
        cases = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]

        self.assertEqual(8, len(cases))
        self.assertEqual(2, sum(case["split"] == "acceptance" for case in cases))
        self.assertTrue(all("expected_behavior" in case for case in cases))
        self.assertTrue(all("cost_limits" in case for case in cases))
        self.assertTrue(any(case.get("required_skills") for case in cases))
        self.assertTrue(any(case.get("forbidden_skills") for case in cases))

    def test_research_craft_routes_model_instruction_migrations_on_demand(self) -> None:
        skill = skill_text("research-craft")
        migration = reference_text("research-craft", "instruction-migration.md")

        self.assertIn("references/instruction-migration.md", skill)
        self.assertIn("Model-only baseline", migration)
        self.assertIn("Instruction candidate", migration)
        self.assertIn("required and forbidden skill activation", migration)
        self.assertIn("retirement trigger", migration)
        self.assertIn("before every task", migration)

    def test_decision_eval_cases_cover_observable_multi_turn_paths(self) -> None:
        path = ROOT / "decision" / "evals" / "cases.jsonl"
        cases = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
        behaviors = {case.get("expected_behavior") for case in cases}
        self.assertTrue(
            {"ask_then_stop", "decide_after_answer", "decide_without_question"}
            <= behaviors
        )
        ask_case = next(case for case in cases if case.get("expected_behavior") == "ask_then_stop")
        self.assertIn("最终决定", ask_case["must_not_include"])

    def test_invest_behavior_cases_gate_notion_tool_calls(self) -> None:
        path = ROOT / INVESTMENT_SKILL / "evals" / "cases.jsonl"
        cases = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
        by_behavior = {case["expected_behavior"]: case for case in cases}
        self.assertIn(
            "mcp__notion__",
            by_behavior["answer_without_notion_write"]["forbidden_tool_prefixes"],
        )
        self.assertIn(
            "mcp__notion__",
            by_behavior["report_delta_without_notion_write"]["forbidden_tool_prefixes"],
        )
        self.assertIn(
            "mcp__notion__",
            by_behavior["write_after_exact_target_resolution"]["required_tool_prefixes"],
        )

    def test_every_skill_has_openai_interface_metadata(self) -> None:
        for skill_dir in sorted(ROOT.iterdir()):
            if skill_dir.name.startswith(".") or not (skill_dir / "SKILL.md").is_file():
                continue
            with self.subTest(skill=skill_dir.name):
                self.assertTrue((skill_dir / "agents" / "openai.yaml").is_file())

    def test_no_skill_references_a_removed_skill(self) -> None:
        for skill_dir in sorted(ROOT.iterdir()):
            if skill_dir.name.startswith(".") or not (skill_dir / "SKILL.md").is_file():
                continue
            text = skill_text(skill_dir.name)
            for removed in REMOVED_SKILLS:
                with self.subTest(skill=skill_dir.name, removed=removed):
                    self.assertNotIn(removed, text)

    def test_skill_file_paths_resolve(self) -> None:
        for skill_dir in skill_dirs():
            text = skill_text(skill_dir.name)
            targets = set(PATH_IN_BACKTICKS.findall(text))
            targets.update(
                link
                for link in MARKDOWN_LINK.findall(text)
                if not link.startswith(("http://", "https://", "#"))
            )
            for target in sorted(targets):
                with self.subTest(skill=skill_dir.name, path=target):
                    self.assertTrue(
                        (skill_dir / target.split("#", 1)[0]).exists(),
                        f"{skill_dir.name}/SKILL.md points at missing {target}",
                    )

    def test_argument_audit_keeps_its_domain_adapters(self) -> None:
        self.assertIn("Argument integrity", skill_text("research-craft"))
        self.assertIn("Audit The Approval Argument", skill_text("code-review-craft"))
        self.assertIn("核心概念一致", skill_text("writing"))
        self.assertIn("是否分清事实、假设和推断", skill_text("decision"))

    def test_agent_harness_closes_verification_before_scaling_autonomy(self) -> None:
        skill = skill_text("research-craft")
        harness = (
            ROOT / "research-craft" / "references" / "harness-engineering.md"
        ).read_text(encoding="utf-8")

        self.assertIn("verification closure", skill)
        self.assertIn("Close the verifier loop before scaling", harness)
        self.assertIn("Human-verification debt", harness)
        self.assertIn("User surface / entry", harness)
        self.assertIn("failure evidence", harness)
        self.assertIn("Autonomy tier by task class", harness)

    def test_code_review_gates_auto_merge_by_task_class(self) -> None:
        skill = skill_text("code-review-craft")
        judgment = (
            ROOT / "code-review-craft" / "references" / "judgment-training.md"
        ).read_text(encoding="utf-8")

        self.assertIn("Calibrate review or merge autonomy", skill)
        self.assertIn("task-class-specific privilege", skill)
        self.assertIn("revision-linked evidence", judgment)
        self.assertIn("PR count", judgment)

    def test_decision_causal_attribution_keeps_its_counterfactual_gate(self) -> None:
        skill = skill_text("decision")
        causal = (
            ROOT / "decision" / "references" / "causal-analysis.md"
        ).read_text(encoding="utf-8")

        self.assertIn("references/causal-analysis.md", skill)
        self.assertIn("观察变化是否等于干预效果", skill)
        self.assertIn("恒等式用于定位变化，不自动证明原因", causal)
        self.assertIn("目标效应 = 8 月涨价后的结果", causal)
        self.assertIn("反事实来源、识别假设和范围", causal)
        self.assertIn("中介、交互与反馈", causal)

    def test_model_boundary_audit_has_domain_guardrails(self) -> None:
        self.assertIn("latent construct / model boundary", skill_text("research-craft"))

        invest = "\n".join(
            [
                skill_text(INVESTMENT_SKILL),
                reference_text(INVESTMENT_SKILL, "mode-b-bayesian-growth.md"),
                reference_text(INVESTMENT_SKILL, "mode-c-gf-dma.md"),
                reference_text(INVESTMENT_SKILL, "mode-d-serenity-alpha.md"),
                reference_text(INVESTMENT_SKILL, "mode-e-tam-adj-peg.md"),
            ]
        )
        self.assertIn("not independent confirmations", invest)
        self.assertIn("inverse problem, not a unique observable", invest)
        self.assertIn("GrowthMatch gate", invest)
        self.assertIn("aggregate score is disabled", invest.lower())
        # Mode D also covers cost/regulatory signals, not only latent demand.
        signal = reference_text(INVESTMENT_SKILL, "mode-d-serenity-alpha.md")
        self.assertIn("observed signal -> economic hypothesis -> rival explanations", signal)
        self.assertIn("Keep an unverified benefit as a research hypothesis", signal)
        self.assertIn("label the conclusion `model-sensitive`", invest)

    def test_result_analysis_daily_loop_keeps_live_and_research_gates_separate(
        self,
    ) -> None:
        skill = skill_text("result-analysis")
        daily = (
            ROOT
            / "result-analysis"
            / "references"
            / "daily-decision-loop.md"
        ).read_text(encoding="utf-8")

        self.assertIn("references/daily-decision-loop.md", skill)
        self.assertIn("PREAPPROVED_LIVE", daily)
        self.assertIn("REAL_OBSERVED", daily)
        self.assertIn("POSTHOC_CANDIDATE", daily)
        self.assertIn("KEEP_CURRENT", daily)
        self.assertIn("日报不能凭单日 SIM 盈利新增实盘品种", daily)
        self.assertIn("1 个同身份日：只能 `OBSERVE/MEASURE`", daily)
        self.assertIn("policy-conditional cohort", daily)
        self.assertIn("不自动落盘", daily)


if __name__ == "__main__":
    unittest.main()
