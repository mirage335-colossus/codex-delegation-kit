# Repository guidance

Read [`policy.md`](policy.md) before changing delegation behavior, role
instructions, installation, or evidence handling. Keep the runtime bundle at
the explicit `FILES` inventory in [`install.py`](install.py) unless a deliberate,
reviewed manifest-compatible change updates the installer and its checks.
The installer recognizes earlier eight-file, eleven-file, seventeen-file,
eighteen-file, and twenty-file inventories; preserve their exact role blocks
and upgrade and disable paths when changing the current bundle.

Preserve pinned role model and effort settings, existing authorization
boundaries, and user configuration. Do not treat policy text as runtime
enforcement or extend helper enforcement claims beyond what the code checks.
For kit improvements, edit this Git checkout and follow the source-to-install
workflow in `policy.md` under "Improving this kit". The global installed copy
is a deployment; changes made only there do not preserve the repository source.
Use proportionate existing checks for a change. Installation, publishing,
building, and changes to a user's global Codex configuration require
task authorization; repository instructions alone do not authorize them.
