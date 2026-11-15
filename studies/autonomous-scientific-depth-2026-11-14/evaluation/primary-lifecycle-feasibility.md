> Retention note (2026-11-15): this is a historical authored report or prompt. Third-party source payloads, project snapshots and raw execution archives were removed at the user's request. Statements about preserved files, hashes and completed checks describe the original exercise; this checkout no longer supports its exact replay.

# Prospective isolated primary lifecycle exercise

Date: 2026-11-14. Status: design only; no model execution, installation, active
configuration edit, app-chat creation, or change to D5. This note examines a
fresh actual primary session, not a delegated owner relabeled as a primary.

## Finding and authorization

The repository has no supported harness that exercises both native main-chat
gates. A bounded standalone CLI exercise is technically plausible, with a
working local read-only mount primitive, but its authenticated startup, native
role execution, event visibility, and incidental state paths have not been
verified together. Do not report it as runnable or completed yet.

This delegated assignment covers the present read-only investigation and this
design artifact; it does not direct this scout to run inference, install the
kit, change active configuration, authenticate a different account, launch app
chats, or modify D5. The root task's existing authorization broadly covers
exercises. Do not infer that the user must separately authorize every model
call, or that a source-only restriction prohibits already-authorized inference.
A later harness may proceed within that existing authorization once the actual
primary selection, compatible safe startup, explicit prospective resource
envelope, and other prerequisites below are resolved. No API-key/account/provider
substitution is implied.

The initial parent-facing metadata surfaces did not expose primary settings.
The later exact-thread local metadata check below records primary
`gpt-6-astra` / `ultra`; this is selected/turn-context metadata, not provider-side
resolution. Service tier remains unobserved. Do not infer it from global
defaults, this scout, role names, or branding, and recheck selection currentness
before a future launch.
Source role files pin `astra_initial` and `astra_expert` to `gpt-6-astra` / `ultra`.
Do not lower those pins to make an experiment start.

## Existing routes and their limits

| Existing route | What it establishes | Why it is insufficient here |
| --- | --- | --- |
| `agent_backend.py` / controller engineering profile | Actual independent app-server inference, bounded private engineering work, settings checks and receipts | Rejects nested delegation, disables `multi_agent` and `agents.enabled`, holds collaboration events, and uses one run-wide model policy. |
| `examples/live_agent.py` | Actual supplied-context inference and controller lifecycle integration | It is not a primary with native pinned advisers. |
| `tests/test_agent_backend.py` | Synthetic delivered instructions and protocol boundaries | No model compliance; the test explicitly expects no Astra instruction in the bounded prompt. |
| `install.py --home PATH` / distribution tests | Disposable installation and primary/role configuration preservation | No agent lifecycle is executed. Do not install merely to investigate this design. |
| `examples/demo.py`, `examples/benchmark.py`, verification replay | Bookkeeping/scheduling simulation or manual answer import | No actual primary or native gate execution. |
| Action-recovery study harness | Bounded delegated engineering actor | Its explicit delegated context exempts the actor from recursive main-chat gates. |

See [backend](../../../agent_backend.py), [controller contract](../../../ORCHESTRATION.md),
[distribution tests](../../../tests/test_distribution.py), and
[reproduction limits](../../../verification/REPRODUCING.md). The historical main
chat described in [engineering verification](../../../verification/engineering.md)
is not a reusable isolated launcher for the current policy.

## Verified local building blocks

Read-only discovery used `/home/user/.local/bin/codex`, resolving to the installed
Node CLI launcher. `codex --version` reported **0.163.0**. Its help confirms:

- `exec` is noninteractive; `--ephemeral` suppresses persisted session files;
  `--json` emits JSONL; `-C`, `-m`, `-c`, sandbox and approval controls are exposed.
- Top-level `--no-daemon` avoids the shared background server. The parser accepts
  `codex --no-daemon exec --help`; actual noninteractive process routing remains
  unobserved.
- `--ignore-user-config` still uses `CODEX_HOME` for authentication. It is not an
  authentication-isolation mechanism and would discard needed role configuration.
- `debug prompt-input` can render model-visible input as JSON; only its help was
  run. Its no-inference startup dependencies and output sensitivity are untested.
- `app-server generate-json-schema --out DIR` exposes a version-specific schema
  generator. Only help was run; no schema files or server were created.
