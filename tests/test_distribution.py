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
        self.assertIn("installed and activated", result.stdout)
        self.assertEqual((home / "config.toml").read_text(encoding="utf-8").count('model = "primary-model"'), 1)
        self.assertIn('model_reasoning_effort = "high"', (home / "config.toml").read_text(encoding="utf-8"))
        self.assertIn('service_tier = "default"', (home / "config.toml").read_text(encoding="utf-8"))
        self.assertIn("max_threads = 5", (home / "config.toml").read_text(encoding="utf-8"))
        self.assertIn("keep = \"unrelated setting\"", (home / "config.toml").read_text(encoding="utf-8"))
        self.assertIn(original_agents, (home / "AGENTS.md").read_text(encoding="utf-8"))
        managed_agents = (home / "AGENTS.md").read_text(encoding="utf-8")
        self.assertIn("Before the main chat decides to stop advancing a substantive user request", managed_agents)
        self.assertIn("regardless of response wording", managed_agents)
        self.assertIn("external research", managed_agents)
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

        research_guidance = {
            "luna_scout": (
                "map plausible mechanisms, approach families and assumptions",
                "map the entire relevant requested operating envelope",
                "Give each material domain real explanatory depth and discriminating evidence",
                "Surface missing domain depth for independent review and correction",
                "carry the actual comparison and measurement conventions into the decision",
            ),
            "inherited_scout": (
                "map plausible mechanisms, approach families and assumptions",
                "map the entire relevant requested operating envelope",
                "Give each material domain real explanatory depth and discriminating evidence",
                "Surface missing domain depth for independent review and correction",
                "carry the actual comparison and measurement conventions into the decision",
            ),
            "sol_expert": (
                "dedicated research-lead assignment",
                "request a sustained research lead through the coordinator without waiting for the user to ask",
                "Establish a coverage contract for the entire relevant operating envelope",
                "carry out meaningful bounded derivations, reference calculations or public-observation checks",
                "preserve the actual comparison, conventions and contrary measured outcomes",
            ),
            "inherited_reviewer": (
                "dedicated research-lead assignment",
                "request a sustained research lead through the coordinator without waiting for the user to ask",
                "Review coverage across the entire relevant operating envelope",
                "return independently found depth gaps for correction",
                "check that the actual comparison, measurement conventions and contrary measured outcomes are retained",
            ),
            "luna_worker": (
                "verify that a proposed method is not already implemented",
                "request scoped research support through the owner/coordinator without assuming the user must ask",
                "Consume assigned supporting evidence",
                "flag material operating-envelope, domain-depth or design-dependent check gaps to the owner",
                "carry through its measured comparison and conventions",
            ),
            "inherited_worker": (
                "verify that a proposed method is not already implemented",
                "request scoped research support through the owner/coordinator without assuming the user must ask",
                "Consume assigned supporting evidence",
                "flag material operating-envelope, domain-depth or design-dependent check gaps to the owner",
                "carry through its measured comparison and conventions",
            ),
            "astra_expert": (
                "review whether implementation and checks actually take up",
                "check whether substantial research was initiated when material scientific gaps could change the decisions ahead",
                "verify the coverage contract spans the entire relevant operating envelope",
                "independently identified depth gaps are sent for correction",
                "verify that results and limitations, actual comparisons, measurement conventions and contrary measured outcomes inform the decision",
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
