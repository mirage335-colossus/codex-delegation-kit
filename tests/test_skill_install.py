"""Explicit-only discovery, legacy migration, and scoped installation outcomes."""
from contextlib import redirect_stdout
import io
import json
import os
from pathlib import Path
import tempfile
import unittest

import install as kit


class SkillInstallationTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.source = Path(kit.__file__).parent
        self.home = self.root / "home"

    def apply(self, **kwargs):
        kit.apply(kit.plan(self.home, self.source, **kwargs))

    def skill(self, member=None):
        return ((member / ".agents/skills") if member else self.home / "skills") / "delegation-kit"

    def tree(self):
        root = self.root / "collection"
        for name in ("podboss", "group/podprocessor"):
            repo = root / name
            (repo / ".git").mkdir(parents=True)
            (repo / "AGENTS.md").write_text("local project rules\n")
            (repo / ".codex").mkdir()
            (repo / ".codex/config.toml").write_text('model = "keep-local"\n')
        (root / "AGENTS.md").write_text("collection rules\n")
        self.home = root / ".codex"
        return root

    def test_global_roundtrip_never_changes_user_instructions(self):
        self.home.mkdir()
        agents = self.home / "AGENTS.md"
        agents.write_bytes(b"user text without final newline")
        override = self.home / "AGENTS.override.md"
        override.write_bytes(b"user override\n")
        preview = kit.plan(self.home, self.source)
        self.assertFalse(any(c.path in (agents, override) for c in preview))
        self.assertFalse(self.skill().exists())
        kit.apply(preview)
        self.assertEqual(agents.read_bytes(), b"user text without final newline")
        self.assertIn("allow_implicit_invocation: false", (self.skill() / "agents/openai.yaml").read_text())
        self.assertEqual(json.loads((self.skill() / "runtime.json").read_text()),
                         {"runtime_directory": str(self.home / "delegation-kit")})
        self.assertEqual(kit.plan(self.home, self.source), [])
        self.apply(uninstall=True)
        self.assertFalse((self.skill() / "SKILL.md").exists())
        self.assertFalse((self.home / "config.toml").exists())
        self.assertTrue((self.home / "delegation-kit/policy.md").exists())
        self.assertEqual(agents.read_bytes(), b"user text without final newline")
        self.assertEqual(override.read_bytes(), b"user override\n")
        self.assertEqual(kit.plan(self.home, self.source, True), [])
        self.apply()
        self.assertTrue((self.skill() / "SKILL.md").is_file())

    def test_project_install_and_disable_are_confined_to_project(self):
        root = self.root / "project"
        root.mkdir()
        (root / "AGENTS.md").write_bytes(b"project instructions")
        self.home = root / ".codex"
        args = dict(scope="project", root=root)
        self.apply(**args)
        self.assertTrue((self.skill(root) / "SKILL.md").exists())
        self.assertFalse((self.home / "AGENTS.md").exists())
        self.assertEqual((root / "AGENTS.md").read_bytes(), b"project instructions")
        self.assertEqual(kit.plan(self.home, self.source, **args), [])
        self.apply(uninstall=True, **args)
        self.assertFalse((self.skill(root) / "SKILL.md").exists())
        self.assertEqual((root / "AGENTS.md").read_bytes(), b"project instructions")

    def test_scope_cli_preview_apply_and_disable(self):
        collection = self.tree()
        cases = [("--home", self.root / "cli-home", []),
                 ("--project", self.root / "cli-project", []),
                 ("--tree", collection, ["--repo", "podboss"])]
        for flag, root, members in cases:
            with self.subTest(scope=flag), redirect_stdout(io.StringIO()):
                arguments = [flag, str(root), "--source", str(self.source)]
                skill = (root / "skills" if flag == "--home" else root / ".agents/skills") / "delegation-kit/SKILL.md"
                self.assertEqual(kit.main(arguments + members), 0)
                self.assertFalse(skill.exists())
                self.assertEqual(kit.main(arguments + members + ["--apply"]), 0)
                self.assertTrue(skill.exists())
                self.assertEqual(kit.main(arguments + ["--uninstall", "--apply"]), 0)
                self.assertFalse(skill.exists())

    def test_tree_registers_explicit_members_and_disable_uses_saved_members(self):
        root = self.tree()
        members = [root, root / "podboss", root / "group/podprocessor"]
        before = {p / "AGENTS.md": (p / "AGENTS.md").read_bytes() for p in members}
        args = dict(scope="tree", root=root, repositories=["podboss", "group/podprocessor"])
        self.apply(**args)
        for member in members:
            pointer = json.loads((self.skill(member) / "runtime.json").read_text())
            self.assertEqual(pointer["runtime_directory"], str(self.home / "delegation-kit"))
            config = kit.parse_toml((member / ".codex/config.toml").read_bytes(), member)
            self.assertEqual(config["agents"]["luna_worker"]["config_file"],
                             str(self.home / "delegation-kit/agents/luna_worker.toml"))
        self.assertEqual(kit.plan(self.home, self.source, **args), [])
        self.apply(uninstall=True, scope="tree", root=root)
        for member in members:
            self.assertFalse((self.skill(member) / "SKILL.md").exists())
            self.assertEqual((member / "AGENTS.md").read_bytes(), before[member / "AGENTS.md"])
        for member in members[1:]:
            self.assertEqual((member / ".codex/config.toml").read_text(), 'model = "keep-local"\n')
        self.assertEqual(kit.plan(self.home, self.source, True, scope="tree", root=root), [])
        self.apply(**args)

    def test_tree_update_removes_only_dropped_member_activation(self):
        root = self.tree()
        self.apply(scope="tree", root=root, repositories=["podboss", "group/podprocessor"])
        dropped = root / "group/podprocessor"
        self.apply(scope="tree", root=root, repositories=["podboss"])
        self.assertFalse((self.skill(dropped) / "SKILL.md").exists())
        self.assertEqual((dropped / ".codex/config.toml").read_text(), 'model = "keep-local"\n')
        self.assertTrue((self.skill(root / "podboss") / "SKILL.md").exists())

    def test_disable_and_reactivation_preserve_new_unowned_dropped_child_files(self):
        root = self.tree()
        child = root / "podboss"
        config = child / ".codex/config.toml"
        config.unlink()
        self.apply(scope="tree", root=root, repositories=["podboss"])
        self.apply(uninstall=True, scope="tree", root=root)
        self.assertFalse(config.exists())
        config.write_bytes(b"")
        skill = self.skill(child) / "SKILL.md"
        skill.write_bytes(b"new unrelated skill")
        self.assertEqual(kit.plan(self.home, self.source, True, scope="tree", root=root), [])
        self.assertEqual(config.read_bytes(), b"")
        self.assertEqual(skill.read_bytes(), b"new unrelated skill")
        self.apply(scope="tree", root=root, repositories=["group/podprocessor"])
        self.assertEqual(config.read_bytes(), b"")
        self.assertEqual(skill.read_bytes(), b"new unrelated skill")
        self.assertTrue((self.skill(root / "group/podprocessor") / "SKILL.md").exists())

    def test_tree_refuses_escaped_or_unlisted_targets(self):
        root = self.tree()
        for repositories in ([], ["../outside"], [str(self.root)], ["missing"]):
            with self.subTest(repositories=repositories), self.assertRaises(kit.Refusal):
                kit.plan(self.home, self.source, scope="tree", root=root, repositories=repositories)
        self.assertFalse((self.home / "delegation-kit").exists())

    @unittest.skipUnless(os.name == "nt", "Windows path anchors")
    def test_tree_rejects_current_drive_rooted_and_drive_relative_paths(self):
        root = self.tree()
        outside = self.root / "outside"
        (outside / ".git").mkdir(parents=True)
        rooted = str(outside)[len(outside.drive):]
        for name in (rooted, outside.drive + "outside"):
            with self.subTest(name=name), self.assertRaises(kit.Refusal):
                kit.plan(self.home, self.source, scope="tree", root=root, repositories=[name])
        self.assertFalse((self.home / "delegation-kit").exists())
        self.assertFalse((outside / ".codex").exists())

    def test_edited_skill_refuses_update_and_disable_without_any_writes(self):
        self.apply()
        path = self.skill() / "SKILL.md"
        path.write_text("local customization")
        before = (self.home / "config.toml").read_bytes()
        for disable in (False, True):
            with self.subTest(disable=disable), self.assertRaises(kit.Refusal):
                kit.plan(self.home, self.source, disable)
        self.assertEqual((self.home / "config.toml").read_bytes(), before)
        self.assertEqual(path.read_text(), "local customization")

    def test_unowned_skill_directory_and_tree_config_collision_refused(self):
        self.skill().mkdir(parents=True)
        (self.skill() / "personal.txt").write_text("unrelated")
        with self.assertRaises(kit.Refusal):
            kit.plan(self.home, self.source)
        self.assertFalse((self.home / "config.toml").exists())
        root = self.tree()
        config = root / "podboss/.codex/config.toml"
        config.write_text('[agents.luna_worker]\nconfig_file = "mine.toml"\n')
        with self.assertRaises(kit.Refusal):
            kit.plan(self.home, self.source, scope="tree", root=root, repositories=["podboss"])
        self.assertFalse((self.home / "delegation-kit").exists())

    def seed_old24(self, active=True):
        self.home.mkdir()
        target = self.home / "delegation-kit"
        for name in kit.OLD24_FILES:
            path = target / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes((self.source / name).read_bytes())
        activation = {}
        for name, block in kit.blocks(target, kit.OLD24_ROLES).items():
            path = self.home / name
            data = "user notes\n" if name == "AGENTS.md" else 'model = "keep"\n'
            # Published installers write exact LF bytes on every platform.
            path.write_bytes((data + block if active else data).encode())
            activation[name] = {"inserted": block, "original_exists": True}
        metadata = target / ".installation/manifest.json"
        metadata.parent.mkdir()
        metadata.write_text(json.dumps({"version": 1, "home": str(self.home), "active": active,
            "activation": activation, "last_backups": [],
            "bundle_digests": {name: kit.digest((target / name).read_bytes()) for name in kit.OLD24_FILES}}))

    def test_active_old24_migration_removes_gateway_and_keeps_user_text(self):
        self.seed_old24()
        self.apply()
        self.assertEqual((self.home / "AGENTS.md").read_text(), "user notes\n")
        self.assertTrue((self.skill() / "SKILL.md").exists())
        self.assertEqual(kit.plan(self.home, self.source), [])
        self.apply(uninstall=True)
        self.assertEqual((self.home / "AGENTS.md").read_text(), "user notes\n")
        self.assertEqual((self.home / "config.toml").read_text(), 'model = "keep"\n')

    def test_disabled_old24_upgrades_and_old24_can_disable_directly(self):
        self.seed_old24(active=False)
        self.apply(uninstall=True)
        self.apply()
        self.assertEqual((self.home / "AGENTS.md").read_text(), "user notes\n")
        self.assertTrue((self.skill() / "SKILL.md").exists())

    def test_tampered_discovery_path_refused_before_changes(self):
        self.apply()
        path = self.home / "delegation-kit/.installation/manifest.json"
        manifest = json.loads(path.read_text())
        record = manifest["discovery"].pop(str(self.skill() / "SKILL.md"))
        manifest["discovery"][str(self.root / "unrelated.txt")] = record
        path.write_text(json.dumps(manifest))
        with self.assertRaises(kit.Refusal):
            kit.plan(self.home, self.source, True)
        self.assertTrue((self.skill() / "SKILL.md").exists())


if __name__ == "__main__":
    unittest.main()