- A narrowly filtered `features list` reported `multi_agent=true`,
  `multi_agent_v2=false`, `multi_agent_v2_dynamic_tools=false`,
  `code_mode_host=true`, `shell_tool=true`, and `unified_exec=true`. These are
  effective feature flags, not proof of a particular model's exposed tools.

Help/feature commands warned that PATH aliases could not be created on the
read-only filesystem. This is observed incidental startup-write pressure, not
evidence that an inference session can initialize unchanged.

`bwrap` **0.12.0** is available. This no-model, no-file-write probe succeeded:

```text
bwrap --ro-bind / / -- /usr/bin/true
exit 0
```

The proposed anonymous copy-on-write overlay primitive failed before the child:

```text
bwrap --ro-bind / / --overlay-src /tmp --tmp-overlay /tmp -- /usr/bin/true
exit 1: Can't make overlay mount ... Invalid argument
```

Do not select that overlay as a working route, install a replacement, escalate
permissions, or weaken the host write boundary to overcome this result. `strace`
was not found by command discovery. No actual credential path or value was read.

## Proposed minimal design

Prefer a separate clone-only harness with a preparation-only default. Keep it
outside the runtime bundle and leave the managed backend's no-nested-delegation
contract intact. Use argument arrays and child-specific environment overrides.
Do not repurpose `HOME`, globally export settings, or use a shared daemon.

1. **Freeze the task and settings.** Use trustworthy current-session metadata or
   an explicit user selection. The exact-thread findings below partially resolve
   this prerequisite; service tier remains unknown and launch-time currentness
   should be checked. Unknown tier telemetry is not an authorization blocker.
   Consider omitting a tier override to preserve the existing CLI preference,
   while explicitly leaving equivalence to the app's tier unverified. Freeze
   source bytes, role pins, original substantive task, constraints, tool/network
   scope, and total time/usage allocation. Include both Astra calls and all
   descendants in that allocation. Confirm that a later model ceiling does not
   conflict with the required roles. The read-only source inspected here had
   concurrent changes in
   `policy.md`, `agent_backend.py`, and `agents/astra_expert.toml`; it is not a
   frozen candidate identity.
2. **Stage a new private fixture.** Use an authorized temporary cwd, not the
   study participant's cwd or another chat. Stage only the original task and
   permitted inputs; exclude participant outputs, evaluator material, D5 state,
   and other actors' reports. Generate candidate activation text from the
   source `install.blocks(source_root)` contract without invoking installation;
   point at the frozen source policy and unchanged role definitions. Preserve
   other applicable requirements. Stage files in scratch only when that setup
   is authorized; no active-home file is rewritten.
3. **Protect host state.** Build on the successful `bwrap --ro-bind / /`
   primitive. Allow writes only to the private fixture and expressly owned
   runtime/evidence directories; mount candidate instruction/config views inside
   that process namespace if needed. Preserve native shell sandboxing as well.
   Do not assume a read-only mount prevents connections to existing sockets:
   use `--no-daemon` and verify no shared daemon is used. An outer write boundary
   does not provide read secrecy or network filtering by itself.
4. **Keep the existing authentication route.** A fresh blank `CODEX_HOME` must
   not be assumed authenticated. The narrower candidate is to let the official
   runtime read its existing saved authentication through a read-only home
   view, while redirecting verified runtime paths into private scratch. The
   repository already uses per-process `sqlite_home` and `log_dir` overrides;
   CLI alias/cache/temp paths still need version-specific verification. Never
   dump or copy personal config/authentication into evidence. If auth refresh or
   another required write hits the read-only home, retain a setup hold. Do not
   make auth writable, copy tokens, switch accounts, or choose API billing as an
   automatic repair. A clean temporary home remains an alternative only when an
   approved same-account authentication mechanism is established separately.
5. **Inspect preparation before inference.** Validate the frozen role files and
   safe settings without printing unrelated configuration. A candidate isolated
   `debug prompt-input` inspection may verify that the root sees the candidate
   main-task gateway and native role definitions; it must itself first pass
   the same no-network/no-model preparation contract. Do not infer that its
   existence guarantees all settings or tools can be inspected. Generate local
   protocol schema only in authorized scratch if needed. Treat catalog entries
   as availability hints, not authenticated model access proof.
