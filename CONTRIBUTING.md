# Contributing

`policy.md`, `install.py`, `uninstall.py`, `supervisor.py`, and the three
files in `agents/` are the maintained source. The installed bundle is a copy
of the fixed eight-file list in `install.py`; `CONTRIBUTING.md`, `tests/`,
and `examples/` remain clone-only resources. Keep the manifest and bundle
version behavior compatible with existing installations. If changing the
bundle list or managed installation format, update its compatibility handling
and focused installer tests together, and explain any required migration.

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

The optional [`examples/demo.py`](examples/demo.py) demonstrates assignment
evidence using deterministic synthetic data and makes no model calls. It is a
clone-only example, not an installed command or a substitute for the tests.
The `supervisor.py` command interface and evidence schemas are documented in
its `--help` output and in [`policy.md`](policy.md#evidence-and-routing-helper).

Changes to `policy.md` and role prompts affect user-visible operating
instructions. Keep them consistent, preserve the configured model/effort
pairs, and distinguish behavioral guidance from checks that the helper code
actually enforces. Do not publish, create a release, or change a remote as an
implicit part of contributing.
