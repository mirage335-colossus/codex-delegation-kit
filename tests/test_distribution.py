"""End-to-end tests for the standalone installer bundle."""

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import tomllib
import unittest


BUNDLE_ROOT = Path(__file__).resolve().parents[1]
BUNDLE_FILES = (
    "README.md", "policy.md", "supervisor.py", "install.py", "uninstall.py",
    "agents/luna_scout.toml", "agents/luna_worker.toml", "agents/sol_expert.toml",
    "agents/inherited_scout.toml", "agents/inherited_worker.toml",
    "agents/inherited_reviewer.toml",
    "controller.py", "controller_store.py", "execution.py", "agent_backend.py",
    "scheduling.py", "ORCHESTRATION.md", "engineering.py",
    "agents/inherited_swarm.toml", "agents/luna_swarm.toml",
    "agents/astra_expert.toml", "agents/astra_initial.toml", "CLOUD.md",
    "agents/sol_researcher.toml",
    "skills/delegation-kit/SKILL.md", "skills/delegation-kit/agents/openai.yaml",
)


class DistributionTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)

    def copy_bundle(self, destination):
        destination.mkdir(parents=True)
        for name in BUNDLE_FILES:
            target = destination / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(BUNDLE_ROOT / name, target)

    def run_installer(self, source, home, *options, env=None):
        return subprocess.run(
            [sys.executable, "-B", str(source / "install.py"), "--home", str(home),
             "--source", str(source), *options],
            check=False, text=True, capture_output=True, env=env,
        )

    def test_install_into_spaced_path_preserves_user_configuration(self):
        source = self.root / "bundle source"
        home = self.root / "Codex home with spaces"
        self.copy_bundle(source)
        home.mkdir()
        config = (
            'model = "primary-model"\n'
            'model_reasoning_effort = "high"\n'
            'service_tier = "default"\n'
            '\n[agents]\nmax_threads = 5\n'
            '\n[other]\nkeep = "unrelated setting"\n'
        )
        (home / "config.toml").write_text(config, encoding="utf-8")
        original_agents = "# My global instructions\nKeep this text.\n"
        (home / "AGENTS.md").write_text(original_agents, encoding="utf-8")
        (home / "notes.txt").write_text("unrelated global content\n", encoding="utf-8")

        result = self.run_installer(source, home, "--apply")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("explicit skill invocation required", result.stdout)
        self.assertEqual((home / "config.toml").read_text(encoding="utf-8").count('model = "primary-model"'), 1)
        self.assertIn('model_reasoning_effort = "high"', (home / "config.toml").read_text(encoding="utf-8"))
        self.assertIn('service_tier = "default"', (home / "config.toml").read_text(encoding="utf-8"))
        self.assertIn("max_threads = 5", (home / "config.toml").read_text(encoding="utf-8"))
        self.assertIn("keep = \"unrelated setting\"", (home / "config.toml").read_text(encoding="utf-8"))
        self.assertIn(original_agents, (home / "AGENTS.md").read_text(encoding="utf-8"))
        self.assertEqual((home / "AGENTS.md").read_text(), original_agents)
        self.assertIn("allow_implicit_invocation: false",
                      (home / "skills/delegation-kit/agents/openai.yaml").read_text())
        self.assertEqual((home / "skills/delegation-kit/SKILL.md").read_bytes(),
                         (source / "skills/delegation-kit/SKILL.md").read_bytes())
        self.assertEqual((home / "notes.txt").read_text(encoding="utf-8"), "unrelated global content\n")
        self.assertTrue((home / "config.toml").read_text(encoding="utf-8").startswith(config))
        self.assertTrue((home / "delegation-kit" / "policy.md").is_file())
        self.assertTrue((home / "delegation-kit" / "CLOUD.md").is_file())
        self.assertIn("](CLOUD.md)", (home / "delegation-kit" / "README.md").read_text(encoding="utf-8"))
        manifest = json.loads((home / "delegation-kit/.installation/manifest.json").read_text(encoding="utf-8"))
        self.assertTrue(manifest["active"])
        self.assertEqual(set(manifest["bundle_digests"]), set(BUNDLE_FILES))
        self.assertEqual(manifest["source_directory"], str(source.absolute()))
        for name in BUNDLE_FILES:
            self.assertEqual((home / "delegation-kit" / name).read_bytes(),
                             (source / name).read_bytes())
        self.assertFalse((home / "delegation-kit/state").exists())
        configuration = tomllib.loads((home / "config.toml").read_text(encoding="utf-8"))
        expected_roles = {
            "luna_scout": ("gpt-6-luna", "high"),
            "luna_worker": ("gpt-6-luna", "high"),
            "sol_expert": ("gpt-6.1-sol", "ultra"),
            "inherited_scout": None,
            "inherited_worker": None,
            "inherited_reviewer": None,
            "inherited_swarm": None,
            "luna_swarm": ("gpt-6-luna", "medium"),
            "astra_expert": ("gpt-6-astra", "ultra"),
            "astra_initial": ("gpt-6-astra", "ultra"),
            "sol_researcher": ("gpt-6.1-sol", "ultra"),
        }
        self.assertEqual(set(configuration["agents"]), {"max_threads", *expected_roles})
        for role, settings in expected_roles.items():
            with self.subTest(role=role):
                path = home / "delegation-kit/agents" / (role + ".toml")
                self.assertEqual(configuration["agents"][role]["config_file"], str(path))
                role_config = tomllib.loads(path.read_text(encoding="utf-8"))
                self.assertTrue(role_config["developer_instructions"].strip())
                self.assertNotIn("service_tier", role_config)
                if settings is None:
                    self.assertNotIn("model", role_config)
                    self.assertNotIn("model_reasoning_effort", role_config)
                else:
                    self.assertEqual((role_config["model"], role_config["model_reasoning_effort"]), settings)

        # Delivery checks do not establish research behavior or scientific adequacy.
        research_guidance = {
            "sol_researcher": (
                "native scientific author, research lead or independent",
                "architecture approval or the main chat's completion decision",
                "This native role adds no controller responsibility or model route",
                "Start from a standalone scientific assignment",
                "Keep the complete development request, operating",
                "identity proves absent inherited context or isolation",
                "Do not spawn helpers, self-schedule",
                "Do not accept your own authored",
                "Retain scientific authorship for material subjects you do not delegate",
                "Inspect decisive primary-source methods, results and limitations",
                "Treat _ref/ and _appraisal/ as user-curated and read-only",
                "through bounded primary-literature discovery before receiving authors' maps or",
                "Return detailed reusable findings and a concise status with actual checks",
            ),
            "luna_scout": (
                "map plausible mechanisms, approach families and assumptions",
                "map the entire relevant requested operating envelope",
                "Give each material domain real explanatory depth and discriminating evidence",
                "Surface missing domain depth for independent review and correction",
                "carry the actual comparison and measurement conventions into the decision",
                "report meaningful gaps, their decision impact and the next feasible check to the owner",
                "synthesis and engineering uptake without expanding the team",
                "Readiness of your bounded step does not establish scientific coverage across the full requested conditions",
                "flag explanatory gaps, unresolved question groups and unfinished feasible comparisons to the owner",
                "any contraction of the original research brief at audit or specialist boundaries",
                "even when later target calibration remains",
            ),
            "inherited_scout": (
                "map plausible mechanisms, approach families and assumptions",
                "map the entire relevant requested operating envelope",
                "Give each material domain real explanatory depth and discriminating evidence",
                "Surface missing domain depth for independent review and correction",
                "carry the actual comparison and measurement conventions into the decision",
                "report meaningful gaps, their decision impact and the next feasible check to the owner",
                "synthesis and engineering uptake without expanding the team",
                "Readiness of your bounded step does not establish scientific coverage across the full requested conditions",
                "flag explanatory gaps, unresolved question groups and unfinished feasible comparisons to the owner",
                "any contraction of the original research brief at audit or specialist boundaries",
                "even when later target calibration remains",
            ),
            "sol_expert": (
                "dedicated research-lead assignment",
                "request a sustained research lead through the coordinator without waiting for the user to ask",
                "Establish a coverage contract for the entire relevant operating envelope",
                "carry out meaningful bounded derivations, reference calculations or public-observation checks",
                "preserve the actual comparison, conventions and contrary measured outcomes",
                "The assignment selects scientific subject investigation, research leadership,",
                "without waiting for the user or main chat to supply missing science",
                "routes unresolved relationships or corrections to their authors",
                "an intermediate report while material feasible research remains",
                "commission focused subject investigations through the coordinator, each the author's sole substantive research assignment in a separate working context",
                "Only after that sourced scope is preserved does the critic receive the scientific account or both preserved accounts when paired",
                "Before returning its initial scope, the critic performs bounded literature discovery across the full brief using permitted evidence routes",
                "Factual context excludes engineering recommendations, including suggestions appended to code observations",
                "Follow through on useful corrections even when the first engineering stage can begin",
                "report the science as partial with the exact next action",
                "When a broad consequential task needs substantial new scientific grounding",
                "the engineering or task owner autonomously requests one pair of independent full-problem research inquiries for the overall scientific problem",
                "An assigned inquiry completes that scope and requests bounded discovery or verification help through the coordinator; it does not commission another pair for the same problem",
                "preserve both substantive first accounts before cross-inquiry disclosure",
                "retain each material question or justified equivalent group from the inquiries and critic, including questions without a supported conclusion",
                "Map each conclusion's conditions and performed evidence to the distinctions it actually resolves",
                "Withhold engineering-plan artifacts and prior tranche-approval messages through scientific disposition",
                "Complete internally requested feasible science and changed-evidence review before handoff",
                "Use a research-only brief preserving the original problem, requested outcome, full operating envelope and constraints",
                "Deliver a reusable scientific account that can inform multiple approaches; the engineering owner separately owns the implementation plan",
                "retain end-to-end scientific responsibility across code audits and specialist partitions",
                "including material links among mechanisms, observations, inference, validation and computational feasibility",
                "neither a safe current design nor one successful example per branch establishes broad grounding",
                "Review explanatory adequacy and the actual scope of successful checks",
                "Distinguish these present evidence obligations from product qualification",
            ),
            "inherited_reviewer": (
                "dedicated research-lead assignment",
                "request a sustained research lead through the coordinator without waiting for the user to ask",
                "Review coverage across the entire relevant operating envelope",
                "return independently found depth gaps for correction",
                "check that the actual comparison, measurement conventions and contrary measured outcomes are retained",
                "The assignment selects scientific subject investigation, research leadership,",
                "without waiting for the user or main chat to supply missing science",
                "Return decision-relevant gaps with their impact and smallest feasible discriminator",
                "an intermediate report while material feasible research remains",
                "commission focused subject investigations through the coordinator, each the author's sole substantive research assignment in a separate working context",
                "Only after that sourced scope is preserved does the critic receive the scientific account or both preserved accounts when paired",
                "Before returning its initial scope, the critic performs bounded literature discovery across the full brief using permitted evidence routes",
                "Factual context excludes engineering recommendations, including suggestions appended to code observations",
                "Follow through on useful corrections even when the first engineering stage can begin",
                "report the science as partial with the exact next action",
                "When a broad consequential task needs substantial new scientific grounding",
                "the engineering or task owner autonomously requests one pair of independent full-problem research inquiries for the overall scientific problem",
                "An assigned inquiry completes that scope and requests bounded discovery or verification help through the coordinator; it does not commission another pair for the same problem",
                "preserve both substantive first accounts before cross-inquiry disclosure",
                "retain each material question or justified equivalent group from the inquiries and critic, including questions without a supported conclusion",
                "Map each conclusion's conditions and performed evidence to the distinctions it actually resolves",
                "Withhold engineering-plan artifacts and prior tranche-approval messages through scientific disposition",
                "Complete internally requested feasible science and changed-evidence review before handoff",
                "Use a research-only brief preserving the original problem, requested outcome, full operating envelope and constraints",
                "Deliver a reusable scientific account that can inform multiple approaches; the engineering owner separately owns the implementation plan",
                "retain end-to-end scientific responsibility across code audits and specialist partitions",
                "including material links among mechanisms, observations, inference, validation and computational feasibility",
                "neither a safe current design nor one successful example per branch establishes broad grounding",
                "Review explanatory adequacy and the actual scope of successful checks",
                "Distinguish these present evidence obligations from product qualification",
            ),
            "luna_worker": (
                "verify that a proposed method is not already implemented",
                "request scoped research support through the owner/coordinator without assuming the user must ask",
                "Consume assigned supporting evidence",
                "flag material operating-envelope, domain-depth or design-dependent check gaps to the owner",
                "carry through its measured comparison and conventions",
                "Carry accepted scientific findings and review corrections into the owned implementation and checks",
                "Report meaningful scientific gaps with their decision impact and a feasible discriminator to the owner",
                "Separate readiness for the next implementation step from scientific coverage across the full requested conditions",
                "Flag explanatory gaps, unresolved question groups and unfinished feasible comparisons to the owner",
                "any contraction of the original research brief at audit or specialist boundaries",
            ),
            "inherited_worker": (
                "verify that a proposed method is not already implemented",
                "request scoped research support through the owner/coordinator without assuming the user must ask",
                "Consume assigned supporting evidence",
                "flag material operating-envelope, domain-depth or design-dependent check gaps to the owner",
                "carry through its measured comparison and conventions",
                "Carry accepted scientific findings and review corrections into the owned implementation and checks",
                "Report meaningful scientific gaps with their decision impact and a feasible discriminator to the owner",
                "Separate readiness for the next implementation step from scientific coverage across the full requested conditions",
                "Flag explanatory gaps, unresolved question groups and unfinished feasible comparisons to the owner",
                "any contraction of the original research brief at audit or specialist boundaries",
            ),
            "astra_expert": (
                "review whether implementation and checks actually take up",
                "check whether substantial research was initiated when material scientific gaps could change the decisions ahead",
                "verify the coverage contract spans the entire relevant operating envelope",
                "independently identified depth gaps are sent for correction",
                "verify that results and limitations, actual comparisons, measurement conventions and contrary measured outcomes inform the decision",
                "internally requested independent criticism, correction and engineering uptake",
                "Before returning your initial scope, perform bounded literature discovery across the full brief using permitted evidence routes",
                "Only after that sourced scope is preserved, receive the scientific account or both preserved accounts when paired",
                "Factual context excludes engineering recommendations, including suggestions appended to code observations",
                "Retain each material question or justified equivalent group from the inquiries and critic, including questions without a supported conclusion",
                "Map each conclusion's conditions and performed evidence to the distinctions it actually resolves",
                "Treat a handoff as intermediate while material feasible research remains within scope",
                "Assess readiness for a bounded next engineering step separately from scientific coverage across the full requested conditions",
                "check the weakest primary-source support, decisive quantitative comparisons and contrary evidence",
                "require the science to be reported as partial with the exact next action",
                "two independent full-problem inquiries shared the original problem, constraints and source facts",
                "Check the initial-account checkpoint and follow-through reserve within one shared allowance",
                "Withhold engineering-plan artifacts and prior tranche-approval messages through scientific disposition",
                "disclose that exposure and request suitable independent review through the coordinator where feasible; do not claim blinding",
                "check that the lead's research-only brief preserves the original problem, requested outcome, full operating envelope and constraints",
                "end-to-end scientific responsibility survives code audits and specialist partitions",
                "Assess explanatory adequacy and the actual scope of successful checks",
                "feasible representative calculations or source-based discriminators were executed within authority even when later target calibration remains",
            ),
        }
        for role, markers in research_guidance.items():
            with self.subTest(scientific_research_role=role):
                source_role = tomllib.loads((source / "agents" / (role + ".toml")).read_text(encoding="utf-8"))
                installed_role = tomllib.loads((home / "delegation-kit/agents" / (role + ".toml")).read_text(encoding="utf-8"))
                for marker in markers:
                    self.assertIn(marker, source_role["developer_instructions"])
                    self.assertIn(marker, installed_role["developer_instructions"])
                self.assertEqual(source_role, installed_role)

    def test_relocated_source_update_idempotent_reinstall_and_disable_retain_state(self):
        original_source = self.root / "original source"
        relocated_source = self.root / "relocated kit source"
        home = self.root / "Codex home with spaces"
        self.copy_bundle(original_source)
        home.mkdir()
        (home / "config.toml").write_text('model = "keep-me"\n', encoding="utf-8")
        installed = self.run_installer(original_source, home, "--apply")
        self.assertEqual(installed.returncode, 0, installed.stderr)

        # Retained supervisor evidence is user state and must survive upgrade, reinstall, and disable.
        evidence = home / "delegation-kit/state/assignment/original-result.json"
        evidence.parent.mkdir(parents=True)
        evidence.write_text('{"status":"completed","evidence":["logs/result.txt"]}\n', encoding="utf-8")
        before_update_manifest = home / "delegation-kit/.installation/manifest.json"
        before_update = json.loads(before_update_manifest.read_text(encoding="utf-8"))
        self.assertEqual(before_update["source_directory"], str(original_source.absolute()))
        (original_source / "README.md").write_text("# Relocated source update\n", encoding="utf-8")
        shutil.copytree(original_source, relocated_source)
        shutil.rmtree(original_source)

        upgraded = self.run_installer(relocated_source, home, "--apply")
        self.assertEqual(upgraded.returncode, 0, upgraded.stderr)
        self.assertEqual((home / "delegation-kit/README.md").read_text(encoding="utf-8"), "# Relocated source update\n")
        self.assertEqual(evidence.read_text(encoding="utf-8"), '{"status":"completed","evidence":["logs/result.txt"]}\n')
        upgraded_manifest = json.loads(before_update_manifest.read_text(encoding="utf-8"))
        self.assertTrue(upgraded_manifest["active"])
        self.assertNotEqual(upgraded_manifest["bundle_digests"]["README.md"], before_update["bundle_digests"]["README.md"])
        self.assertEqual(upgraded_manifest["source_directory"], str(relocated_source.absolute()))

        snapshots = {
            evidence: evidence.read_bytes(),
            home / "delegation-kit/README.md": (home / "delegation-kit/README.md").read_bytes(),
        }
        upgraded_manifest_bytes = before_update_manifest.read_bytes()
        reinstall = self.run_installer(relocated_source, home, "--apply")
        self.assertEqual(reinstall.returncode, 0, reinstall.stderr)
        for path, contents in snapshots.items():
            self.assertEqual(path.read_bytes(), contents)
        self.assertEqual(before_update_manifest.read_bytes(), upgraded_manifest_bytes)

        disabled = self.run_installer(relocated_source, home, "--uninstall", "--apply")
        self.assertEqual(disabled.returncode, 0, disabled.stderr)
        self.assertIn("Kit disabled", disabled.stdout)
        self.assertEqual(evidence.read_text(encoding="utf-8"), '{"status":"completed","evidence":["logs/result.txt"]}\n')
        self.assertEqual((home / "delegation-kit/README.md").read_text(encoding="utf-8"), "# Relocated source update\n")
        inactive = json.loads(before_update_manifest.read_text(encoding="utf-8"))
        self.assertFalse(inactive["active"])
        self.assertEqual(inactive["source_directory"], str(relocated_source.absolute()))
        self.assertEqual((home / "config.toml").read_text(encoding="utf-8"), 'model = "keep-me"\n')

    @unittest.skipIf(os.name == "nt", "The controller requires POSIX fcntl; run in WSL")
    def test_installed_controller_help_is_self_contained_and_does_not_start_a_run(self):
        source = self.root / "bundle"
        home = self.root / "Codex home"
        self.copy_bundle(source)
        installed = self.run_installer(source, home, "--apply")
        self.assertEqual(installed.returncode, 0, installed.stderr)
        target = home / "delegation-kit"
        # Running away from the checkout catches imports omitted from FILES.
        result = subprocess.run(
            [sys.executable, "-B", str(target / "controller.py"), "--help"],
            cwd=self.root, check=False, text=True, capture_output=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("usage:", result.stdout)
        imported = subprocess.run(
            [sys.executable, "-B", "-c", "import engineering"],
            cwd=target, check=False, text=True, capture_output=True,
        )
        self.assertEqual(imported.returncode, 0, imported.stderr)
        self.assertFalse((target / "state").exists())
        self.assertFalse(list(self.root.rglob("state.sqlite3")))

    def test_default_codex_home_uses_child_environment_and_dry_run_is_read_only(self):
        source = self.root / "bundle"
        home = self.root / "CODEX_HOME child path"
        self.copy_bundle(source)
        env = os.environ.copy()
        env["CODEX_HOME"] = str(home)
        result = subprocess.run(
            [sys.executable, "-B", str(source / "install.py"), "--source", str(source)],
            check=False, text=True, capture_output=True, env=env,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Dry run only", result.stdout)
        self.assertFalse(home.exists())


if __name__ == "__main__":
    unittest.main()
