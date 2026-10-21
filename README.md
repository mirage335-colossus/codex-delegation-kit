# Codex delegation kit

This user-level Codex kit provides a focused read-only scout role, a bounded
implementation role, and a strong review/takeover role. It preserves the
primary model and effort selected for the user's chat. Read [`policy.md`](policy.md)
for the full operating guidance, including delegation boundaries, evidence,
review, escalation, and validation.

## Routing and engineering responsibilities

Establish the applicable routing boundary from the user's instructions and
reliable current-session evidence of the selected main model and reasoning
effort. A global default is not evidence of the active chat's settings. Unknown
model context or uncertain eligibility defaults to native inheritance; do not
guess a tier from model version names, availability, price, or historical work.

| Current routing boundary | Scout and bounded worker | Independent review, consequential design, integration, and takeover |
| --- | --- | --- |
| Known high-end selection, with the user's standing mixed-quality preference | Pinned `luna_scout` and `luna_worker` | Pinned `sol_expert`, or the permitted primary in default engineering mode |
| Known low-cost selection, including Luna medium | `inherited_scout` and `inherited_worker` | `inherited_reviewer` |
| Unknown active settings or eligibility | Native inherited roles | Native inherited reviewer |

The three existing pins remain intentional: the Luna roles request
`gpt-6-luna` with `high`; `sol_expert` requests `gpt-6.1-sol` with `ultra`.
High-end routing keeps the quality-oriented strategy: delegate suitable bounded
work and retain consequential ownership and independent review. It does not
automatically maximize agent occupancy. Known low-cost and unknown operation
must use inheritance unless the user explicitly authorizes a scoped exception.
For example, authorizing the pinned expert for one final review does not
authorize pinned workers or later expert execution outside that review.