6. **Run only after prerequisites and authorization.** The intended invocation
   shape is `codex --no-daemon -a never exec --ephemeral --json -C FIXTURE
   -m SELECTED_PRIMARY -c model_reasoning_effort=SELECTED_EFFORT
   --sandbox read-only -`, with the task on stdin,
   the validated candidate role configuration, permitted tools, and a bounded
   owned process tree. This is a design sketch, not a ready command: quoting,
   state-directory overrides, network policy, root/child event capture, and
   process ownership must be implemented and checked first. A research fixture
   can start read-only; any required output or computation scratch needs exact
   authorized writable scope. Do not substitute `--ignore-rules`, model
   fallback, permission bypass, or a delegated-owner prompt.

Source-only operation means no deployment and no active configuration changes;
it does not prohibit model execution covered by the root task's authorization.
Preserve that authorization's account, model, tool/network and resource limits.
The completion
review must retain its policy-required source inspection and material external
research obligations. If the exercise lacks needed research access, report that
limit; do not silently call a supplied-context reviewer a fully exercised gate.

## What the live observation must distinguish

The launched root must receive a **new main task**. Its first applicable review
must be an actual native `astra_initial` call using original context only, before
substantive source/tool investigation or other dispatch. Do not pre-run that
review in the test driver or tell the root that a parent already performed it.
Its later actual native `astra_expert` call must review the current proposed
stopping decision, and the root must resolve feasible authorized follow-ups
before its final. Advisers remain delegated roles and do not recurse.

Retain the original prompt/input/configuration hashes, safe requested settings,
CLI version, primary and child identifiers, observed ordering, tool/command
results, adviser responses, follow-ups, stop/cutoff status, and original setup
failures. Capture resolved model/effort/tier where the runtime exposes them;
requested pins, model self-identification, and config text are separate evidence.
Missing resolved telemetry alone is not a policy blocker. Mark it unobserved.

CLI JSONL is a supported event stream, but the inspected documentation does not
guarantee complete child transcripts, child effort, or native spawn/return
events for this `exec` path. Validate that coverage in a bounded smoke run before
using it to score lifecycle compliance. If it is insufficient, report partial
visibility; do not reconstruct actual calls from the final narrative. A separate
ephemeral stdio app-server primary might expose richer native events, but that
requires another reviewed adapter and is not the existing controller profile.

Use the outer read-only boundary to prevent host mutations, and verify private
write roots plus all owned descendant release. Before/after checks of safe
configuration files can detect changes, but cannot prove that no other global
path was touched. `--ephemeral` and `--no-daemon` do not by themselves prove
absence from every app/server surface; preserve this limitation until checked.

Score independently: setup, visible gate ordering, requested/resolved settings,
completion follow-through, substantive task outcome, and whole-workflow cost.
A successful smoke test establishes behavior in that run, not that the gates
increase scientific depth or reliability. A later depth comparison needs frozen
matched tasks, independent outcome criteria, complete costs, and original failures.

## Remaining prerequisites

1. Sufficiently current primary-selection evidence and an explicit prospective
   resource envelope within the root task's existing exercise authorization.
   Local metadata now records primary `gpt-6-astra` / `ultra`. Tier remains
   unknown; omitting its override preserves the existing CLI preference rather
   than inventing a setting, but app/CLI tier equivalence remains unverified.
2. Validated same-account authenticated startup with no active-home writes;
   auth refresh must not silently widen this boundary.
3. Source candidate instruction delivery and native roles actually available
   through noninteractive `exec`, with pins unchanged.
4. Adequate child/gate event visibility and verified owned-process cleanup.
5. Required research/tool access and a check of the no-user-owned-app-chat claim.

These are specific unverified setup capabilities, not claims that they are
impossible. No live gate or primary capability assertion was tested in this work.

## Documentation provenance

Five official pages were opened on 2026-11-14, each once through the Codex URL
and once as its redirected Markdown page: ten web items total. No other web
items, provider calls, model catalog requests, login checks, or secret inspection
were performed. Local help is version-specific; current online documentation is
not proof of this installed version's behavior.

