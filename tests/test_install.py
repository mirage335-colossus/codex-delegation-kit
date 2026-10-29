"""Disposable filesystem tests; never read or write the real Codex home."""

import importlib.util
import json
from pathlib import Path
import os
import sys
import tempfile
import unittest
from unittest import mock


MODULE_PATH = Path(__file__).absolute().parents[1] / "install.py"
SPEC = importlib.util.spec_from_file_location("delegation_install", MODULE_PATH)
kit = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = kit
SPEC.loader.exec_module(kit)
PUBLISHED_LEGACY_AGENTS_BLOCK = (
    "# >>> CODEX GLOBAL DELEGATION KIT (managed; do not edit) >>>\n"
    "For coding, repository investigation, debugging, software design, and technical factual research tasks, "
    "read and follow `{{policy}}` before deciding whether to delegate.\n"
    "Preserve the user's selected primary model. Project contracts and authorization "
    "constraints remain applicable.\n"
    "# <<< CODEX GLOBAL DELEGATION KIT <<<\n"
)
PUBLISHED_OLD21_AGENTS_BLOCK = (
    "# >>> CODEX GLOBAL DELEGATION KIT (managed; do not edit) >>>\n"
    "For coding, repository investigation, debugging, software design, and technical factual research, "
    "before substantive work on each new main task, obtain one initial Astra review using only the original "
    "prompt and context already available. Do no preparatory investigation, planning, decomposition, "
    "or implementation, and do not dispatch any other subagent, before obtaining that review. "
    "Ask about intent, constraints, ambiguities, approaches "
    "and alternatives, and early user questions. Clearly trivial mechanical authorized configuration edits, "
    "Git pulls, or basic recompiles may skip this review; if unsure, get the review. Reuse it for ordinary "
    "progress and continuations and delegated subtasks; do not repeat it or apply it recursively. Then read "
    "and follow `{{policy}}` before deciding whether to delegate.\n"
    "Preserve the user's selected primary model. Project contracts and authorization "
    "constraints remain applicable.\n"
    "# <<< CODEX GLOBAL DELEGATION KIT <<<\n"
)


def published_legacy_agents_block(target):
    return PUBLISHED_LEGACY_AGENTS_BLOCK.replace("{{policy}}", str(target / "policy.md"))


def published_old21_agents_block(target):
    return PUBLISHED_OLD21_AGENTS_BLOCK.replace("{{policy}}", str(target / "policy.md"))


class InstallerTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.source = self.root / "source"
        self.home = self.root / "codex"
        self.home.mkdir()
        for name in kit.FILES:
            path = self.source / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b'model = "fixture"\n' if name.endswith(".toml") else b"# fixture\n")
            path.chmod(0o640)
        self.agents = self.home / "AGENTS.md"
        self.config = self.home / "config.toml"
        self.agents.write_bytes(b"Keep local instructions exactly.\n")
        self.agents.chmod(0o640)
        self.config.write_bytes(b'model = "primary"\nmodel_reasoning_effort = "ultra"')
        self.config.chmod(0o600)
        self.original = {path: kit.read_state(path) for path in (self.agents, self.config)}

    def activate(self):
        kit.apply(kit.plan(self.home, self.source))

    def assert_original(self):
        for path, state in self.original.items():
            self.assertEqual(kit.read_state(path), state)

    def seed_legacy(self, *, active=True):
        """Create the prior eight-file version-1 installation layout."""
        return self.seed_layout(kit.LEGACY_FILES, kit.LEGACY_ROLES, active=active)

    def seed_advisory(self, *, active=True):
        """Create the eleven-file, six-role layout before controller support."""
        return self.seed_layout(kit.ADVISORY_FILES, kit.PRE_SWARM_ROLES, active=active)

    def seed_controller(self, *, active=True):
        """Create the seventeen-file controller layout before engineering support."""
        return self.seed_layout(kit.CONTROLLER_FILES, kit.PRE_SWARM_ROLES, active=active)

    def seed_engineering(self, *, active=True):
        """Create the eighteen-file engineering layout before swarm roles."""
        return self.seed_layout(kit.ENGINEERING_FILES, kit.PRE_SWARM_ROLES, active=active)

    def seed_swarm(self, *, active=True):
        """Create the twenty-file, eight-role layout before strategic review."""
        return self.seed_layout(kit.SWARM_FILES, kit.PRE_ASTRA_ROLES, active=active)

    def seed_old21(self, *, active=True):
        """Create the published twenty-one-file Astra-first installation."""
        return self.seed_layout(kit.OLD21_FILES, kit.OLD21_ROLES, active=active)

    def seed_current_with_legacy_gateway(self, *, active=True):
        """Create a published old bundle with its earlier legacy AGENTS gateway."""
        target = self.seed_layout(kit.OLD21_FILES, kit.OLD21_ROLES, active=active)
        legacy = published_legacy_agents_block(target)
        manifest_path = target / ".installation/manifest.json"
        manifest = json.loads(manifest_path.read_text())
        record = manifest["activation"]["AGENTS.md"]
        inserted = record["inserted"]
        old_prefix = "\n" if inserted.startswith("\n") else ""
        original = self.agents.read_text()
        if active:
            self.agents.write_text(original.replace(inserted, old_prefix + legacy, 1))
        record["inserted"] = old_prefix + legacy
        manifest_path.write_text(json.dumps(manifest))
        return target

    def seed_layout(self, files, roles, *, active):
        target = self.home / "delegation-kit"
        for name in files:
            path = target / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes((self.source / name).read_bytes())
        activation = {}
        for name, block in kit.blocks(target, roles).items():
            if name == "AGENTS.md" and roles == kit.OLD21_ROLES:
                block = published_old21_agents_block(target)
            elif name == "AGENTS.md" and roles != kit.ROLES:
                block = published_legacy_agents_block(target)
            path = self.home / name
            before = kit.read_state(path)
            text = (before.data or b"").decode()
            inserted = ("\n" if text and not text.endswith("\n") else "") + block
            activation[name] = {"inserted": inserted, "original_exists": before.data is not None}
            if active:
                path.write_bytes((text + inserted).encode())
        manifest_path = target / ".installation/manifest.json"
        manifest_path.parent.mkdir()
        manifest_path.write_text(json.dumps({
            "version": 1, "home": str(self.home), "active": active,
            "activation": activation,
            "bundle_digests": {name: kit.digest((target / name).read_bytes())
                               for name in files},
            "last_backups": [],
        }))
        return target

    def snapshot_home(self):
        return {path.relative_to(self.home): kit.read_state(path)
                for path in self.home.rglob("*") if path.is_file()}

    def assert_only_role_block_updated(self, target, globals_before, prior_roles=kit.PRE_SWARM_ROLES,
                                       prior_agents_block=None):
        old = kit.blocks(target, prior_roles)["config.toml"].encode()
        new = kit.blocks(target)["config.toml"].encode()
        if prior_agents_block is not None:
            old_agents = prior_agents_block
        elif prior_roles == kit.OLD21_ROLES:
            old_agents = published_old21_agents_block(target).encode()
        else:
            old_agents = published_legacy_agents_block(target).encode()
        new_agents = kit.blocks(target)["AGENTS.md"].encode()
        self.assertEqual(globals_before[self.config].data.count(old), 1)
        self.assertEqual(globals_before[self.agents].data.count(old_agents), 1)
        for path, before in globals_before.items():
            if path == self.config:
                expected = kit.State(before.data.replace(old, new, 1), before.mode)
            elif path == self.agents:
                expected = kit.State(before.data.replace(old_agents, new_agents, 1), before.mode)
            else:
                expected = before
            self.assertEqual(kit.read_state(path), expected)

    def test_active_legacy_upgrade_preserves_config_position_history_and_roundtrip(self):
        target = self.seed_legacy()
        self.config.write_bytes(self.config.read_bytes() + b'\n[history]\npersistence = "save-all"\n')
        before = self.config.read_bytes()
        old_block = kit.blocks(target, kit.LEGACY_ROLES)["config.toml"].encode()
        historical = target / ".installation/backups/older-transaction/config.toml"
        historical.parent.mkdir(parents=True)
        historical.write_bytes(b"earlier user configuration\n")
        evidence = target / "state/prior-assignment/result.json"
        evidence.parent.mkdir(parents=True)
        evidence.write_bytes(b'{"status": "completed"}\n')
        history = {path: path.read_bytes() for path in (historical, evidence)}

        self.activate()
        self.assertEqual(self.config.read_bytes(), before.replace(old_block, kit.blocks(target)["config.toml"].encode()))
        manifest = json.loads((target / ".installation/manifest.json").read_text())
        self.assertEqual(manifest["version"], 1)
        self.assertEqual(set(manifest["bundle_digests"]), set(kit.FILES))
        self.assertEqual(manifest["source_directory"], str(self.source.absolute()))
        loaded = kit.parse_toml(self.config.read_bytes(), self.config)
        self.assertEqual(set(loaded["agents"]), set(kit.ROLES))
        self.assertEqual(kit.plan(self.home, self.source), [])
        self.assertEqual({path: path.read_bytes() for path in history}, history)
        kit.apply(kit.plan(self.home, self.source, uninstall=True))
        self.assertEqual(kit.read_state(self.agents), self.original[self.agents])
        self.assertEqual(self.config.read_bytes(), self.original[self.config].data + b'\n[history]\npersistence = "save-all"\n')
        self.assertEqual({path: path.read_bytes() for path in history}, history)

    def test_current_old_gateway_upgrade_and_repeat_preview(self):
        target = self.seed_current_with_legacy_gateway()
        self.agents.write_bytes(b"leading instructions without newline")
        legacy = published_legacy_agents_block(target).encode()
        self.agents.write_bytes(self.agents.read_bytes() + legacy + b"trailing instructions\n")
        original = kit.read_state(self.agents)
        config_before = kit.read_state(self.config)
        history = target / "state/prior-assignment/result.json"
        history.parent.mkdir(parents=True)
        history.write_bytes(b'{"status": "completed"}\n')
        kit.apply(kit.plan(self.home, self.source))
        current = kit.blocks(target)["AGENTS.md"].encode()
        self.assertEqual(self.agents.read_bytes(), original.data.replace(legacy, current, 1))
        self.assertEqual(kit.read_state(self.agents).mode, original.mode)
        old_config = kit.blocks(target, kit.OLD21_ROLES)["config.toml"].encode()
        new_config = kit.blocks(target)["config.toml"].encode()
        self.assertEqual(kit.read_state(self.config),
                         kit.State(config_before.data.replace(old_config, new_config, 1), config_before.mode))
        self.assertEqual(history.read_bytes(), b'{"status": "completed"}\n')
        manifest = json.loads((target / ".installation/manifest.json").read_text())
        self.assertEqual(manifest["activation"]["AGENTS.md"]["inserted"], current.decode())
        self.assertEqual(set(manifest["bundle_digests"]), set(kit.FILES))
        self.assertEqual(manifest["source_directory"], str(self.source.absolute()))
        self.assertEqual(kit.plan(self.home, self.source), [])

    def test_current_old_gateway_disable_and_reactivate_when_globals_were_absent(self):
        for path in (self.agents, self.config):
            path.unlink()
        self.original = {path: kit.read_state(path) for path in (self.agents, self.config)}
        target = self.seed_current_with_legacy_gateway()
        kit.apply(kit.plan(self.home, self.source, uninstall=True))
        self.assertIsNone(kit.read_state(self.agents).data)
        self.assertIsNone(kit.read_state(self.config).data)
        self.activate()
        self.assertIn("before substantive work on each new main task", self.agents.read_text())
        self.assertEqual(set(kit.parse_toml(self.config.read_bytes(), self.config)["agents"]), set(kit.ROLES))
        self.assertEqual(kit.plan(self.home, self.source), [])

    def test_current_old_gateway_without_original_final_newline_upgrades_and_roundtrips(self):
        self.agents.write_bytes(b"original instructions without final newline")
        original = kit.read_state(self.agents)
        target = self.seed_current_with_legacy_gateway()
        manifest_path = target / ".installation/manifest.json"
        manifest = json.loads(manifest_path.read_text())
        old_inserted = manifest["activation"]["AGENTS.md"]["inserted"]
        self.assertTrue(old_inserted.startswith("\n"))
        self.assertIn(old_inserted.encode(), self.agents.read_bytes())

        kit.apply(kit.plan(self.home, self.source))
        current = kit.blocks(target)["AGENTS.md"].encode()
        self.assertEqual(self.agents.read_bytes(), original.data + b"\n" + current)
        self.assertEqual(kit.plan(self.home, self.source), [])
        kit.apply(kit.plan(self.home, self.source, uninstall=True))
        self.assertEqual(kit.read_state(self.agents), original)

    def test_old21_active_upgrade_preserves_published_gateway_and_unrelated_bytes(self):
        target = self.seed_old21()
        suffix = b"\n# user suffix without final newline"
        self.agents.write_bytes(self.agents.read_bytes() + suffix)
        before = {path: kit.read_state(path) for path in (self.agents, self.config)}

        kit.apply(kit.plan(self.home, self.source))

        self.assert_only_role_block_updated(target, before, kit.OLD21_ROLES)
        manifest = json.loads((target / ".installation/manifest.json").read_text())
        self.assertEqual(set(manifest["bundle_digests"]), set(kit.FILES))
        self.assertEqual(manifest["activation"]["AGENTS.md"]["inserted"],
                         kit.blocks(target)["AGENTS.md"])
        self.assertTrue(self.agents.read_bytes().endswith(suffix))
        self.assertEqual(kit.plan(self.home, self.source), [])

    def test_old21_direct_disable_preserves_personal_new_role(self):
        target = self.seed_old21()
        personal = b'\n[agents.astra_initial]\nconfig_file = "personal-initial.toml"\n'
        self.config.write_bytes(self.config.read_bytes() + personal)

        kit.apply(kit.plan(self.home, self.source, uninstall=True))

        self.assertEqual(kit.read_state(self.agents), self.original[self.agents])
        self.assertEqual(kit.read_state(self.config), kit.State(
            self.original[self.config].data + personal, self.original[self.config].mode))
        manifest = json.loads((target / ".installation/manifest.json").read_text())
        self.assertFalse(manifest["active"])
        self.assertEqual(set(manifest["bundle_digests"]), set(kit.OLD21_FILES))
        self.assertEqual(kit.plan(self.home, self.source, uninstall=True), [])

    def test_old21_legacy_gateway_is_accepted_and_active_disable_roundtrips(self):
        target = self.seed_old21()
        manifest_path = target / ".installation/manifest.json"
        manifest = json.loads(manifest_path.read_text())
        inserted = manifest["activation"]["AGENTS.md"]["inserted"]
        prefix = "\n" if inserted.startswith("\n") else ""
        legacy = prefix + published_legacy_agents_block(target)
        self.agents.write_text(self.agents.read_text().replace(inserted, legacy, 1))
        manifest["activation"]["AGENTS.md"]["inserted"] = legacy
        manifest_path.write_text(json.dumps(manifest))
        active_globals = {path: kit.read_state(path) for path in (self.agents, self.config)}

        kit.apply(kit.plan(self.home, self.source))
        self.assert_only_role_block_updated(target, active_globals, kit.OLD21_ROLES,
                                            prior_agents_block=legacy.encode())
        kit.apply(kit.plan(self.home, self.source, uninstall=True))
        self.assertEqual(kit.read_state(self.agents), self.original[self.agents])
        self.assertEqual(kit.read_state(self.config), self.original[self.config])

    def assert_inactive_old21_reactivation_preserves(self, *, legacy_gateway):
        self.home = self.root / ("legacy old21 home" if legacy_gateway else "published old21 home")
        self.home.mkdir()
        self.agents = self.home / "AGENTS.md"
        self.config = self.home / "config.toml"
        self.agents.write_bytes(b"Local instructions without final newline")
        self.agents.chmod(0o640)
        self.config.write_bytes(
            b'model = "primary"\nmodel_reasoning_effort = "ultra"\n'
            b'\n[history]\npersistence = "save-all"\n')
        self.config.chmod(0o640)
        self.original = {path: kit.read_state(path) for path in (self.agents, self.config)}
        target = self.seed_old21(active=False)
        manifest_path = target / ".installation/manifest.json"
        if legacy_gateway:
            manifest = json.loads(manifest_path.read_text())
            inserted = manifest["activation"]["AGENTS.md"]["inserted"]
            legacy = "\n" + published_legacy_agents_block(target)
            self.assertTrue(inserted.startswith("\n"))
            manifest["activation"]["AGENTS.md"]["inserted"] = legacy
            manifest_path.write_text(json.dumps(manifest))
        evidence = target / "state/prior-assignment/result.json"
        evidence.parent.mkdir(parents=True)
        evidence.write_bytes(b'{"status":"completed","keep":true}\n')
        before = {path: kit.read_state(path) for path in (self.agents, self.config)}

        kit.apply(kit.plan(self.home, self.source))
        self.assertEqual(kit.plan(self.home, self.source), [])
        manifest = json.loads(manifest_path.read_text())
        self.assertTrue(manifest["active"])
        self.assertEqual(set(manifest["bundle_digests"]), set(kit.FILES))
        self.assertEqual(kit.read_state(self.agents).mode, before[self.agents].mode)
        self.assertEqual(kit.read_state(self.config).mode, before[self.config].mode)
        self.assertEqual(evidence.read_bytes(), b'{"status":"completed","keep":true}\n')

        kit.apply(kit.plan(self.home, self.source, uninstall=True))
        self.assertEqual(kit.read_state(self.agents), before[self.agents])
        self.assertEqual(kit.read_state(self.config), before[self.config])
        self.assertEqual(evidence.read_bytes(), b'{"status":"completed","keep":true}\n')

    def test_inactive_old21_upgrade_reactivation_and_roundtrip_both_gateways(self):
        for legacy_gateway in (False, True):
            with self.subTest(legacy_gateway=legacy_gateway):
                self.assert_inactive_old21_reactivation_preserves(legacy_gateway=legacy_gateway)

    def test_current22_manifest_rejects_both_historical_gateways_without_writes(self):
        self.activate()
        target = self.home / "delegation-kit"
        manifest_path = target / ".installation/manifest.json"
        original_manifest = json.loads(manifest_path.read_text())
        historical = (published_old21_agents_block(target), published_legacy_agents_block(target))
        for gateway in historical:
            with self.subTest(gateway=gateway[:24]):
                manifest = json.loads(json.dumps(original_manifest))
                manifest["activation"]["AGENTS.md"]["inserted"] = gateway
                manifest_path.write_text(json.dumps(manifest))
                before = self.snapshot_home()
                for uninstall in (False, True):
                    with self.subTest(uninstall=uninstall), self.assertRaisesRegex(
                            kit.Refusal, "unexpected managed block"):
                        kit.plan(self.home, self.source, uninstall=uninstall)
                    self.assertEqual(self.snapshot_home(), before)
        manifest_path.write_text(json.dumps(original_manifest))

    def test_current_modified_gateway_refused_without_writes(self):
        self.seed_current_with_legacy_gateway()
        self.agents.write_bytes(self.agents.read_bytes().replace(b"selected primary model", b"changed model"))
        before = self.snapshot_home()
        for uninstall in (False, True):
            with self.subTest(uninstall=uninstall), self.assertRaises(kit.Refusal):
                kit.plan(self.home, self.source, uninstall)
            self.assertEqual(self.snapshot_home(), before)

    def test_inactive_legacy_installation_upgrades_and_roundtrips(self):
        target = self.seed_legacy(active=False)
        self.assertEqual(kit.plan(self.home, self.source, uninstall=True), [])
        self.activate()
        manifest = json.loads((target / ".installation/manifest.json").read_text())
        self.assertTrue(manifest["active"])
        self.assertEqual(set(manifest["bundle_digests"]), set(kit.FILES))
        self.assertEqual(kit.plan(self.home, self.source), [])
        kit.apply(kit.plan(self.home, self.source, uninstall=True))
        self.assert_original()

    def test_active_legacy_can_be_disabled_before_upgrade(self):
        self.seed_legacy()
        kit.apply(kit.plan(self.home, self.source, uninstall=True))
        self.assert_original()
        self.activate()
        self.assertEqual(set(kit.parse_toml(self.config.read_bytes(), self.config)["agents"]), set(kit.ROLES))

    def test_legacy_upgrade_refuses_unowned_new_role_even_with_identical_bytes(self):
        target = self.seed_legacy()
        name = "agents/inherited_worker.toml"
        (target / name).write_bytes((self.source / name).read_bytes())
        before = self.snapshot_home()
        with self.assertRaisesRegex(kit.Refusal, "not owned"):
            kit.plan(self.home, self.source)
        self.assertEqual(self.snapshot_home(), before)

    def test_unknown_manifest_inventory_is_refused_without_writes(self):
        self.activate()
        path = self.home / "delegation-kit/.installation/manifest.json"
        manifest = json.loads(path.read_text())
        manifest["bundle_digests"]["unexpected-file"] = "unrecognized"
        path.write_text(json.dumps(manifest))
        before = self.snapshot_home()
        for uninstall in (False, True):
            with self.subTest(uninstall=uninstall), self.assertRaisesRegex(kit.Refusal, "unexpected bundle file list"):
                kit.plan(self.home, self.source, uninstall=uninstall)
            self.assertEqual(self.snapshot_home(), before)

    def test_advisory_upgrade_preserves_activation_and_retained_controller_state(self):
        target = self.seed_advisory()
        globals_before = {path: kit.read_state(path) for path in (self.agents, self.config)}
        retained = target / "state/owned-run/state.sqlite3"
        retained.parent.mkdir(parents=True)
        retained.write_bytes(b"retained database fixture; not an installer input\n")
        receipt = target / "state/owned-run/operations/op-1/receipt.json"
        receipt.parent.mkdir(parents=True)
        receipt.write_bytes(b'{"operation_id":"op-1","state":"running"}\n')
        history = {path: path.read_bytes() for path in (retained, receipt)}

        preview = kit.plan(self.home, self.source)
        self.assertTrue(preview)
        self.assertEqual({path: kit.read_state(path) for path in globals_before}, globals_before)
        kit.apply(preview)
        self.assert_only_role_block_updated(target, globals_before)
        manifest = json.loads((target / ".installation/manifest.json").read_text())
        self.assertEqual(set(manifest["bundle_digests"]), set(kit.FILES))
        for name in kit.FILES:
            self.assertEqual((target / name).read_bytes(), (self.source / name).read_bytes())
        self.assertEqual(kit.plan(self.home, self.source), [])
        self.assertEqual({path: path.read_bytes() for path in history}, history)
        kit.apply(kit.plan(self.home, self.source, uninstall=True))
        self.assert_original()
        self.assertEqual({path: path.read_bytes() for path in history}, history)
        self.assertEqual(kit.plan(self.home, self.source, uninstall=True), [])

    def test_inactive_advisory_upgrade_and_disable_before_upgrade(self):
        target = self.seed_advisory(active=False)
        self.assertEqual(kit.plan(self.home, self.source, uninstall=True), [])
        self.activate()
        manifest = json.loads((target / ".installation/manifest.json").read_text())
        self.assertTrue(manifest["active"])
        self.assertEqual(set(manifest["bundle_digests"]), set(kit.FILES))
        self.assertEqual(kit.plan(self.home, self.source), [])
        kit.apply(kit.plan(self.home, self.source, uninstall=True))
        self.assert_original()

    def test_active_advisory_can_be_disabled_without_installing_controller(self):
        target = self.seed_advisory()
        kit.apply(kit.plan(self.home, self.source, uninstall=True))
        self.assert_original()
        self.assertFalse((target / "controller.py").exists())
        manifest = json.loads((target / ".installation/manifest.json").read_text())
        self.assertEqual(set(manifest["bundle_digests"]), set(kit.ADVISORY_FILES))

    def test_advisory_upgrade_refuses_unowned_controller_even_with_identical_bytes(self):
        target = self.seed_advisory()
        name = "controller.py"
        (target / name).write_bytes((self.source / name).read_bytes())
        before = self.snapshot_home()
        with self.assertRaisesRegex(kit.Refusal, "not owned"):
            kit.plan(self.home, self.source)
        self.assertEqual(self.snapshot_home(), before)

    def test_controller_upgrade_preserves_activation_owned_execution_and_history(self):
        target = self.seed_controller()
        globals_before = {path: kit.read_state(path) for path in (self.agents, self.config)}
        retained = {
            target / "state/run/state.sqlite3": b"retained scheduling database\n",
            target / "state/run/operations/op-1/receipt.json": b'{"state":"running","released":false}\n',
            target / "state/run/operations/op-1/patch.diff": b"retained original patch\n",
            target / ".installation/backups/old/manifest.json": b"retained historical manifest\n",
        }
        for path, contents in retained.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(contents)

        preview = kit.plan(self.home, self.source)
        self.assertTrue(any(change.path == target / "engineering.py" for change in preview))
        self.assertFalse((target / "engineering.py").exists())
        kit.apply(preview)
        self.assert_only_role_block_updated(target, globals_before)
        manifest = json.loads((target / ".installation/manifest.json").read_text())
        self.assertEqual(len(manifest["bundle_digests"]), 22)
        self.assertEqual(set(manifest["bundle_digests"]), set(kit.FILES))
        self.assertEqual((target / "engineering.py").read_bytes(), (self.source / "engineering.py").read_bytes())
        self.assertEqual(kit.plan(self.home, self.source), [])
        self.assertEqual({path: path.read_bytes() for path in retained}, retained)

        kit.apply(kit.plan(self.home, self.source, uninstall=True))
        self.assert_original()
        self.assertTrue((target / "engineering.py").is_file())
        self.assertEqual({path: path.read_bytes() for path in retained}, retained)
        self.assertEqual(kit.plan(self.home, self.source, uninstall=True), [])

    def test_inactive_controller_upgrade_and_idempotent_disable(self):
        target = self.seed_controller(active=False)
        self.assertEqual(kit.plan(self.home, self.source, uninstall=True), [])
        self.activate()
        manifest = json.loads((target / ".installation/manifest.json").read_text())
        self.assertTrue(manifest["active"])
        self.assertEqual(set(manifest["bundle_digests"]), set(kit.FILES))
        self.assertEqual(kit.plan(self.home, self.source), [])
        kit.apply(kit.plan(self.home, self.source, uninstall=True))
        self.assert_original()

    def test_controller_can_be_disabled_without_installing_engineering(self):
        target = self.seed_controller()
        kit.apply(kit.plan(self.home, self.source, uninstall=True))
        self.assert_original()
        self.assertFalse((target / "engineering.py").exists())
        manifest = json.loads((target / ".installation/manifest.json").read_text())
        self.assertEqual(set(manifest["bundle_digests"]), set(kit.CONTROLLER_FILES))

    def test_controller_upgrade_refuses_unowned_engineering_even_with_identical_bytes(self):
        target = self.seed_controller()
        (target / "engineering.py").write_bytes((self.source / "engineering.py").read_bytes())
        before = self.snapshot_home()
        with self.assertRaisesRegex(kit.Refusal, "not owned"):
            kit.plan(self.home, self.source)
        self.assertEqual(self.snapshot_home(), before)

    def test_engineering_upgrade_preserves_config_position_execution_history_and_modes(self):
        self.config.write_bytes(self.config.read_bytes() +
                               b'\nservice_tier = "default"\n[agents]\nmax_threads = 7\n')
        self.original[self.config] = kit.read_state(self.config)
        target = self.seed_engineering()
        suffix = b'\n[history]\npersistence = "save-all"\n'
        self.config.write_bytes(self.config.read_bytes() + suffix)
        globals_before = {path: kit.read_state(path) for path in (self.agents, self.config)}
        retained = {
            target / "state/run/state.sqlite3": b"retained scheduling database\n",
            target / "state/run/operations/op-1/receipt.json": b'{"state":"running","released":false}\n',
            target / "state/run/operations/op-1/patch.diff": b"retained original patch\n",
            target / ".installation/backups/old/manifest.json": b"retained historical manifest\n",
        }
        for path, contents in retained.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(contents)
        before = self.snapshot_home()
        preview = kit.plan(self.home, self.source)
        for role in ("inherited_swarm", "luna_swarm"):
            destination = target / "agents" / (role + ".toml")
            self.assertTrue(any(change.path == destination for change in preview))
            self.assertFalse(destination.exists())
        self.assertEqual(self.snapshot_home(), before)

        kit.apply(preview)
        self.assert_only_role_block_updated(target, globals_before)
        loaded = kit.parse_toml(self.config.read_bytes(), self.config)
        self.assertEqual(loaded["model"], "primary")
        self.assertEqual(loaded["model_reasoning_effort"], "ultra")
        self.assertEqual(loaded["service_tier"], "default")
        self.assertEqual(loaded["agents"]["max_threads"], 7)
        self.assertEqual(set(loaded["agents"]), {"max_threads", *kit.ROLES})
        manifest = json.loads((target / ".installation/manifest.json").read_text())
        self.assertEqual(manifest["version"], 1)
        self.assertEqual(len(manifest["bundle_digests"]), 22)
        self.assertEqual(set(manifest["bundle_digests"]), set(kit.FILES))
        for name in kit.FILES:
            self.assertEqual((target / name).read_bytes(), (self.source / name).read_bytes())
        self.assertEqual({path: path.read_bytes() for path in retained}, retained)
        self.assertEqual(kit.plan(self.home, self.source), [])

        kit.apply(kit.plan(self.home, self.source, uninstall=True))
        self.assertEqual(kit.read_state(self.agents), self.original[self.agents])
        self.assertEqual(kit.read_state(self.config), kit.State(
            self.original[self.config].data + suffix, self.original[self.config].mode))
        self.assertEqual({path: path.read_bytes() for path in retained}, retained)
        self.assertEqual(kit.plan(self.home, self.source, uninstall=True), [])

    def test_inactive_engineering_upgrade_and_idempotent_disable(self):
        target = self.seed_engineering(active=False)
        self.assertEqual(kit.plan(self.home, self.source, uninstall=True), [])
        self.activate()
        manifest = json.loads((target / ".installation/manifest.json").read_text())
        self.assertTrue(manifest["active"])
        self.assertEqual(set(manifest["bundle_digests"]), set(kit.FILES))
        self.assertEqual(kit.plan(self.home, self.source), [])
        kit.apply(kit.plan(self.home, self.source, uninstall=True))
        self.assert_original()

    def test_engineering_can_be_disabled_without_installing_swarm_roles(self):
        target = self.seed_engineering()
        kit.apply(kit.plan(self.home, self.source, uninstall=True))
        self.assert_original()
        for role in ("inherited_swarm", "luna_swarm"):
            self.assertFalse((target / "agents" / (role + ".toml")).exists())
        manifest = json.loads((target / ".installation/manifest.json").read_text())
        self.assertEqual(set(manifest["bundle_digests"]), set(kit.ENGINEERING_FILES))
        self.assertEqual(kit.plan(self.home, self.source, uninstall=True), [])

    def test_swarm_upgrade_preserves_config_position_execution_history_and_modes(self):
        target = self.seed_swarm()
        suffix = b'\n[history]\npersistence = "save-all"\n'
        self.config.write_bytes(self.config.read_bytes() + suffix)
        globals_before = {path: kit.read_state(path) for path in (self.agents, self.config)}
        retained = {
            target / "state/run/operations/op-1/receipt.json": b'{"state":"running","released":false}\n',
            target / "state/run/operations/op-1/patch.diff": b"retained original patch\n",
            target / ".installation/backups/old/manifest.json": b"retained historical manifest\n",
        }
        for path, contents in retained.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(contents)
        before = self.snapshot_home()
        preview = kit.plan(self.home, self.source)
        destination = target / "agents/astra_expert.toml"
        self.assertTrue(any(change.path == destination for change in preview))
        self.assertFalse(destination.exists())
        self.assertEqual(self.snapshot_home(), before)

        kit.apply(preview)
        self.assert_only_role_block_updated(target, globals_before, kit.PRE_ASTRA_ROLES)
        manifest = json.loads((target / ".installation/manifest.json").read_text())
        self.assertEqual(manifest["version"], 1)
        self.assertEqual(len(manifest["bundle_digests"]), 22)
        self.assertEqual(set(manifest["bundle_digests"]), set(kit.FILES))
        for name in kit.FILES:
            self.assertEqual((target / name).read_bytes(), (self.source / name).read_bytes())
        self.assertEqual({path: path.read_bytes() for path in retained}, retained)
        self.assertEqual(kit.plan(self.home, self.source), [])

        kit.apply(kit.plan(self.home, self.source, uninstall=True))
        self.assertEqual(kit.read_state(self.agents), self.original[self.agents])
        self.assertEqual(kit.read_state(self.config), kit.State(
            self.original[self.config].data + suffix, self.original[self.config].mode))
        self.assertEqual({path: path.read_bytes() for path in retained}, retained)
        self.assertEqual(kit.plan(self.home, self.source, uninstall=True), [])

    def test_inactive_swarm_upgrade_and_idempotent_disable(self):
        target = self.seed_swarm(active=False)
        self.assertEqual(kit.plan(self.home, self.source, uninstall=True), [])
        self.activate()
        manifest = json.loads((target / ".installation/manifest.json").read_text())
        self.assertTrue(manifest["active"])
        self.assertEqual(set(manifest["bundle_digests"]), set(kit.FILES))
        self.assertEqual(kit.plan(self.home, self.source), [])
        kit.apply(kit.plan(self.home, self.source, uninstall=True))
        self.assert_original()

    def assert_swarm_disable_preserves_personal_astra_role(self, *, standalone):
        target = self.seed_swarm()
        personal = b'\n[agents.astra_expert]\nconfig_file = "personal-astra.toml"\n'
        if standalone:
            personal_path = self.home / "agents/different_filename.toml"
            personal_path.parent.mkdir()
            personal_path.write_bytes(b'name = "astra_expert"\n')
        else:
            self.config.write_bytes(self.config.read_bytes() + personal)
        before = self.snapshot_home()
        with self.assertRaisesRegex(kit.Refusal, "conflicts"):
            kit.plan(self.home, self.source)
        self.assertEqual(self.snapshot_home(), before)

        kit.apply(kit.plan(self.home, self.source, uninstall=True))
        self.assertEqual(kit.read_state(self.agents), self.original[self.agents])
        self.assertEqual(kit.read_state(self.config), kit.State(
            self.original[self.config].data + (b"" if standalone else personal),
            self.original[self.config].mode))
        if standalone:
            self.assertEqual(kit.read_state(personal_path), before[personal_path.relative_to(self.home)])
        manifest = json.loads((target / ".installation/manifest.json").read_text())
        self.assertFalse(manifest["active"])
        self.assertEqual(set(manifest["bundle_digests"]), set(kit.SWARM_FILES))
        self.assertEqual(len(manifest["bundle_digests"]), 20)
        self.assertFalse((target / "agents/astra_expert.toml").exists())
        self.assertEqual(kit.plan(self.home, self.source, uninstall=True), [])

    def test_swarm_disable_preserves_personal_astra_config_role(self):
        self.assert_swarm_disable_preserves_personal_astra_role(standalone=False)

    def test_swarm_disable_preserves_personal_astra_standalone_role(self):
        self.assert_swarm_disable_preserves_personal_astra_role(standalone=True)

    def test_swarm_upgrade_refuses_unowned_astra_role_even_with_identical_bytes(self):
        target = self.seed_swarm()
        name = "agents/astra_expert.toml"
        (target / name).write_bytes((self.source / name).read_bytes())
        before = self.snapshot_home()
        with self.assertRaisesRegex(kit.Refusal, "not owned"):
            kit.plan(self.home, self.source)
        self.assertEqual(self.snapshot_home(), before)

    def assert_historical_disable_preserves_personal_swarm_roles(self, seed, files):
        target = seed()
        personal = (b'\n[agents.luna_swarm]\nconfig_file = "personal-luna.toml"\n'
                    b'\n[agents.inherited_swarm]\nconfig_file = "personal-inherited.toml"\n')
        self.config.write_bytes(self.config.read_bytes() + personal)
        before = self.snapshot_home()
        with self.assertRaisesRegex(kit.Refusal, "Existing agent role conflicts"):
            kit.plan(self.home, self.source)
        self.assertEqual(self.snapshot_home(), before)

        kit.apply(kit.plan(self.home, self.source, uninstall=True))
        self.assertEqual(kit.read_state(self.agents), self.original[self.agents])
        self.assertEqual(kit.read_state(self.config), kit.State(
            self.original[self.config].data + personal, self.original[self.config].mode))
        manifest = json.loads((target / ".installation/manifest.json").read_text())
        self.assertFalse(manifest["active"])
        self.assertEqual(set(manifest["bundle_digests"]), set(files))
        for role in ("inherited_swarm", "luna_swarm"):
            self.assertFalse((target / "agents" / (role + ".toml")).exists())
        self.assertEqual(kit.plan(self.home, self.source, uninstall=True), [])

    def test_advisory_disable_preserves_personal_swarm_roles(self):
        self.assert_historical_disable_preserves_personal_swarm_roles(
            self.seed_advisory, kit.ADVISORY_FILES)

    def test_controller_disable_preserves_personal_swarm_roles(self):
        self.assert_historical_disable_preserves_personal_swarm_roles(
            self.seed_controller, kit.CONTROLLER_FILES)

    def test_engineering_disable_preserves_personal_swarm_roles(self):
        self.assert_historical_disable_preserves_personal_swarm_roles(
            self.seed_engineering, kit.ENGINEERING_FILES)

    def test_engineering_upgrade_refuses_unowned_swarm_roles_even_with_identical_bytes(self):
        target = self.seed_engineering()
        for role in ("inherited_swarm", "luna_swarm"):
            with self.subTest(role=role):
                name = "agents/" + role + ".toml"
                destination = target / name
                destination.write_bytes((self.source / name).read_bytes())
                before = self.snapshot_home()
                with self.assertRaisesRegex(kit.Refusal, "not owned"):
                    kit.plan(self.home, self.source)
                self.assertEqual(self.snapshot_home(), before)
                destination.unlink()

    def assert_historical_inventory_cannot_claim_new_activation_block(self, seed):
        target = seed()
        path = target / ".installation/manifest.json"
        manifest = json.loads(path.read_text())
        manifest["activation"]["config.toml"]["inserted"] = kit.blocks(target)["config.toml"]
        path.write_text(json.dumps(manifest))
        before = self.snapshot_home()
        for uninstall in (False, True):
            with self.subTest(uninstall=uninstall), self.assertRaisesRegex(kit.Refusal, "unexpected managed block"):
                kit.plan(self.home, self.source, uninstall=uninstall)
            self.assertEqual(self.snapshot_home(), before)

    def test_historical_inventory_cannot_claim_new_activation_block(self):
        self.assert_historical_inventory_cannot_claim_new_activation_block(self.seed_engineering)

    def test_swarm_inventory_cannot_claim_new_activation_block(self):
        self.assert_historical_inventory_cannot_claim_new_activation_block(self.seed_swarm)

    def test_historical_inventory_cannot_claim_new_agents_gateway(self):
        target = self.seed_engineering()
        path = target / ".installation/manifest.json"
        manifest = json.loads(path.read_text())
        manifest["activation"]["AGENTS.md"]["inserted"] = kit.blocks(target)["AGENTS.md"]
        path.write_text(json.dumps(manifest))
        before = self.snapshot_home()
        for uninstall in (False, True):
            with self.subTest(uninstall=uninstall), self.assertRaisesRegex(kit.Refusal, "unexpected managed block"):
                kit.plan(self.home, self.source, uninstall=uninstall)
            self.assertEqual(self.snapshot_home(), before)

    def test_old21_inventory_cannot_claim_current_initial_astra_gateway(self):
        target = self.seed_old21()
        path = target / ".installation/manifest.json"
        manifest = json.loads(path.read_text())
        manifest["activation"]["AGENTS.md"]["inserted"] = kit.blocks(target)["AGENTS.md"]
        path.write_text(json.dumps(manifest))
        before = self.snapshot_home()
        for uninstall in (False, True):
            with self.subTest(uninstall=uninstall), self.assertRaisesRegex(kit.Refusal, "unexpected managed block"):
                kit.plan(self.home, self.source, uninstall=uninstall)
            self.assertEqual(self.snapshot_home(), before)

    def test_old21_upgrade_refuses_personal_initial_role(self):
        self.seed_old21()
        self.config.write_bytes(self.config.read_bytes() +
                                b'\n[agents.astra_initial]\nconfig_file = "personal.toml"\n')
        before = self.snapshot_home()
        with self.assertRaisesRegex(kit.Refusal, "astra_initial"):
            kit.plan(self.home, self.source)
        self.assertEqual(self.snapshot_home(), before)

    def test_old21_upgrade_refuses_unowned_initial_agent_file(self):
        target = self.seed_old21()
        destination = target / "agents/astra_initial.toml"
        destination.write_bytes((self.source / "agents/astra_initial.toml").read_bytes())
        before = self.snapshot_home()
        with self.assertRaisesRegex(kit.Refusal, "not owned"):
            kit.plan(self.home, self.source)
        self.assertEqual(self.snapshot_home(), before)

    def test_roundtrip_exact_bytes_and_modes(self):
        self.activate()
        loaded = kit.parse_toml(self.config.read_bytes(), self.config)
        self.assertEqual(loaded["model"], "primary")
        self.assertEqual(loaded["model_reasoning_effort"], "ultra")
        self.assertEqual(set(loaded["agents"]), set(kit.ROLES))
        self.assertNotIn("subagent_model", loaded)
        kit.apply(kit.plan(self.home, self.source, uninstall=True))
        self.assert_original()
        self.assertTrue((self.home / "delegation-kit" / "policy.md").exists())
        self.assertTrue(list((self.home / "delegation-kit" / ".installation" / "backups").rglob("config.toml")))

    def test_preserves_intervening_unrelated_edits(self):
        self.activate()
        self.agents.write_bytes(b"Added before.\n" + self.agents.read_bytes() + b"Added after.\n")
        self.config.write_bytes(b"# user note\n" + self.config.read_bytes() + b"\n[history]\npersistence = \"save-all\"\n")
        kit.apply(kit.plan(self.home, self.source, uninstall=True))
        self.assertEqual(self.agents.read_bytes(), b"Added before.\n" + self.original[self.agents].data + b"Added after.\n")
        self.assertEqual(self.config.read_bytes(), b"# user note\n" + self.original[self.config].data + b"\n[history]\npersistence = \"save-all\"\n")

    def test_idempotent_install_disable_and_reactivation(self):
        self.activate()
        self.assertEqual(kit.plan(self.home, self.source), [])
        kit.apply(kit.plan(self.home, self.source, uninstall=True))
        self.assertEqual(kit.plan(self.home, self.source, uninstall=True), [])
        self.activate()
        self.assertEqual(kit.plan(self.home, self.source), [])

    def test_source_provenance_refreshes_for_identical_relocated_bundle(self):
        self.activate()
        target = self.home / "delegation-kit"
        manifest_path = target / ".installation/manifest.json"
        original_manifest = json.loads(manifest_path.read_text())
        self.assertEqual(original_manifest["source_directory"], str(self.source.absolute()))
        globals_before = {path: kit.read_state(path) for path in (self.agents, self.config)}
        relocated = self.root / "relocated source"
        self.source.rename(relocated)

        changes = kit.plan(self.home, relocated)
        self.assertTrue(changes)
        kit.apply(changes)
        updated = json.loads(manifest_path.read_text())
        self.assertEqual(updated["source_directory"], str(relocated.absolute()))
        self.assertEqual(updated["bundle_digests"], original_manifest["bundle_digests"])
        self.assertEqual({path: kit.read_state(path) for path in globals_before}, globals_before)
        self.assertEqual(kit.plan(self.home, relocated), [])

    def test_current_manifest_without_source_provenance_upgrades(self):
        self.activate()
        manifest_path = self.home / "delegation-kit/.installation/manifest.json"
        manifest = json.loads(manifest_path.read_text())
        manifest.pop("source_directory")
        manifest_path.write_text(json.dumps(manifest))
        globals_before = {path: kit.read_state(path) for path in (self.agents, self.config)}

        self.activate()
        updated = json.loads(manifest_path.read_text())
        self.assertEqual(updated["source_directory"], str(self.source.absolute()))
        self.assertEqual(updated["bundle_digests"], manifest["bundle_digests"])
        self.assertEqual({path: kit.read_state(path) for path in globals_before}, globals_before)
        self.assertEqual(kit.plan(self.home, self.source), [])

    def test_installed_copy_reinstall_and_disable_preserve_source_provenance(self):
        self.activate()
        target = self.home / "delegation-kit"
        manifest_path = target / ".installation/manifest.json"
        self.assertEqual(kit.plan(self.home, target), [])

        kit.apply(kit.plan(self.home, target, uninstall=True))
        disabled = json.loads(manifest_path.read_text())
        self.assertFalse(disabled["active"])
        self.assertEqual(disabled["source_directory"], str(self.source.absolute()))
        kit.apply(kit.plan(self.home, target))
        reactivated = json.loads(manifest_path.read_text())
        self.assertTrue(reactivated["active"])
        self.assertEqual(reactivated["source_directory"], str(self.source.absolute()))
        self.assertEqual(kit.plan(self.home, target), [])

    def test_installed_copy_cannot_invent_missing_source_provenance(self):
        self.activate()
        target = self.home / "delegation-kit"
        manifest_path = target / ".installation/manifest.json"
        manifest = json.loads(manifest_path.read_text())
        manifest.pop("source_directory")
        manifest_path.write_text(json.dumps(manifest))

        kit.apply(kit.plan(self.home, target))
        self.assertNotIn("source_directory", json.loads(manifest_path.read_text()))
        self.assertEqual(kit.plan(self.home, target), [])

    def test_source_provenance_normalizes_external_and_deployment_aliases(self):
        source_alias = self.source / ".." / self.source.name
        kit.apply(kit.plan(self.home, source_alias))
        target = self.home / "delegation-kit"
        manifest_path = target / ".installation/manifest.json"
        self.assertEqual(json.loads(manifest_path.read_text())["source_directory"], str(self.source.resolve()))
        target_alias = target / ".." / target.name
        self.assertEqual(kit.plan(self.home, target_alias), [])

    def test_malformed_source_provenance_is_refused_without_writes(self):
        self.activate()
        manifest_path = self.home / "delegation-kit/.installation/manifest.json"
        original = manifest_path.read_bytes()
        for value in (None, 42, [], "", "relative/source", "/source\0invalid"):
            with self.subTest(value=value):
                manifest = json.loads(original)
                manifest["source_directory"] = value
                manifest_path.write_text(json.dumps(manifest))
                before = self.snapshot_home()
                for uninstall in (False, True):
                    with self.assertRaises(kit.Refusal):
                        kit.plan(self.home, self.source, uninstall=uninstall)
                    self.assertEqual(self.snapshot_home(), before)
        manifest_path.write_bytes(original)

    def test_absent_globals_removed_only_if_still_empty(self):
        self.agents.unlink()
        self.config.unlink()
        self.activate()
        self.config.write_bytes(self.config.read_bytes() + b"# new user content\n")
        kit.apply(kit.plan(self.home, self.source, uninstall=True))
        self.assertFalse(self.agents.exists())
        self.assertEqual(self.config.read_bytes(), b"# new user content\n")

    def test_preflight_refuses_override_conflicts_and_corrupt_toml(self):
        cases = (
            ("AGENTS.override.md", b"This suppresses AGENTS.md\n"),
            ("config.toml", b"[agents.luna_worker]\nmodel = 'mine'\n"),
            ("config.toml", b"[agents.inherited_worker]\nconfig_file = 'personal.toml'\n"),
            ("config.toml", b"[agents.inherited_swarm]\nconfig_file = 'personal.toml'\n"),
            ("config.toml", b"[agents.luna_swarm]\nconfig_file = 'personal.toml'\n"),
            ("config.toml", b"[agents.astra_expert]\nconfig_file = 'personal.toml'\n"),
            ("config.toml", b"not = valid = toml\n"),
            ("config.toml", b"agents = 4\n"),
        )
        for name, data in cases:
            with self.subTest(name=name, data=data):
                path = self.home / name
                before = kit.read_state(path)
                path.write_bytes(data)
                with self.assertRaises(kit.Refusal):
                    kit.plan(self.home, self.source)
                self.assertFalse((self.home / "delegation-kit").exists())
                if before.data is None:
                    path.unlink()
                else:
                    path.write_bytes(before.data)

    def test_modified_or_incomplete_block_refused(self):
        self.activate()
        initial = self.agents.read_bytes()
        self.agents.write_bytes(initial.replace(b"Preserve the user's", b"Ignore the user's"))
        for uninstall in (False, True):
            with self.assertRaises(kit.Refusal):
                kit.plan(self.home, self.source, uninstall)
        self.agents.write_bytes(initial.replace(kit.END.encode(), b""))
        with self.assertRaises(kit.Refusal):
            kit.plan(self.home, self.source, True)

    def test_standalone_internal_names_and_ambiguous_files_refused(self):
        directory = self.home / "agents"
        directory.mkdir()
        path = directory / "different_filename.toml"
        for contents in (
            b'name = "luna_worker"\n',
            b'name = "inherited_worker"\n',
            b'name = "inherited_swarm"\n',
            b'name = "luna_swarm"\n',
            b'name = "astra_expert"\n',
            b'model = "unknown-name"\n',
            b'name = 17\n',
            b'name = invalid = toml\n',
        ):
            with self.subTest(contents=contents):
                path.write_bytes(contents)
                with self.assertRaises(kit.Refusal):
                    kit.plan(self.home, self.source)
                self.assertFalse((self.home / "delegation-kit").exists())
        path.write_bytes(b'name = "unrelated_reviewer"\n')
        self.activate()
        self.assertEqual(path.read_bytes(), b'name = "unrelated_reviewer"\n')

    def test_symlink_sources_and_destinations_refused(self):
        original = self.source / "policy.md"
        original.rename(self.source / "policy-real.md")
        original.symlink_to(self.source / "policy-real.md")
        with self.assertRaises(kit.Refusal):
            kit.plan(self.home, self.source)
        original.unlink()
        (self.source / "policy-real.md").rename(original)
        self.config.rename(self.home / "config-real.toml")
        self.config.symlink_to(self.home / "config-real.toml")
        with self.assertRaises(kit.Refusal):
            kit.plan(self.home, self.source)

    def test_modified_bundle_not_overwritten(self):
        self.activate()
        installed = self.home / "delegation-kit" / "policy.md"
        installed.write_bytes(b"my local changes\n")
        with self.assertRaises(kit.Refusal):
            kit.plan(self.home, self.source)
        self.assertEqual(installed.read_bytes(), b"my local changes\n")

    def test_concurrent_global_edit_is_preserved(self):
        changes = kit.plan(self.home, self.source)
        self.config.write_bytes(b'model = "new choice"\n')
        with self.assertRaises(kit.Refusal):
            kit.apply(changes)
        self.assertEqual(self.config.read_bytes(), b'model = "new choice"\n')
        self.assertFalse((self.home / "delegation-kit").exists())

    def test_every_staging_failure_leaves_globals_and_no_partial_bundle(self):
        changes = kit.plan(self.home, self.source)
        original_stage = kit._stage
        for failing_index in range(1, len(changes) + 1):
            with self.subTest(failing_index=failing_index):
                count = 0

                def fail_once(*arguments):
                    nonlocal count
                    count += 1
                    if count == failing_index:
                        raise OSError("simulated staging write failure")
                    return original_stage(*arguments)

                with mock.patch.object(kit, "_stage", side_effect=fail_once):
                    with self.assertRaises(OSError):
                        kit.apply(changes)
                self.assert_original()
                self.assertFalse((self.home / "delegation-kit").exists())

    def test_every_atomic_replace_failure_rolls_back(self):
        changes = kit.plan(self.home, self.source)
        original_replace = os.replace
        for failing_index in range(1, len(changes) + 1):
            with self.subTest(failing_index=failing_index):
                count = 0

                def fail_once(*arguments):
                    nonlocal count
                    count += 1
                    if count == failing_index:
                        raise OSError("simulated replacement failure")
                    return original_replace(*arguments)

                with mock.patch.object(kit.os, "replace", side_effect=fail_once):
                    with self.assertRaises(OSError):
                        kit.apply(changes)
                self.assert_original()
                self.assertFalse((self.home / "delegation-kit").exists())

    def test_uninstall_failure_rolls_back_active_configuration(self):
        self.activate()
        active = {path: kit.read_state(path) for path in (self.agents, self.config)}
        changes = kit.plan(self.home, self.source, uninstall=True)
        original_replace = os.replace
        count = 0

        def fail_once(*arguments):
            nonlocal count
            count += 1
            if count == 2:
                raise OSError("simulated disable failure")
            return original_replace(*arguments)

        with mock.patch.object(kit.os, "replace", side_effect=fail_once):
            with self.assertRaises(OSError):
                kit.apply(changes)
        for path, state in active.items():
            self.assertEqual(kit.read_state(path), state)
        self.assertEqual(kit.plan(self.home, self.source), [])

    def test_uninstall_failure_restores_newly_created_globals_after_deletion(self):
        self.agents.unlink()
        self.config.unlink()
        self.activate()
        active = {path: kit.read_state(path) for path in (self.agents, self.config)}
        changes = kit.plan(self.home, self.source, uninstall=True)
        original_replace = os.replace
        count = 0

        def fail_once(*arguments):
            nonlocal count
            count += 1
            if count == 1:
                raise OSError("failure after removing globals")
            return original_replace(*arguments)

        with mock.patch.object(kit.os, "replace", side_effect=fail_once):
            with self.assertRaises(OSError):
                kit.apply(changes)
        for path, state in active.items():
            self.assertEqual(kit.read_state(path), state)
        self.assertEqual(kit.plan(self.home, self.source), [])

    def test_preview_is_read_only(self):
        with mock.patch("sys.stdout"):
            self.assertEqual(kit.main(["--home", str(self.home), "--source", str(self.source)]), 0)
        self.assert_original()
        self.assertFalse((self.home / "delegation-kit").exists())


if __name__ == "__main__":
    unittest.main()