The inherited role TOMLs omit both `model` and `model_reasoning_effort`. In
inherited operation also omit spawn-time model and effort overrides, and never
select a pinned custom role to obtain inheritance. The documented resolution
uses explicit spawn settings, then agent defaults, then the parent; a custom
role file's explicit selectors take precedence afterward. Weaker spawn values
therefore cannot override a stronger pin. See the official [subagent
configuration guidance](https://learn.chatgpt.com/docs/agent-configuration/subagents).

Omission inherits the parent only when effective agent/profile defaults do not
override it. Keep existing unset global subagent model and effort defaults
unset. If a conflicting effective default is known, preserve unrelated
configuration and report the precise limitation rather than silently edit it
or claim inheritance. With no overriding defaults, a Luna-medium parent is
intended to supply Luna medium to both inherited workers and reviewers. Prove
actual resolution from current-session runtime settings when available;
configuration checks, a role's own model claim, and this example do not prove a
fresh Luna-medium session behaved that way.

The current desktop supports the existing `[agents.<name>]` descriptions and
`config_file` registration form. A fresh session is needed to expose newly
registered inherited role names. If the current native role table does not
expose them, use a supported unpinned native default with the neutral role's
instructions and no model/effort overrides; do not claim a custom role was
loaded. Report any inability to achieve permitted settings rather than use an
excluded pin. Current capability investigation found no documented native
conditional setting that selects roles by parent model tier, or an automatic
cost hierarchy/runtime-enforced ceiling. Exact current-session settings can be
evidence when available; uncertain eligibility still requires inheritance.
No new conditional TOML keys, model ranking, or pricing mechanism is installed.

Engineering responsibilities do not grant model permission. Independent
review, diagnosis, escalation, and takeover stay within the current routing
boundary through repairs, continuations, and handoffs. A historical Sol owner
must not be resumed under a low-cost or unknown boundary merely to preserve
ownership. Arrange an explicit permitted-owner handoff under the same
assignment, retaining evidence, acceptance criteria, original failures,
repair use, budget, deadline, and ownership history. Use independent permitted
reasoning, narrower experiments, or a precise unresolved issue when necessary;
do not weaken acceptance or automatically upgrade models. A reviewer cannot
approve a patch it produced or substantively repaired.

## Coordination and useful parallelism

Model routing, engineering allocation, coordination mechanism, and concurrency
are independent choices. The latest applicable user delegation instruction can
select coordinator-only or native-only coordination and supersede conflicting
kit or user-level delegation preferences. System, developer, tool, substantive
project, and authorization constraints still apply.

In coordinator-only mode all engineering goes to permitted subagents, including
tiny source lookups, wrappers/tests, builds, artifact analysis, existing-run
monitoring, integration, and review. The primary handles assignment, dispatch,
routing, and status/completion from delegated acceptance evidence. In native-only
mode use native messages/history without the kit helper or new coordination
registries, ledgers, or report files. Authorized engineering artifacts, logs,
reproducers, and task-requested outputs remain allowed.

Choose concurrency for useful accepted progress and quality. When the task or
user calls for aggressive parallelism, keep current native capacity usefully
occupied by real independent assignments and replenish ready work. Do not add
filler, duplicate investigations, or a historical agent-count target. Ready
implementation and regression work must not be starved by broad scouting.
Respect read/write dependencies and machine limits: reasoning-agent capacity
is separate from compiler/test jobs and isolated timing measurements. Assign
one monitor to an existing run and preserve its identity instead of restarting
or duplicating it. No concurrency strategy authorizes different model settings,
changes to the selected primary, higher service tiers, or altered limits.

The policy's [five scheduling rules](policy.md#keep-useful-work-moving-after-scouting)
prioritize quick useful outcomes, dispatch before waiting, reassess slow work,
keep resource restrictions temporary, and use lightweight progress feedback.
Publish stable partial results and split unstarted backlogs when useful.
Required expensive work, validation, and escalation remain necessary; deferral
is not completion. These rules add no fixed time caps, reporting system, or
runtime scheduler.

## Application maintenance and interruptions

For a task that actually authorizes application maintenance, use bounded
reproductions and causal narrowing to identify and correct ordinary defects.
Reduce inputs and execution paths, prefer tiny wrappers around the real helper
or API where useful, compare unchanged and corrected behavior, and check relevant
boundaries and regressions. Keep work within authorized repositories, execution
environments, and services, preserving task-specific access and write limits.
This scope excludes fuzzing campaigns, exploit development, security scanning,
tests targeting external systems, unauthorized access, credential handling,
and security-control changes; it is not blanket authorization for another task.
Authorized cloud runners and CI services, including GitHub Actions, may execute
application checks; that execution is not itself testing an external system.

Use small wrappers and short targeted compiles when they can answer the question.
Do not use broad/full builds, long or expensive cloud/CI jobs, or repeated workflow
runs merely to avoid writing a feasible small reproducer or wrapper. Minimal
checks may run in authorized cloud environments. Larger integration, regression,
platform/toolchain, and performance checks remain appropriate when their
validation or environment requirements justify them.

Cybersecurity notices may have limited logged detail, may never have been shown
to the user, or may be unavailable. Preserve the exact available notice and
attempted operation with the same assignment, partial work, and failure history.
Report absent details honestly; do not guess a reason, assume a mistake, or ask
the user for hidden details they cannot supply. Relevant visible command/run
context may still be requested when genuinely needed.

If the optional helper is selected, its nonempty `notice` field retains exact
accessible text. Label partial text `PARTIAL` and include the verbatim accessible
portion; if no text is accessible, label the evidence limitation `UNAVAILABLE`.
These labels are not fabricated service notices, and legacy exact-text records
remain valid. State unknown required-field details with the existing assignment
or invocation reference; omit unknown optional model/effort values. Preserve the
same hold's operation/scope identity and append new evidence/decisions without
rewriting original events or renaming the blocked operation. An availability
label alone does not establish a wider restriction.
Native-only coordination needs no helper schema or new records.

Determine the affected scope only from actual available evidence. Keep the known
restricted operation blocked, pause dependent work with unclear permission, and
continue demonstrably independent permitted work. Do not retry the operation
through another agent, model, account, renamed assignment, or disguised wording.
Useful aggressive maintenance remains possible within the selected routing and
resource limits: each independent question needs a concrete hypothesis, disjoint
writes and private technical output paths where applicable, and a small
discriminating test. Confirmed fixes can proceed alongside independent inquiries.
Separate paths do not create OS isolation; no new coordination registry is added.

At the next substantive interruption update, state the known blocked operation,
available notice or missing-detail limitation, supported scope and uncertainty,
permitted assignments progressing, concrete results, and any genuinely needed
user-suppliable clarification. A broad audit or full build does not replace
focused diagnosis, and parallel assignments cannot bypass a restriction.
See the policy's [maintenance scope](policy.md#application-maintenance) and
[interruption procedure](policy.md#classify-interruptions-before-implementation-escalation).

## Requirements and model support

Cloning requires Git. The installer and optional evidence helper require Linux
and Python 3.11 or newer; those are the verified runtime prerequisites. They
use only the Python standard library and install no packages or services. The
installer uses Linux filesystem operations and is not documented as portable
to Windows. Use the evidence helper only when its workflow is selected; it is
skipped in native-only operation. Its action names describe responsibilities,
not models, and its legacy `strong` result kind remains a compatibility label.

Check that a selected pinned model/effort is both supported and authorized;
report an unavailable setting instead of silently substituting. The role
instructions govern behavior, while the installer/helper enforce only their
specific checks. These files do not schedule native agents, automatically
recognize every parent tier, or guarantee model-routing enforcement.

## Clone, install, update, and disable

Clone the public repository:

```sh
git clone https://github.com/mirage335-colossus/codex-delegation-kit.git
cd codex-delegation-kit
python3 --version
```

The installer previews changes by default. Review the diff before applying it:

```sh
python3 install.py
python3 install.py --apply
```

To target a separate Codex home, pass `--home` or set `CODEX_HOME` for a
single command. These examples quote paths so spaces are handled as one
argument and do not persist an environment change:

```sh
python3 install.py --home "$HOME/Codex Home"
CODEX_HOME="$HOME/Codex Home" python3 install.py --apply
```

To update, fetch the desired repository revision, inspect the changes, then
run the same dry-run and apply sequence from the updated clone. The installer
refuses to overwrite local edits to managed installed files. Back up or
reconcile those edits before updating. Reinstallation is idempotent.

For requests to improve the delegation kit itself, edit the verified Git clone
first, validate and review the changes, then install from that clone when the
task authorizes updating the active global kit. Follow `policy.md` under
"Improving this kit"; preserve any source-only or no-global-write instruction.
Editing only the installed copy leaves the repository unchanged. Git updates
and global installation are separate steps, and neither automatically commits
or pushes changes. Report source revision/dirty state, validation, installation,
and commit/push status separately; preserve remote-write restrictions.

The installed `.installation/manifest.json` optionally records `source_directory`,
the absolute external bundle source last used by the installer. Verify that
candidate is still the intended Git checkout with its development files before
using it. It may be missing in an older installation, moved, or an unpacked
bundle; it is not proof of Git identity, authorization, or remote state. Use an
explicit current user source when supplied, and resolve a missing or ambiguous
source rather than falling back to installed-only edits. Installing from a new
source path refreshes this hint even when bundle bytes are unchanged. Running
the installed utility or disabling preserves the existing hint, including an
unknown source. This metadata does not make Git-to-global synchronization
automatic.

Updates from the original eight-file bundle migrate its three managed role
registrations to six and add the inherited role files. Active and disabled
installations are supported. The installer preserves unrelated configuration
and retained evidence, and refuses conflicting registrations or unowned files
at the new role paths.

Preview disabling, then apply it:

```sh
kit_home="${CODEX_HOME:-$HOME/.codex}"
# If installation used --home, set kit_home to that same path first.
python3 "$kit_home/delegation-kit/uninstall.py" --home "$kit_home"
python3 "$kit_home/delegation-kit/uninstall.py" --home "$kit_home" --apply
```

The default destination is `$CODEX_HOME/delegation-kit`, where `CODEX_HOME`
defaults to `~/.codex`. Disable removes only the kit's marked activation blocks
from global `AGENTS.md` and `config.toml`. It retains the installed bundle,
backups, and task evidence; it does not remove or restore unrelated settings,
project configuration, or local edits. Review the preview and preserve any
needed files before making separate cleanup decisions. Start a fresh Codex
session after installing, updating role instructions, or disabling: existing
sessions may retain instructions already loaded.

The runtime install contains exactly eleven files: this README, `policy.md`,
`supervisor.py`, `install.py`, `uninstall.py`, and six role TOML files in
`agents/`: the three pinned roles and three selector-free inherited roles.
`CONTRIBUTING.md`, `tests/`, and `examples/` are clone-only development
resources and are not copied into the installed bundle. The policy governs
agent behavior; the installer and evidence helper enforce only their specific
checks. Markdown instructions are not a permission boundary or a runtime
scheduler, and the helpers do not enforce every policy requirement.

## Development (source checkout)

Read `CONTRIBUTING.md` in the clone for development and compatibility guidance.
From the repository root, run the isolated standard-library checks and optional
synthetic helper examples:

```sh
python3 -B -m unittest discover -s tests -v
python3 -B examples/demo.py
```

The examples make no model calls and do not prove live routing or model quality.
These development resources are available in the source checkout only.

## License

Author and CC0 affirmer: **mirage335**.

This repository is dedicated to the public domain under
[CC0 1.0 Universal](https://creativecommons.org/publicdomain/zero/1.0/).
The full `LICENSE` text is included in the source checkout; it is clone-only
and is not copied into the installed eleven-file runtime bundle.