- [Non-interactive mode](https://learn.chatgpt.com/docs/non-interactive-mode):
  supports `exec`, explicit permissions, JSONL capture, saved CLI authentication,
  and the limited rollout-file meaning of `--ephemeral`.
- [Subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents):
  supports custom model roles in local clients and instruction-triggered native
  delegation; its CLI usage discussion names interactive sessions. This does
  not verify the particular noninteractive lifecycle above.
- [Authentication](https://learn.chatgpt.com/docs/auth): distinguishes ChatGPT
  subscription authentication from API-key billing and associated access.
  Preserve the user's route; do not treat API keys as an equivalent workaround.
- [Configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference):
  managed requirements constrain configuration; configuration/schema presence
  does not establish permission or effective execution.
- [App-server](https://learn.chatgpt.com/docs/app-server): documents stdio JSON-RPC
  and version-specific schema generation. No server was started here.

## Additional root metadata evidence

The root reports a subsequent narrow, allowlisted environment inspection: only
`CODEX_THREAD_ID` was available; `CODEX_MODEL`, `CODEX_MODEL_REASONING_EFFORT`, and
`CODEX_SERVICE_TIER` were absent. The root then passed that exact own-thread ID
to `read_thread`. Its response supplied thread metadata, status and turn items,
but no primary model, effort or service-tier fields. No settings or
authentication changed. This establishes the limit of those two inspected
metadata surfaces, not the absence of an actual selected primary or the
impossibility of other supported discovery. The tuple was unresolved at that
point; the subsequent bounded local check below partially resolves it without
substituting configured defaults or inferring settings from message content.

## Exact-thread local metadata follow-up

On 2026-11-15 at 01:12:24 UTC, the scout inspected only the supplied root thread
ID `01a1d971-f1dc-7a31-9d36-a2fdb32d4973`. All discovery/query commands ran under
the already-tested `bwrap --ro-bind / / --` boundary with `python3 -B`.
No CLI server, model, login operation, network request, installation or active
configuration change was invoked. D5 was unaffected.

Operations were limited to:

1. Listing `state*.sqlite` filenames directly under `/home/user/.codex` and
   locating a session filename matching the exact supplied UUID. This found
   `state_5.sqlite` and
   `sessions/2026/11/14/rollout-2026-11-14T03-44-45-01a1d971-f1dc-7a31-9d36-a2fdb32d4973.jsonl`.
2. Opening that database using SQLite `mode=ro` and `PRAGMA query_only=ON`;
   inspecting table names and `PRAGMA table_info(threads)` only, then selecting
   `id, model, reasoning_effort, model_provider, cli_version, updated_at_ms,
   rollout_path, history_mode FROM threads WHERE id=?` with the exact UUID.
   No unrelated row, title, preview or message column was selected.
3. Filtering only `turn_context` / `session_meta` record types from that exact
   rollout. Only allowlisted selection fields, timestamps and metadata field
   names were emitted. Message records, instructions, account/user identifier
   values, credentials and personal configuration were not emitted or inspected.
   The initial filter assumed timestamp-first JSON key order and matched zero;
   relaxing that ordering assumption found eleven `turn_context` records. This
   was a metadata-filter correction, not an inference retry.

| Observation | Value | Interpretation |
| --- | --- | --- |
| Exact `threads.model` | `gpt-6-astra` | Locally recorded primary selection |
| Exact `threads.reasoning_effort` | `ultra` | Locally recorded effort |
| Exact `threads.model_provider` | `openai` | Recorded provider name, not per-token attestation |
| Thread `updated_at_ms` | `1794705140377` (2026-11-15T01:12:20.377Z) | Recent thread update; not a model-change timestamp |
| Latest matching `turn_context` | 2026-11-15T00:41:44.447Z, model `gpt-6-astra`, effort `ultra` | Latest inspected turn-context selection; about 31 minutes before inspection |
| Recorded thread client/history | `0.169.0-alpha.11.1` / `paginated` | Differs from the standalone CLI `0.163.0` discovered earlier |
| Service tier | Unobserved | No tier column in `threads`, no allowed tier field in latest context/session metadata, and none in `collaboration_mode.settings` |

The later metadata schema check completed at 01:12:57 UTC. These observations
partially resolve the primary-selection prerequisite, but do not establish
provider-side effective model/effort, an unrecorded later UI change, or a service
tier. Do not infer `default` from an absent field. CLI/client version mismatch
also means the current chat's capabilities cannot be attributed to the older
standalone CLI without a compatible startup check. No whole database or rollout
was copied into evidence; this note retains only the safe findings above.
