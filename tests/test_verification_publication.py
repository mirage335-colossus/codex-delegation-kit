import json
from pathlib import Path
import tempfile
import unittest

from tools.publish_verification import sanitize, seal, verify


class PublicationTests(unittest.TestCase):
  def setUp(self):
    self.temp = tempfile.TemporaryDirectory()
    self.addCleanup(self.temp.cleanup)
    self.tmp_path = Path(self.temp.name)

  def test_sanitizer_keeps_urls_commits_numbers_and_alias_joins(self):
    tmp_path = self.tmp_path
    root = tmp_path / "verification"
    root.mkdir()
    (root / "one.md").write_text(
        "https://example.org/a/b, commit 4c471cb93702cdc03b5230bfa33372355424b665; turns=17\n"
        "participant 01234567-89ab-cdef-0123-456789abcdef\n",
        encoding="utf-8",
    )
    (root / "two.json").write_text(json.dumps({
        "root_thread_id": "01234567-89ab-cdef-0123-456789abcdef",
        "source_log": "/home/example/.codex/sessions/private.jsonl",
        "turns": 17,
    }), encoding="utf-8")
    changed = sanitize(root)
    one = (root / "one.md").read_text(encoding="utf-8")
    two = json.loads((root / "two.json").read_text(encoding="utf-8"))
    assert changed == 2
    assert "https://example.org/a/b," in one
    assert "4c471cb93702cdc03b5230bfa33372355424b665" in one
    assert "turns=17" in one and two["turns"] == 17
    assert "01234567-89ab" not in one
    assert two["root_thread_id"].startswith("study-id-h")
    assert two["root_thread_id"] in one
    assert "source_log" in two and two["source_log"].startswith("reported-source")

  def test_repository_and_system_paths_become_portable_labels(self):
    root = self.tmp_path / "verification"
    root.mkdir()
    sample = root / "paths.txt"
    sample.write_text(
        "/home/example/checkouts/codex-delegation-kit/verification/item.json "
        "/home/example/checkouts/codex-delegation-kit /dev/full "
        "repo/verification/item.json https://example.org/repo/item.json",
        encoding="utf-8",
    )
    sanitize(root)
    published = sample.read_text(encoding="utf-8")
    assert published == (
        "verification/item.json repository root system-fixture/dev/full "
        "verification/item.json https://example.org/repo/item.json"
    )

  def test_distinct_path_keys_survive_without_merging_observations(self):
    root = self.tmp_path / "verification"
    root.mkdir()
    file = root / "observations.json"
    file.write_text(json.dumps({
        "/tmp/run-abcdef/result.json": {"count": 17},
        "/tmp/run-ghijkl/result.json": {"count": 29},
    }))
    sanitize(root)
    data = json.loads(file.read_text())
    assert len(data) == 2
    assert sorted(v["count"] for v in data.values()) == [17, 29]
    assert all(k.startswith("unbundled-runtime/run-h") for k in data)
    before = file.read_bytes()
    sanitize(root)
    assert file.read_bytes() == before

  def test_new_native_identity_does_not_reuse_existing_public_alias(self):
    root = self.tmp_path / "verification"
    root.mkdir()
    file = root / "identities.txt"
    file.write_text("existing study-id-001; new 01234567-89ab-cdef-0123-456789abcdef")
    sanitize(root)
    before = file.read_text()
    assert before.startswith("existing study-id-001; new study-id-h")
    sanitize(root)
    assert file.read_text() == before

  def test_json_key_collision_fails_before_overwriting_source(self):
    root = self.tmp_path / "verification"
    root.mkdir()
    file = root / "collision.json"
    file.write_text(json.dumps({"/home/example/codex-delegation-kit/a": 1, "a": 2}))
    before = file.read_bytes()
    with self.assertRaisesRegex(ValueError, "merge distinct JSON keys"):
        sanitize(root)
    assert file.read_bytes() == before

  def test_duplicate_original_json_key_is_rejected(self):
    root = self.tmp_path / "verification"
    root.mkdir()
    file = root / "duplicate.json"
    file.write_text('{"observation": 1, "observation": 2}')
    with self.assertRaisesRegex(ValueError, "duplicate JSON key"):
        sanitize(root)

  def test_captured_path_list_sanitizes_every_entry(self):
    root = self.tmp_path / "verification"
    root.mkdir()
    file = root / "environment.json"
    file.write_text(json.dumps({"PATH": "/usr/local/bin:/usr/bin:/bin"}))
    sanitize(root)
    assert json.loads(file.read_text())["PATH"] == (
        "system-fixture/usr/local/bin:system-fixture/usr/bin:system-fixture/bin"
    )
    file.write_text(json.dumps({"PATH": "system-fixture/usr/bin:/bin:system-fixture/usr/games"}))
    sanitize(root)
    assert json.loads(file.read_text())["PATH"] == (
        "system-fixture/usr/bin:system-fixture/bin:system-fixture/usr/games"
    )


  def test_json_log_replacement_and_historical_scope(self):
    tmp_path = self.tmp_path
    root = tmp_path / "verification"
    root.mkdir()
    file = root / "installation.json"
    file.write_text(json.dumps({"source_log": "/tmp/private/run.jsonl", "sha256": "a" * 64}), encoding="utf-8")
    sanitize(root)
    data = json.loads(file.read_text(encoding="utf-8"))
    assert data["source_log"].startswith("reported-source")
    assert data["sha256"] == "a" * 64
    assert data["publication_scope"] == "historical_pre_publication"
    assert "do not validate" in data["publication_note"]

  def test_release_digests_are_historical_but_new_public_manifest_is_not(self):
    root = self.tmp_path / "verification"
    root.mkdir()
    (root / "E1-release.json").write_text(json.dumps({"same_bytes_sha256": "b" * 64}))
    current = {"schema_version": 1, "files": {"sample.txt": "c" * 64}}
    (root / "publication-manifest.json").write_text(json.dumps(current))
    sanitize(root)
    release = json.loads((root / "E1-release.json").read_text())
    assert release["publication_scope"] == "historical_pre_publication"
    assert release["same_bytes_sha256"] == "b" * 64
    assert json.loads((root / "publication-manifest.json").read_text()) == current


  def test_manifest_detects_unexpected_missing_mutated_and_traversal(self):
    tmp_path = self.tmp_path
    root = tmp_path / "verification"
    root.mkdir()
    (root / "evidence.txt").write_text("stable", encoding="utf-8")
    seal(root)
    assert verify(root) == {"files": 1, "repository_recipes": 0}
    (root / "extra.txt").write_text("unexpected", encoding="utf-8")
    with self.assertRaisesRegex(ValueError, "unexpected"):
        verify(root)
    (root / "extra.txt").unlink()
    (root / "evidence.txt").write_text("mutated", encoding="utf-8")
    with self.assertRaisesRegex(ValueError, "mutated"):
        verify(root)
    (root / "evidence.txt").unlink()
    with self.assertRaisesRegex(ValueError, "missing"):
        verify(root)
    with self.assertRaisesRegex(ValueError, "unsafe"):
        seal(root, "../manifest.json")


  def test_manifest_rejects_symlink_escape(self):
    tmp_path = self.tmp_path
    root = tmp_path / "verification"
    root.mkdir()
    outside = tmp_path / "outside.txt"
    outside.write_text("secret", encoding="utf-8")
    (root / "escape.txt").symlink_to(outside)
    with self.assertRaisesRegex(ValueError, "symlink"):
        seal(root)

  def test_manifest_detects_repository_recipe_mutation(self):
    repo = self.tmp_path / "repo"
    root = repo / "verification"
    root.mkdir(parents=True)
    recipes = (
        "tools/publish_verification.py",
        "examples/verification_replay.py",
        "examples/recompute_verification_usage.py",
        "tests/test_verification_publication.py",
        "tests/test_verification_replay.py",
        "tests/test_verification_usage.py",
    )
    for rel in recipes:
        path = repo / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(rel, encoding="utf-8")
    (root / "evidence.txt").write_text("stable", encoding="utf-8")
    seal(root)
    self.assertEqual(verify(root), {"files": 1, "repository_recipes": 6})
    (repo / recipes[0]).write_text("changed", encoding="utf-8")
    with self.assertRaisesRegex(ValueError, "repository recipe mutation"):
        verify(root)


if __name__ == "__main__":
    unittest.main()
