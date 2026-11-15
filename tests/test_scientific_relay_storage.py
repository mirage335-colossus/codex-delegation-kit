"""Offline storage admission checks for the retained relay publication helper."""
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import time
import unittest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "relay_storage_test", ROOT / "studies/autonomous-scientific-depth-2026-11-14/tools/scientific_relay.py")
relay = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(relay)


class RelayStorageTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.repo = self.root / "repo"
        self.repo.mkdir()
        self.git("init", "-q")
        self.response = self.root / "supplied-response"
        self.response.write_bytes(b"synthetic acquired response")
        self.dependency = self.root / "supplied-dependency"
        self.dependency.write_bytes(b"synthetic acquired dependency")

    def git(self, *args):
        return subprocess.run(["git", "-C", str(self.repo), *args], check=True,
                              capture_output=True)

    def packet(self, path, *, dependency=False, closed=False):
        for name in ("support", "relay/control", "relay/inbox", "relay/dependencies"):
            (path / name).mkdir(parents=True, exist_ok=True)
        def put(name, value):
            (path / name).write_text(json.dumps(value))
        put("support/profile.json", {"name": "scientific-v1", "limits": {
            "max_relay_response_bytes": 1024, "max_relay_bytes": 4096}})
        put("support/project-source.json", {"revision": "synthetic"})
        put("relay/inbox/dispatch.json", {"deadline_monotonic": time.monotonic() + 60})
        if closed:
            put("relay/inbox/terminal.json", {"status": "held"})
        (path / "relay/inbox/.service.lock").touch()
        request = {"kind": "dependency" if dependency else "public",
                   "parameters": {"path": "src/sample.c", "purpose": "synthetic test"}}
        put("relay/control/r1.claim.json", {"outbox_sha256": "bound-request",
            "scope_review": "synthetic fixture", "receipt": {
                "request": request, "operations": 1, "web_reservation": None}})
        return path

    def publish(self, packet, *, dependency=False):
        return relay.publish(packet, "r1", self.response, status="returned",
            actual_operations=1, actual_calls=1, request_sha256="bound-request",
            dependency_file=self.dependency if dependency else None)

    def test_ignored_repository_publication_and_external_scratch(self):
        (self.repo / ".gitignore").write_text("/.research-artifacts/\n")
        for destination in (self.repo / ".research-artifacts/case", self.root / "external-case"):
            with self.subTest(destination=destination):
                packet = self.packet(destination, dependency=True)
                result = self.publish(packet, dependency=True)
                self.assertTrue(result["published_to_author"])
                self.assertEqual((packet / "relay/inbox/r1/response.bin").read_bytes(), self.response.read_bytes())
                self.assertEqual((packet / result["dependency"]["path"]).read_bytes(), self.dependency.read_bytes())

    def test_unignored_refusal_preserves_inputs_and_reservation(self):
        packet = self.packet(self.repo / "unignored")
        claim = (packet / "relay/control/r1.claim.json").read_bytes()
        with self.assertRaises(ValueError):
            self.publish(packet)
        self.assertEqual(self.response.read_bytes(), b"synthetic acquired response")
        self.assertEqual((packet / "relay/control/r1.claim.json").read_bytes(), claim)
        self.assertFalse((packet / "relay/control/published.json").exists())
        self.assertFalse((packet / "relay/control/r1.publication").exists())
        self.assertFalse((packet / "relay/inbox/r1").exists())

    def test_each_staged_and_final_payload_requires_exclusion(self):
        packet = self.packet(self.repo / "cache", dependency=True)
        paths = ["relay/control/r1.publication/response/response.bin",
                 "relay/inbox/r1/response.bin",
                 "relay/control/r1.publication/dependency/src/sample.c",
                 "relay/dependencies/r1/src/sample.c"]
        for excluded in paths:
            with self.subTest(unignored=excluded):
                # File patterns leave all ancestors traversable: each negative
                # rule really re-includes its concrete payload.
                (self.repo / ".gitignore").write_text(
                    "/cache/**/*.bin\n/cache/**/*.c\n!/cache/" + excluded + "\n")
                with self.assertRaises(ValueError):
                    self.publish(packet, dependency=True)
                self.assertFalse((packet / "relay/control/r1.publication").exists())
                self.assertFalse((packet / "relay/control/published.json").exists())

    def test_already_tracked_payload_is_not_overwritten(self):
        packet = self.packet(self.repo / ".research-artifacts/case")
        target = packet / "relay/inbox/r1/response.bin"
        target.parent.mkdir()
        target.write_bytes(b"previous tracked evidence")
        self.git("add", str(target.relative_to(self.repo)))
        (self.repo / ".gitignore").write_text("/.research-artifacts/\n")
        with self.assertRaises(ValueError):
            self.publish(packet)
        self.assertEqual(target.read_bytes(), b"previous tracked evidence")

    def test_closed_author_keeps_ignored_late_evidence_without_delivery(self):
        (self.repo / ".gitignore").write_text("/.research-artifacts/\n")
        packet = self.packet(self.repo / ".research-artifacts/case", closed=True)
        result = self.publish(packet)
        self.assertFalse(result["published_to_author"])
        self.assertEqual(result["disposition"], "late_private_audit")
        self.assertEqual((packet / result["audit_path"] / "response.bin").read_bytes(), self.response.read_bytes())
        self.assertFalse((packet / "relay/inbox/r1").exists())
        state = json.loads((packet / "relay/control/published.json").read_text())
        self.assertEqual(state["dispositions"]["r1"]["actual_operations"], 1)


if __name__ == "__main__":
    unittest.main()
