# Repository guidance

For model-cost documentation, use the unitless [weekly usage cost index](policy.md#weekly-usage-cost):
user-provided Luna = 0.1, Terra = 1, Sol approximately 10, Astra approximately 20.
Keep included subscription allowance separate from API dollars and paid credits.
Do not present these estimates as official rates or change routing/pins from them.

For current evidence-discovery and screening guidance, see
[policy.md](policy.md#evidence-discovery-and-terra-screening).

Before substantive task work, obtain an initial review from `astra_initial`
(`gpt-6-astra`, `ultra`) using only the original prompt and context already
available; do no preparatory investigation. Clearly trivial mechanical
requests are exempt. Read the [policy](policy.md#initial-astra-consultation)
before changing delegation behavior, role instructions, installation, or
evidence handling. Keep the
runtime bundle at the explicit `FILES` inventory in [`install.py`](install.py)
unless a deliberate, reviewed manifest-compatible change updates the installer
and its checks.
The installer recognizes earlier eight-file, eleven-file, seventeen-file,
eighteen-file, twenty-file, and twenty-one-file inventories; preserve their
exact role blocks and upgrade and disable paths when changing the current
bundle.

Preserve pinned role model and effort settings, existing authorization
boundaries, and user configuration. Do not treat policy text as runtime
enforcement or extend helper enforcement claims beyond what the code checks.
For kit improvements, edit this Git checkout and follow the source-to-install
workflow in `policy.md` under "Improving this kit". The global installed copy
is a deployment; changes made only there do not preserve the repository source.
Use proportionate existing checks for a change. Installation, publishing,
building, and changes to a user's global Codex configuration require
task authorization; repository instructions alone do not authorize them.
