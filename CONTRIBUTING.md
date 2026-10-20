# Contributing

`policy.md`, `install.py`, `uninstall.py`, `supervisor.py`, and the six
files in `agents/` are the maintained source. The installed bundle is a copy
of the fixed eleven-file list in `install.py`; `CONTRIBUTING.md`, `tests/`,
and `examples/` remain clone-only resources. Keep the manifest and bundle
version behavior compatible with existing installations. If changing the
bundle list or managed installation format, update its compatibility handling
and focused installer tests together, and explain any required migration.

Make kit improvements in the verified Git checkout, then validate and review
them before installing from that checkout. The installed copy is a deployment,
not the maintained source. Follow the source discovery, authorization, and
preservation workflow in `policy.md` under "Improving this kit". With existing
authorization to improve the active global kit, complete the normal installer
preview/apply workflow; a source-only or no-global-write instruction still
limits the task. Report source revision/dirty state, checks, installation,
commit, and push status separately. Keep source changes available for review
and authorized preservation; installation does not commit or push them.

The optional version-1 manifest field `source_directory` records the last
external bundle source. Keep older manifests without it compatible. It is a
discovery hint, not proof of Git identity or permission to access a source.
Source relocation can require a metadata-only update. Reinstalling from the
deployment or disabling must preserve an existing hint rather than replacing
it with the installed directory; an unknown source remains unknown.

The installer accepts the original eight-file, three-role manifest and migrates
its owned registration block to six roles. Keep active and disabled legacy
installations compatible, preserve unrelated configuration and evidence, and
refuse collisions with unowned files or role registrations. The three inherited
role files deliberately omit model and reasoning-effort selectors; preserve the
original pinned pairs in the other three roles.

Run the existing standard-library test suite from the repository root:

```sh
python3 -B -m unittest discover -s tests -v
```

Installer tests use temporary Codex homes and synthetic configuration
fixtures. Keep fixtures isolated from the real user home and do not invoke a
global install as a test. After changing installation behavior, exercise the
normal preview and apply paths only with an explicitly supplied disposable
home through the existing test suite; do not target the maintainer's Codex
home. For a documentation-only change, review links and commands and use
proportionate checks.

Those disposable-home checks are tests. A separately authorized installation
of the validated change uses the intended real Codex home, preserves its
configuration and history, and checks source/installed manifest parity plus
an unchanged repeat preview.

The optional [`examples/demo.py`](examples/demo.py) demonstrates assignment
evidence using deterministic synthetic data and makes no model calls. It is a
clone-only example, not an installed command or a substitute for the tests.
The `supervisor.py` command interface and evidence schemas are documented in
its `--help` output and in [`policy.md`](policy.md#evidence-and-routing).

Changes to `policy.md` and role prompts affect user-visible operating
instructions. Keep them consistent, preserve the configured model/effort
pairs, and distinguish behavioral guidance from checks that the helper code
actually enforces. Do not publish, create a release, or change a remote as an
implicit part of contributing.
