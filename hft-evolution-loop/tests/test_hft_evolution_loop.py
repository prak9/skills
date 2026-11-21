from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]
PY_ROOT = Path("/home/x/py")


class HftEvolutionLoopSkillTests(unittest.TestCase):
    def test_skill_docs_and_metadata_contract(self) -> None:
        skill_md = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        openai_yaml = (SKILL_ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8")

        self.assertIn("name: hft-evolution-loop", skill_md)
        self.assertIn("sim.py", skill_md)
        self.assertIn("conf/features_v2.lst", skill_md)
        self.assertIn("backtest.py diagnose", skill_md)
        self.assertIn("忠实原生", skill_md)
        self.assertIn("conf/workers.yaml", skill_md)
        self.assertIn("localhost", skill_md)
        self.assertLessEqual(len(skill_md.splitlines()), 100)
        self.assertIn("display_name:", openai_yaml)
        self.assertIn("default_prompt:", openai_yaml)

    @unittest.skipUnless(PY_ROOT.is_dir(), "requires /home/x/py repository")
    def test_bootstrap_loop_end_to_end(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            adir = Path(tmp) / "artifacts"
            adir.mkdir()
            (adir / "winress_20261120-20261121.csv").write_text(
                "s,t,account,mc_dwin,mc_dnwin,mc_dnwin_sd,mc_dnwin_min,mc_pot,mc_dret,mc_avgnwt,mc_tn,mc_hitr,ic5,qic,strong_n,strong_hits,fill_recipe\n"
                "pp,night,dce_t2,-500.0,-550.0,30.0,-600.0,-0.4,-0.02,-9.0,15,0.6,0.15,0.06,10,6,JOINT16\n",
                encoding="utf-8",
            )
            cdir = Path(tmp) / "campaign"
            proc = subprocess.run(
                [
                    sys.executable,
                    str(SKILL_ROOT / "scripts" / "bootstrap_loop.py"),
                    "--py-root",
                    str(PY_ROOT),
                    "--artifacts-dir",
                    str(adir),
                    "--campaign-dir",
                    str(cdir),
                    "--root-account",
                    "dce_t2",
                    "--symbols",
                    "pp",
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            out = json.loads(proc.stdout)
            self.assertTrue(out["initialized_now"])
            self.assertTrue(out["ready_for_next_node"])
            self.assertEqual(out["budget"]["remaining_nodes"], 10)
            self.assertEqual(out["actionable_slice_count"], 1)
            self.assertTrue((cdir / "tree.json").is_file())
            self.assertTrue((cdir / "tree.md").is_file())

            # Second run resumes existing tree and applies explicit user-specified max_nodes / max_depth
            proc2 = subprocess.run(
                [
                    sys.executable,
                    str(SKILL_ROOT / "scripts" / "bootstrap_loop.py"),
                    "--py-root",
                    str(PY_ROOT),
                    "--artifacts-dir",
                    str(adir),
                    "--campaign-dir",
                    str(cdir),
                    "--max-nodes",
                    "25",
                    "--max-depth",
                    "5",
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(proc2.returncode, 0, proc2.stderr)
            out2 = json.loads(proc2.stdout)
            self.assertFalse(out2["initialized_now"])
            self.assertEqual(out2["budget"]["max_nodes"], 25)
            self.assertEqual(out2["budget"]["max_depth"], 5)


if __name__ == "__main__":
    unittest.main()
