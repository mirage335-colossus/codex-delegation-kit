"""CLI uninstall discovery proofs using isolated projects and Codex homes."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

import install as kit


class UninstallDiscoveryTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.source = Path(kit.__file__).parent
        self.global_home = self.root / "isolated global home"
        self.environment = dict(os.environ, CODEX_HOME=str(self.global_home), PYTHONUTF8="1")
        self.project = self.root / "repo"
        self.project.mkdir()
        (self.project / ".git").mkdir()
        (self.project / "AGENTS.md").write_bytes(b"Keep my project rules.\n")
        (self.project / ".codex").mkdir()
        (self.project / ".codex/config.toml").write_bytes(b'model = "keep-my-model"\n')

    def install(self, root=None, scope="global", repositories=None):
        home = self.global_home if scope == "global" else root / ".codex"
        kit.apply(kit.plan(home, self.source, scope=scope, root=root, repositories=repositories))
        return home

    def manifest(self, home):
        return json.loads((home / "delegation-kit/.installation/manifest.json").read_text())

    def snapshot(self):
        return {str(p.relative_to(self.root)): p.read_bytes()
                for p in self.root.rglob("*") if p.is_file()}

    def uninstall(self, cwd, *options, script=None):
        return subprocess.run([sys.executable, "-B", str(script or self.source / "uninstall.py"), *options],
                              cwd=cwd, env=self.environment, capture_output=True, text=True, encoding="utf-8")

    def assert_success(self, result):
        self.assertEqual(result.returncode, 0, result.stderr)

    def tree(self):
        root = self.root / "podcast_feed"
        for name in ("PodBoss", "group/Processor"):
            (root / name / ".git").mkdir(parents=True)
        self.assertFalse((root / ".git").exists())
        home = self.install(root, "tree", ["PodBoss", "group/Processor"])
        return root, home

    def test_source_uninstaller_detects_repo_from_nested_cwd_without_touching_global(self):
        self.install()
        home = self.install(self.project, "project")
        global_before = (self.global_home / "delegation-kit/.installation/manifest.json").read_bytes()
        nested = self.project / "src/package"
        nested.mkdir(parents=True)
        before = self.snapshot()
        preview = self.uninstall(nested)
        self.assert_success(preview)
        self.assertIn("Discovered project installation", preview.stdout)
        self.assertEqual(self.snapshot(), before, "Preview must not write")
        result = self.uninstall(nested, "--apply")
        self.assert_success(result)
        self.assertFalse(self.manifest(home)["active"])
        self.assertEqual((self.global_home / "delegation-kit/.installation/manifest.json").read_bytes(), global_before)
        self.assertEqual((self.project / "AGENTS.md").read_bytes(), b"Keep my project rules.\n")
        self.assertEqual((home / "config.toml").read_bytes(), b'model = "keep-my-model"\n')
        self.assertFalse((self.project / ".agents/skills/delegation-kit/SKILL.md").exists())
        self.assertTrue((home / "delegation-kit/controller.py").exists())
        disabled = self.snapshot()
        self.assert_success(self.uninstall(nested, "--apply"))
        self.assertEqual(self.snapshot(), disabled, "Repeat uninstall must not fall back to global")

    def test_source_uninstaller_discovers_tree_and_all_recorded_children(self):
        self.install()
        root, home = self.tree()
        nested = root / "group/Processor/src"
        nested.mkdir()
        self.assert_success(self.uninstall(nested, "--apply"))
        self.assertFalse(self.manifest(home)["active"])
        self.assertTrue(self.manifest(self.global_home)["active"])
        for member in (root, root / "PodBoss", root / "group/Processor"):
            self.assertFalse((member / ".agents/skills/delegation-kit/SKILL.md").exists())
            self.assertFalse((member / ".codex/config.toml").exists())
        disabled = self.snapshot()
        # The child pointer was removed; crossing its Git root to rediscover
        # the shared disabled manifest would violate the repository boundary.
        repeat = self.uninstall(nested, "--apply")
        self.assertNotEqual(repeat.returncode, 0)
        self.assertIn("repository boundary", repeat.stderr)
        self.assertEqual(self.snapshot(), disabled)
        self.assert_success(self.uninstall(nested, "--apply", script=home / "delegation-kit/uninstall.py"))
        self.assertEqual(self.snapshot(), disabled)

    def test_unlisted_repo_cannot_select_parent_tree_or_global_installation(self):
        self.install()
        root, home = self.tree()
        for marker_type in ("directory", "file"):
            with self.subTest(marker_type=marker_type):
                repo = root / f"Unlisted-{marker_type}"
                cwd = repo / "src/package"
                cwd.mkdir(parents=True)
                marker = repo / ".git"
                if marker_type == "directory":
                    marker.mkdir()
                else:
                    marker.write_bytes(b"gitdir: ../external-git-directory\n")
                before = self.snapshot()
                result = self.uninstall(cwd, "--apply")
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("repository boundary", result.stderr)
                self.assertEqual(self.snapshot(), before)
                self.assertTrue(self.manifest(home)["active"])
                self.assertTrue(self.manifest(self.global_home)["active"])

    def test_nested_independent_repo_cannot_select_registered_parent_installation(self):
        self.install()
        root, home = self.tree()
        repo = root / "PodBoss/vendor/independent"
        cwd = repo / "src"
        cwd.mkdir(parents=True)
        (repo / ".git").mkdir()
        before = self.snapshot()
        result = self.uninstall(cwd, "--apply")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("repository boundary", result.stderr)
        self.assertEqual(self.snapshot(), before)
        self.assertTrue(self.manifest(home)["active"])
        self.assertTrue(self.manifest(self.global_home)["active"])

    def test_nested_repo_with_its_own_install_selects_only_that_install(self):
        self.install()
        root, tree_home = self.tree()
        repo = root / "PodBoss/vendor/independent"
        (repo / ".git").mkdir(parents=True)
        (repo / "src").mkdir()
        home = self.install(repo, "project")
        result = self.uninstall(repo / "src", "--apply")
        self.assert_success(result)
        self.assertIn("Discovered project installation", result.stdout)
        self.assertFalse(self.manifest(home)["active"])
        self.assertTrue(self.manifest(tree_home)["active"])
        self.assertTrue(self.manifest(self.global_home)["active"])

    def test_repo_without_local_install_does_not_fall_back_to_global(self):
        self.install()
        before = self.snapshot()
        result = self.uninstall(self.project, "--apply")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("repository boundary", result.stderr)
        self.assertEqual(self.snapshot(), before)

    def test_non_git_collection_root_discovers_its_tree_installation(self):
        self.install()
        root, home = self.tree()
        preview_before = self.snapshot()
        preview = self.uninstall(root)
        self.assert_success(preview)
        self.assertIn("Discovered tree installation", preview.stdout)
        self.assertEqual(self.snapshot(), preview_before)
        self.assert_success(self.uninstall(root, "--apply"))
        self.assertFalse(self.manifest(home)["active"])
        self.assertTrue(self.manifest(self.global_home)["active"])
        disabled = self.snapshot()
        self.assert_success(self.uninstall(root, "--apply"))
        self.assertEqual(self.snapshot(), disabled)

    def test_registered_tree_member_with_git_file_discovers_shared_installation(self):
        self.install()
        root, home = self.tree()
        member = root / "group/Processor"
        (member / ".git").rmdir()
        (member / ".git").write_bytes(b"gitdir: ../../worktrees/Processor\n")
        result = self.uninstall(member, "--apply")
        self.assert_success(result)
        self.assertIn("Discovered tree installation", result.stdout)
        self.assertFalse(self.manifest(home)["active"])
        self.assertTrue(self.manifest(self.global_home)["active"])

    def test_installed_uninstaller_identifies_its_own_scope_from_another_cwd(self):
        self.install()
        project_home = self.install(self.project, "project")
        _, tree_home = self.tree()
        for home, scope in ((self.global_home, "global"), (project_home, "project"), (tree_home, "tree")):
            with self.subTest(scope=scope):
                result = self.uninstall(self.project, "--apply", script=home / "delegation-kit/uninstall.py")
                self.assert_success(result)
                self.assertIn(f"Discovered {scope} installation", result.stdout)
                self.assertFalse(self.manifest(home)["active"])
                after = self.snapshot()
                self.assert_success(self.uninstall(self.project, "--apply", script=home / "delegation-kit/uninstall.py"))
                self.assertEqual(self.snapshot(), after)

    def test_source_uninstaller_uses_default_global_home_outside_projects(self):
        self.install()
        self.assert_success(self.uninstall(self.root, "--apply"))
        self.assertFalse(self.manifest(self.global_home)["active"])

    def test_manifest_without_explicit_scope_defaults_to_global(self):
        self.install()
        path = self.global_home / "delegation-kit/.installation/manifest.json"
        manifest = self.manifest(self.global_home)
        del manifest["scope"]
        del manifest["members"]
        path.write_text(json.dumps(manifest), encoding="utf-8")
        self.assert_success(self.uninstall(self.root, "--apply"))
        self.assertFalse(self.manifest(self.global_home)["active"])

    def test_codex_home_override_wins_over_unrelated_ancestor_global_home(self):
        self.install()
        outer = self.root / "another user home"
        ancestor_home = outer / ".codex"
        kit.apply(kit.plan(ancestor_home, self.source))
        cwd = outer / "work/uninstalled repo"
        cwd.mkdir(parents=True)
        self.assert_success(self.uninstall(cwd, "--apply"))
        self.assertFalse(self.manifest(self.global_home)["active"])
        self.assertTrue(self.manifest(ancestor_home)["active"])

    def test_invalid_local_pointer_refuses_without_global_fallback(self):
        self.install()
        self.install(self.project, "project")
        pointer = self.project / ".agents/skills/delegation-kit/runtime.json"
        pointer.write_bytes(b"not valid JSON")
        before = self.snapshot()
        result = self.uninstall(self.project, "--apply")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Refused:", result.stderr)
        self.assertEqual(self.snapshot(), before)

    def test_pointer_to_another_installation_is_refused(self):
        self.install()
        self.install(self.project, "project")
        other = self.root / "other repo"
        other.mkdir()
        other_home = self.install(other, "project")
        pointer = self.project / ".agents/skills/delegation-kit/runtime.json"
        pointer.write_text(json.dumps({"runtime_directory": str(other_home / "delegation-kit")}), encoding="utf-8")
        before = self.snapshot()
        result = self.uninstall(self.project, "--apply")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.snapshot(), before)

    def test_missing_local_pointer_is_not_mistaken_for_global_install(self):
        self.install()
        self.install(self.project, "project")
        pointer = self.project / ".agents/skills/delegation-kit/runtime.json"
        pointer.unlink()
        before = self.snapshot()
        result = self.uninstall(self.project, "--apply")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.snapshot(), before)

    def test_explicit_target_remains_available(self):
        self.install()
        home = self.install(self.project, "project")
        self.assert_success(self.uninstall(self.project, "--home", str(self.global_home), "--apply"))
        self.assertFalse(self.manifest(self.global_home)["active"])
        self.assertTrue(self.manifest(home)["active"])

    def test_damaged_installed_manifest_does_not_fall_back_to_another_scope(self):
        self.install()
        home = self.install(self.project, "project")
        metadata = home / "delegation-kit/.installation/manifest.json"
        metadata.unlink()
        before = self.snapshot()
        result = self.uninstall(self.root, "--apply", script=home / "delegation-kit/uninstall.py")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.snapshot(), before)

    def test_missing_installed_metadata_directory_does_not_select_another_scope(self):
        self.install()
        home = self.install(self.project, "project")
        metadata = home / "delegation-kit/.installation"
        self.assertTrue(metadata.is_relative_to(self.root))
        shutil.rmtree(metadata)
        before = self.snapshot()
        result = self.uninstall(self.root, "--apply", script=home / "delegation-kit/uninstall.py")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.snapshot(), before)


if __name__ == "__main__":
    unittest.main()
