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
        self.assertEqual((home / "notes.txt").read_text(encoding="utf-8"), "unrelated global content\n")
        self.assertTrue((home / "config.toml").read_text(encoding="utf-8").startswith(config))
        self.assertTrue((home / "delegation-kit" / "policy.md").is_file())
        manifest = json.loads((home / "delegation-kit/.installation/manifest.json").read_text(encoding="utf-8"))
        self.assertTrue(manifest["active"])
        self.assertEqual(set(manifest["bundle_digests"]), set(BUNDLE_FILES))
        configuration = tomllib.loads((home / "config.toml").read_text(encoding="utf-8"))
        expected_roles = {
            "luna_scout": ("gpt-6-luna", "high"),
            "luna_worker": ("gpt-6-luna", "high"),
            "sol_expert": ("gpt-6.1-sol", "ultra"),
            "inherited_scout": None,
            "inherited_worker": None,
            "inherited_reviewer": None,
        }
        self.assertEqual(set(configuration["agents"]), {"max_threads", *expected_roles})
        for role, settings in expected_roles.items():
            with self.subTest(role=role):
                path = home / "delegation-kit/agents" / (role + ".toml")
                self.assertEqual(configuration["agents"][role]["config_file"], str(path))
                role_config = tomllib.loads(path.read_text(encoding="utf-8"))
                self.assertTrue(role_config["developer_instructions"].strip())
                if settings is None:
                    self.assertNotIn("model", role_config)
                    self.assertNotIn("model_reasoning_effort", role_config)
                else:
                    self.assertEqual((role_config["model"], role_config["model_reasoning_effort"]), settings)

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
        self.assertEqual((home / "config.toml").read_text(encoding="utf-8"), 'model = "keep-me"\n')

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
