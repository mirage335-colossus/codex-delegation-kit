> Retention note (2026-11-15): this is a historical authored report or prompt. Third-party source payloads, project snapshots and raw execution archives were removed at the user's request. Statements about preserved files, hashes and completed checks describe the original exercise; this checkout no longer supports its exact replay.

# Actual-primary harness design review

2026-11-15 UTC. Bounded design review; **not the main chat's completion review**.
No inference, login, running server, installation, active configuration change,
product execution, D5 inspection or actor intervention occurred in this review.

## Recommendation and authorization

Implement a separate, repository-only **private stdio app-server harness**, with
preparation as its default and an explicit live-preflight operation. Keep
`agent_backend.py` and its no-nested-delegation contract unchanged. The CLI
`exec --ephemeral --json --no-daemon` route remains useful for a coarse startup
probe, but its known event projection makes it the less useful first investment
for a complete lifecycle observation.

The user requested “exercises, refinement, etc, to actually demonstrate equally
extensive research emerging reliably without such follow-through,” after
clarifying that research should emerge, when appropriate, without an explicit
research-only main-chat request. They also said “Keep the changes in the
repository only” and prohibited agent population of curated `_ref/` and
`_appraisal/` without an explicit request. Those instructions support temporary
same-account exercises; they do not authorize active deployment, configuration
or account changes, new user-owned app chats, or product runs. No new approval
is needed merely because the exercise performs inference. A setup requiring
one of those excluded changes must stop at that specific boundary.

A lifecycle smoke test is a prerequisite, not the requested demonstration of
reliable scientific depth. The later substantive exercise still needs ordinary
development input, an autonomous root, independent scientific outcome review,
engineering uptake and preserved failures. The driver must neither supply
missing science nor rescue the root's gate behavior.

## Decisive evidence

- `policy.md`,
  `agents/astra_expert.toml` and `agent_backend.py` are dirty. The actual V5
  snapshot is `source-v5/checkout/`, not the directory containing its manifest.
  The policy, installer and both Astra role bytes were checked against the
  manifest and current checkout: all four match. An initial wrong-path hash
  attempt failed before checking any file; the corrected check supplies these
  results. Freeze and verify the full needed inventory when preparing a run.
- `install.blocks(frozen_root)` generates the main-task gateway and role entries
  without invoking installation. Both Astra files pin `gpt-6-astra` / `ultra`.
  The source policy requires a fresh primary to perform the initial consultation
  before substantive investigation or other dispatch, and a current completion
  review before returning control. Delegated reviewers do not recurse.
- Existing `agent_backend.py` rejects nested delegation, disables native agents
  and uses a bounded delegated prompt. Its request construction is unsuitable
  here. Its private state-directory handling and `execution.py`'s launch fencing,
  process identity, subreaper and owned-cancellation patterns are reusable ideas.
  A new harness must not inherit that backend's strict required-tier field or
  pretend its request is a primary.
- Standalone CLI/package version is `0.163.0`; local help supports private stdio
  app-server transport and `--no-daemon`. The parent's exact-thread metadata
  records primary `gpt-6-astra` / `ultra` using app client
  `0.169.0-alpha.11.1`. Service tier is unobserved. This is selection evidence,
  not provider-side execution attestation or CLI/app parity.

Version-matched official source settles a material observability question:
`exec` JSONL contains genuine collaboration calls with sender/receiver IDs,
prompts, states and return messages, but its schema lacks role/model/effort.
[Exec event definitions](https://raw.githubusercontent.com/openai/codex/rust-v0.163.0/codex-rs/exec/src/exec_events.rs)
establish that limited payload. The
[JSONL projection](https://raw.githubusercontent.com/openai/codex/rust-v0.163.0/codex-rs/exec/src/event_processor_with_jsonl_output.rs)
also drops send-message, followup-task, interrupt-agent and list-agent operations,
ignores model-verification and hook notifications, and strips additional fields
from collaboration items. Consequently a plausible final narrative plus CLI
JSONL cannot establish full role selection, adviser work or follow-through.

A **local static schema generation** succeeded using the installed executable:

```text
bwrap --ro-bind / / --unshare-pid --unshare-ipc --die-with-parent
      --new-session --proc /proc --tmpfs /tmp --
      codex --no-daemon app-server generate-json-schema --experimental --out ...
```

The actual invocation used the absolute CLI path and a Python inspection of
generated files inside the temporary mount. No generated file survived on the
host. The CLI emitted its read-only PATH-alias warning, then exited 0. This was
a static schema operation, not a server or authentication test. It establishes:

- `thread/start`: `ephemeral`, `allowProviderModelFallback`,
  `experimentalRawEvents`, `config`, sandbox/approval and workspace fields.
- Start response: model, reasoning effort, service tier, instruction sources,
  effective sandbox/approval and thread metadata.
- Child `Thread`: `agentRole`, parent and session identifiers, spawn-source
  metadata, model and effort. The schema explicitly labels the latter two
  **configured values, not per-turn execution telemetry**.
- Native `collabAgentToolCall`: requested model/effort in addition to child IDs,
  prompt, status and result states.
- `thread/read(includeTurns)` exists, but describes rollout-history hydration.
  Availability of complete history for live **ephemeral children** remains
  untested. Schema availability does not establish successful execution.

Adding `--unshare-net` to the containment failed before the child with
`Failed to create NETLINK_ROUTE socket: Operation not permitted`: zero schema
assertions ran in that attempt. Removing that optional offline namespace for
the static generator was recorded explicitly; the host stayed read-only.
PID/IPC isolation, private `/proc` and private temporary storage were separately
checked with `/usr/bin/true`, exit 0. This is not evidence that native shell
sandboxing inside the resulting namespace works. Retain the previous failed
overlay probe; do not use overlays, privilege escalation or sandbox bypasses.

## Settled implementation contract

1. **Preparation is offline and non-inferencing.** Create one uniquely owned
   fixture/runtime/evidence area under authorized scratch; reject symlinked or
   reused operation paths. Hash the original task, inputs, frozen source,
   instruction view, safe requested settings and executable identity. Preparation
   must not call `turn/start`, login, model inference or the active app. Preserve
   source-role bytes and the 23-file runtime inventory; this harness is outside
   that deployment inventory.
2. **Deliver the candidate without installing it.** Generate gateway and role
   entries from the frozen installer's `blocks`, pointing at the frozen bundle.
   Use process-local role configuration overrides. Present a namespace-local
   global instruction view replacing only the managed gateway while preserving
   other applicable instruction text; do not silently combine the old installed
   policy and candidate policy. Detect overriding instruction files and fail
   preparation if the effective candidate delivery cannot be established. Do
   not write the real global AGENTS/config files or set the root's base prompt
   to a delegated-owner exemption.
3. **Contain both writes and contamination.** Start from read-only `/`, with
   writable binds only for owned runtime/scratch and the fixture's expressly
   permitted output paths. Add the tested PID/IPC namespace, private `/proc`,
   private temporary storage and parent-death protection. Record the resulting
   mount inventory. A read-only host still exposes evaluator material: mask
   the original study/output trees and active session/history/state/log paths,
   rebinding only frozen permitted inputs. A minimal namespace-local home view
   with explicit read-only runtime/config/rules/auth binds is a viable way to do
   this if it preserves the official authentication route. Keep the real HOME
   and CODEX_HOME values; no blanket writable home and no credential copies.
4. **Preserve authentication and constrain integrations.** Let the official
   runtime read its existing saved authentication read-only. Do not read, hash,
   print or copy credential contents; do not invoke login or refresh as a repair.
   Do not use API-key, provider, account or billing substitutions. Reject inherited
   remote-execution routing overrides. Redirect `sqlite_home`, `log_dir` and
   verified incidental runtime paths to owned storage. Disable hooks and
   unrelated app/MCP/plugin/computer-use integrations using supported per-process
   settings before the first turn; preserve managed restrictions and native
   shell sandboxing. Never persist full config responses, environment dumps or
   account responses. Read-only mounts alone do not prevent socket/RPC effects.
5. **Use a genuinely fresh root.** Start the official executable with
   `--no-daemon app-server --listen stdio://` in the owned containment. Do not use
   daemon/proxy/app-chat APIs or resume/fork another session. Initialize the
   private protocol connection, inspect only safe configuration fields, then
   create one `ephemeral: true` root with explicit local workspace, `approvalPolicy:
   never`, the chosen native sandbox, `model: gpt-6-astra`, effort `ultra`, and
   `allowProviderModelFallback: false`. Verify returned settings before sending
   the original task. Omit service-tier overrides while the selected tier is
   unknown; record inherited/resolved observations without claiming app parity.
   A known model/effort mismatch or reroute is a hold, not permission to retry on
   another model. Missing provider attestation alone is not a blocker.
6. **Observe; do not orchestrate the gates.** Only the actual root dispatches its
   initial and completion advisers. The driver may submit the original task,
   receive notifications, read metadata/history for IDs observed in its own
   root tree, and interrupt its own work at a hard limit. It must not dispatch
   either adviser, send reminders, inject scientific branches, fabricate native
   events or reinterpret a delegated actor as a main chat. Capture raw native
   notifications and safe settings, including role identity, child return,
   commands/research, completion criticism and root dispositions. Synthetic
   protocol fixtures validate parser behavior only.
7. **Fence and clean up owned work.** Keep a durable launch marker before
   dispatch, bounded monotonic deadline and process start/boot identities.
   Unknown launch status forbids automatic replay. On timeout use supported
   `turn/interrupt`, then bounded termination of only owned processes. Mark
   release only after the private PID tree is gone and the launcher is reaped;
   missing heartbeat is insufficient. Do not modify or stop D5. Capture cutoff,
   authentication/setup failure and original behavioral failure distinctly.

## Required checks and smallest next action

First implement preparation plus **non-model** harness checks: input/hash/path
validation; exact candidate gateway and unchanged role pins; allowed mounts;
write-denial outside disposable permitted roots; symlink escape rejection;
timeout, parent death and a detached grandchild; no duplicate dispatch; partial
JSON/error handling. Put any write-denial target in disposable scratch outside
the inner writable mounts, never in active config/auth. Synthetic child events
must carry an explicit synthetic label and never count as behavioral evidence.

Next run a private **setup-only** server check under the same boundary: initialize,
inspect safe configuration and role availability, create/read an ephemeral root,
then close without `turn/start`. This can test incidental startup writes, local
permission resolution and owned cleanup. It does not prove authenticated
inference, child histories, shell execution or gate compliance. If a role/config
cannot be inspected before inference, report that narrow visibility gap and
test it in the live preflight rather than inventing a user-approval prerequisite.

Then permit **one bounded lifecycle preflight** on a tiny, substantive private
code-investigation task, not the scientific-depth evaluation. Proposed exercise
allocation: one root, the two required native adviser threads, at most two
simultaneously open children, 20 minutes total wall time including descendants,
and 30 seconds for cleanup. These are prospective experimental caps, not user
requirements or measured sufficiency; the coordinator must fit them to its
remaining allocation. No additional model episode or retry is implicit. Retain
source pins and any stricter existing limits. Stream bounded evidence and stop
on output/storage limits. Do not advertise a hard aggregate token or memory cap
unless the implementation actually enforces it; record all observable usage and
mark missing child/aggregate accounting explicitly.

Expected success evidence is: fresh root identity; configured selection retained;
actual initial-role call and return before substantive root work; actual
completion-role call on current evidence; visible resolution of feasible review
actions before final; required native tools operating; and verified owned
cleanup. Runtime child metadata must identify the adviser role. If ephemeral
child inspection fails, retain the partial observation and improve the private
adapter's supported native-notification capture before expanding the
exercise. Do not disable ephemerality to obtain better transcripts. Reading a
child's final answer is not proof that all of its source/research checks ran.

Private sqlite/log paths, ephemeral metadata, absent persisted rollout paths,
explicit stdio ownership and namespace exclusion of shared sockets establish
specific local isolation properties. They do not prove absence from every
possible remote account surface. Make the local no-sidebar claim only to the
extent supported by the actual private routing and state observations; do not
launch a user-owned app chat merely to check it. Any discovered remote
registration behavior inconsistent with the task is a hold.

The actual remaining prerequisites are compatible saved-auth startup under the
read-only view; candidate roles and native tools functioning in that client;
complete enough owned-child observations; and cleanup under the chosen boundary.
They are testable setup questions, not reasons to ask the user to reauthorize
exercises. Read-only-auth failure requiring a writable credential store, a
required unsupported pin, or unavoidable shared/app state is a genuine blocker
for that route. A CLI/app version difference, unknown tier, lack of provider-side
attestation, and the failed optional network-namespace probe are limitations,
not independent reasons to abandon this authorized implementation.

## Research scope and limits

This review made **10 explicit web actions**: seven opens (five successful
documents, one incorrect source filename returning 404, one inaccessible GitHub
directory-API URL) and three finds within the already opened configuration page.
All sources were official OpenAI documentation or the official OpenAI repository.
The other successful source pages were version-tagged
[exec entry code](https://raw.githubusercontent.com/openai/codex/rust-v0.163.0/codex-rs/exec/src/lib.rs),
[core configuration](https://raw.githubusercontent.com/openai/codex/rust-v0.163.0/codex-rs/core/src/config/mod.rs),
and the current [configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference).
The latter documents private SQLite state, role concurrency and native sandbox
configuration; current documentation is not evidence that every option works in
the older installed client. Matching source version tags are not reproducible
binary attestation. No further research was needed to choose the adapter: local
schema generation resolved its consequential protocol capability question.
Authenticated startup and native-child behavior remain explicitly untested.

## Implementation follow-up: exact local shapes and corrections

A subsequent bounded request from the implementation owner asked for precise
configuration and protocol shapes. Additional **static** schema inspections and
one filtered `features list` invocation used the same read-only boundary. They
performed no inference, running-server startup, authentication/config dump or
additional web research. Harness source and tests remain the implementation
owner's responsibility.

**Correction to the earlier raw-event suggestion:** the detailed schema marks
`experimentalRawEvents` internal-use-only and describes raw Responses API items,
not richer ordinary collaboration notifications. Omit that field (or leave it
false). Do not capture raw Responses/private reasoning. Use normal native
`item/started` and `item/completed` events and metadata for the owned tree. The
earlier optional suggestion of raw-event capture is withdrawn; schema presence
alone did not establish suitability. Other consequential schema cautions:

- `disabledPluginIds` explicitly **does not yet filter plugin capabilities**.
- `multiAgentMode` is deprecated and ignored; its response is always
  `explicitRequestOnly`. It cannot test or activate native delegation.
- `model/verification.verifications` currently contains only
  `trustedAccessForCyber`. This is not effective-model attestation.
- `instructionSources` is a list of loaded source **paths**, not content hashes,
  expanded instructions or proof of role execution.
- No `thread/subscribe` method appears in generated `ClientRequest`. Do not invent
  that API or resume a child just to obtain a subscription.

The installed parser accepted the following explicit per-process configuration
overrides and reported each false:

```text
features.hooks
features.apps
features.plugins
features.browser_use
features.browser_use_external
features.computer_use
features.image_generation
features.remote_plugin
features.tool_suggest
features.skill_mcp_dependency_install
features.request_permissions_tool
features.memories
```

For CLI each is `-c features.NAME=false`, passed as argument-array elements.
`features.skill_env_var_dependency_prompt` is marked **removed**; it is not an
additional protection. The same invocation reported native defaults
`multi_agent=true`, `code_mode_host=true`, `shell_tool=true`, `unified_exec=true`,
and `code_mode=false`, `multi_agent_v2=false`,
`multi_agent_v2_dynamic_tools=false`. These are observed feature settings, not
proof of every resulting tool or integration boundary. Do not copy the existing
backend's agent-disabling settings into this primary harness.

For MCP reuse the existing backend's safe addressing rule: gather only server
names from effective config and every layer in memory, require
`[A-Za-z0-9_-]+`, and supply JSON dotted overrides
`{"mcp_servers.NAME.enabled": false}` before creating a thread. Reject names
outside the supported addressing rule. Quoted dotted segments are not equivalent
in this protocol. Neither an empty `mcp_servers` table nor `disabledPluginIds`
establishes that merged server definitions disappear. Never persist the full
configuration or layers. Startup feature controls should already be in force
when the setup-only server starts; any unexpected integration startup is evidence
to retain and resolve before inference.

For routing, existing backend evidence supports rejecting an inherited
`CODEX_EXEC_SERVER_URL`, omitting CLI `--remote`/`--code-mode-host`, and selecting
the explicit local environment. Static inspection did not establish an exhaustive
universal remote-routing-disable setting. Keep that limit explicit and verify
the actual environment and native shell behavior in preflight.

Supported JSON-RPC parameter shapes (illustrative placeholder paths):

```json
{
  "initialize": {
    "clientInfo": {"name": "primary-lifecycle-harness", "version": "1"},
    "capabilities": {"experimentalApi": true}
  },
  "config/read": {"cwd": "/PRIVATE/FIXTURE", "includeLayers": true},
  "thread/start": {
    "model": "gpt-6-astra",
    "cwd": "/PRIVATE/FIXTURE",
    "ephemeral": true,
    "allowProviderModelFallback": false,
    "approvalPolicy": "never",
    "sandbox": "read-only",
    "runtimeWorkspaceRoots": ["/PRIVATE/FIXTURE"],
    "environments": [{
      "environmentId": "local",
      "cwd": "/PRIVATE/FIXTURE",
      "runtimeWorkspaceRoots": ["/PRIVATE/FIXTURE"]
    }],
    "config": {"model_reasoning_effort": "ultra"}
  },
  "thread/read": {"threadId": "OWNED_THREAD_ID", "includeTurns": false},
  "turn/start": {
    "threadId": "OWNED_ROOT_ID",
    "input": [{"type": "text", "text": "ORIGINAL_TASK"}],
    "model": "gpt-6-astra",
    "effort": "ultra"
  }
}
```

These are parameter maps, not a single request. Send `initialized` after the
initialize response. Add candidate-role, private-state and integration settings
to the config overrides. Preserve `agents.ROLE.description` and
`agents.ROLE.config_file` from `install.blocks`; the referenced source role TOML
provides its unchanged pins. `ConfigReadResponse.Config` allows additional
properties and has no typed role catalog, so schema acceptance does not prove
all role settings loaded. Do not send `baseInstructions`, `collaborationMode`,
parent/root-turn provenance or project assignment to manufacture a primary.
Omit both `serviceTier` and `serviceTierForTurn` while tier selection is unknown.
Named `permissions` cannot be combined with `sandbox` (or turn `sandboxPolicy`).

The start response supplies configured selection, sandbox/approval, workspace
roots, instruction-source paths and thread metadata. A child `Thread` can expose
`agentRole`, `parentThreadId`, `source.subAgent.thread_spawn.agent_role`, model and
reasoning effort. The latter two are explicitly configured values, not per-turn
telemetry. Verify staged path identities and frozen content separately.

Native event envelopes are:

```text
thread/started: {thread}
item/started: {threadId, turnId, startedAtMs, item}
item/completed: {threadId, turnId, completedAtMs, item}
thread/tokenUsage/updated: {threadId, turnId, tokenUsage}
```

For `item.type=collabAgentToolCall`, retain `id`, `tool`, `senderThreadId`,
`receiverThreadIds`, `agentsStates`, `status`, and optional `prompt`, `model`,
`reasoningEffort`. Tools are `spawnAgent`, `sendInput`, `resumeAgent`, `wait`,
`closeAgent`, `sendMessage`, `followupTask`, `interruptAgent`, `listAgents`.
Call statuses are `inProgress`, `completed`, `failed`, `interrupted`;
`agentsStates[child]` contains status and optional returned message. Child
statuses are `pendingInit`, `running`, `interrupted`, `completed`, `errored`,
`shutdown`, `notFound`.

`thread/read(includeTurns:true)`, `thread/turns/list` with `itemsView:"full"`,
and `thread/items/list` are schema-supported history operations for owned IDs.
Their descriptions concern persisted history; successful ephemeral-child history
retrieval remains untested. A `Turn.itemsView` of `notLoaded` or `summary` is not
complete history. A null `readState` is unavailable durable unread-state metadata,
not an error or proof of missing live thread state. Do not change ephemerality,
invoke internal raw-response feeds, or infer child checks from final prose to
repair missing observations.

## Conditional full-episode wiring

This later design request inspected only the current harness, static
`inputs/tasks/repeat.md`, environment/capability templates, the protocol, project
identity and canonical project instructions, plus preparation/meter code. It did
not inspect prior actor submissions or contact their actors. The design is now
**deferred behind the failed p25 lifecycle smoke**, not an implementation or
launch recommendation while that infrastructure failure remains unresolved.

The smallest prospective extension is one frozen episode profile consumed by
preparation, mounts, overrides, runtime verification and accounting. Preserve
the default smoke profile. Do not scatter inconsistent larger constants across
those paths or add another orchestration framework.

- Freeze the unchanged V5 manifest and byte-identical ordinary repeat request.
  The supplied pump snapshot currently contains **368 files, 5,805,584 bytes**,
  no symlinks and one canonical `AGENTS.md`. The 256-file smoke cap is too small;
  8 MiB already exceeds the source bytes. Admit the exact measured inventory
  plus explicitly frozen envelope files, rather than choosing an arbitrary
  research-sized input allowance. Preserve and deliberately deliver the
  canonical project instructions; do not silently discard them to satisfy the
  smoke fixture's blanket instruction-file rejection.
- Keep pump code, the candidate kit, task and delivered instructions read-only.
  Add an expressly writable episode work area, including `work/research/`,
  disjoint participant scopes and bounded desk-calculation scratch. Request the
  native workspace-write policy with matching roots and no shell network;
  exclude ambient `/tmp`/TMPDIR from native writable roots. The outer mounts
  must still deny project writes. Verify both policies against the profile.
  Runtime state and evaluator evidence stay separate from author work.
- Do **not** use the component `environment-template.md` unchanged: its statement
  that the parent's initial review is satisfied would invalidate this test.
  Remove that exemption and the component dispatch-through-external-root model.
  The fresh primary receives the original task once, candidate main-task
  gateway, preserved project contract and neutral environment notes. It performs
  its own gates and native assignments. Do not inject research branches,
  staffing plans, scorer feedback, prior outcomes or the evaluator-only 89-row /
  48-depth comparison. `prepare_packet.py` also extracts current scientific
  policy and omits `astra_initial`; reuse only its neutral export/sanitization
  logic, not its delegated participant delivery unchanged.
- Preserve the full episode's existing opportunity: 2,000 web items, 100 public
  browser content actions, 80 other acquisition calls, eight elapsed hours,
  12 active identities including the primary and 32 helper assignments.
  The primary occupies one identity; its initial/completion advisers consume
  identities and assignments within those limits. Eleven open native children
  is a conservative implementation of the 12-identity ceiling, with completed
  threads closed through supported native tools when appropriate. Continuation
  in the same scope does not reset assignment identity or allowances. Disclose
  any stricter actual implementation limit before launch; no mid-run increase.
- Replace component `/root` acquisition/dependency directions with a neutral
  service endpoint for exact actor-authored requests and raw responses. A small
  outbox/inbox under the existing episode work/access paths is sufficient; no
  driver-authored scientific continuation or extra model owner is needed.
  The primary handles its own native helpers. The external service may supply
  only requested omitted source dependencies or exact public acquisition
  actions within authority. No source selection, excerpt selection or science
  rescue. Preserve distinct ordinary-dependency and public-acquisition receipts.
- Native public-web availability and browser/connector parity need actual
  capability observations. The existing `functions.exec` web recipe is not
  automatically portable to this CLI's tool surface. Reuse the cooperative
  meter's reserve/finish interface around supported native operations, or relay
  exact requests through the existing service and meter. Freeze the unit mapping
  before dispatch and retain failures/unwrapped calls. Browser tools absent from
  the private client must be honestly unavailable or supplied by that exact
  request relay; do not install/connect a browser or invent native access.
  Access details and the large research allowance remain on-request as required
  by the existing protocol, rather than becoming scientific hints in the first
  task. Deadline and basic permission limits can be stated neutrally upfront.
- Keep standard native root/child events, owned-ID metadata, requested/resolved
  settings, actor work, service receipts and cooperative usage distinct. Count
  gate work in the same episode. Lock the first terminal primary result and
  referenced artifacts before evaluator access; preserve early closure or a
  started interruption without driver prompts to repair it. The fixed scientific
  bar and independent post-lock evaluation remain unchanged. One actual-primary
  episode would establish only that episode's outcome, not replicated reliability.

Existing successful setup s24 establishes configuration/ephemeral metadata and
cleanup, not model access or gate behavior. No full-profile implementation was
performed in this review, and no additional episode is authorized by this note.

## p25 routing failure: bounded disposition

The actual owned p25 evidence records an acknowledged `turn/start`, native
`turn/started`, repeated recoverable errors, then terminal `turn/completed` with
status `failed` and `workspace routing discovery failed`. No assistant output or
tool work was observed; no model-reroute event was recorded. Namespace cleanup
was observed and released. Preserve this **started failed smoke** separately from
s21's known pre-turn startup failure and from any lost-dispatch uncertainty.
No new server, network probe, inference, auth operation or source repair was run
by this reviewer.

Version-matched
[routing source](https://raw.githubusercontent.com/openai/codex/rust-v0.163.0/codex-rs/app-server/src/request_processors/account_processor/workspace_routing.rs)
maps non-401 errors from account-owned `get_accounts_check` to this redacted
category. Missing account ID, missing/duplicate workspace, requirements conflicts,
401, timeout and configuration changes have other categories. This does not
prove a particular network denial, valid authentication or a bad model choice.
The [backend client](https://raw.githubusercontent.com/openai/codex/rust-v0.163.0/codex-rs/backend-client/src/client.rs)
admits network-policy denial, transport/build/route errors, non-success HTTP and
invalid response JSON as possible underlying failures. The null HTTP status in
the emitted stream error does not distinguish them because the routing layer
has already discarded that detail.

The [authentication routing contract](https://raw.githubusercontent.com/openai/codex/rust-v0.163.0/codex-rs/login/src/auth/manager/workspace_routing.rs)
explicitly requires successful discovery before determining independence of
custom destinations. A failed discovery cannot justify skipping the resolver,
changing endpoint/account/provider, reusing another routing owner, or weakening
requirements.

Strict local log projection found two models-manager `error sending request`
entries and five skills-extension EROFS entries. It did not print raw log lines,
URLs, account data or arbitrary error bodies. An allowlisted environment-name
check found no CA/proxy variables to have been lost; XDG_RUNTIME_DIR was present,
and the network-disabled/permission-profile indicators were present and retained
by the harness. This does not establish effective network policy. Restricted
shell networking is a plausible transport explanation, not a measured cause.
The skills write failures are separate observations, not an established routing
cause. No ordinary omitted-file/environment correction is currently supported
by the evidence.

The tool system's `require_escalated` is a supported **permission-request** path,
not a demonstrated repair or a network-only switch. It would request an
unsandboxed outer wrapper; keeping inner bwrap/native protections would not make
the outer permission change nonexistent. This review cannot grant that change
under the existing no-widening launch contract or predict that it fixes an
intentionally redacted transport/policy/HTTP/parse error. It is not inherently
forbidden by the user's repository-only wording, but would need an explicitly
reviewed concrete permission request and retained containment guarantees before
execution. No such request was performed. Under the current no-new-launch and
no-probe instruction, retain actual-primary as blocked infrastructure and advance
the independently authorized source-only V6/component work. Do not manufacture
a user reapproval request merely to continue those independent exercises.

This routing diagnosis used **3 of its separate 12 authorized official-source
web items**, all successful version-tagged source opens. The prior 10 initial
actions and six startup-diagnosis actions remain separate methodology accounting;
none is charged to an author or evaluator episode. Further public research would
not reconstruct the deliberately omitted underlying error from existing p25
evidence, so the remaining allowance was not consumed.

## Prospective one-shot approval request for a p25 repeat

This separate feasibility/authorization review performs no inference, escalation,
network request, preparation or source edit. It answers whether a concrete
request can be submitted through the now-explicit automatic approval review.
**Yes: permission to prepare and ask is supported; approval to execute and
expected success are separate questions.** The earlier no-launch disposition
was correct for that assignment. It is not evidence of a permanent prohibition
on using the supported permission-request mechanism.

Read-only checks found that the current harness, official launcher/native binary,
p25 task and fixture still match p25's frozen hashes. In particular, the driver
hash is `284cd71d972d05d8e40087a53d0c2e0fc0582ca1932c3a0eb23fd3ddabcff79a`
and the V5 manifest hash is
`f665ced6f177b2993b467951e1afc7c43b98effc55463aa67527b765d9208de4`.
`/tmp/cdk-primary-approval-p25-repeat-01` was absent at inspection. No credential
content or account data was inspected. This review reuses existing official
source findings and consumes **zero additional web items**.

The user continues to authorize exercises while prohibiting active installation,
global configuration and account/provider changes. Asking the platform to approve
this exact contained command is compatible with that scope. The redacted p25
error does not establish a specific managed rejection; conversely it does not
justify declaring the cause network-only. The request must openly identify the
outer execution-permission change. It must not change discovery, endpoints,
accounts, model pins or inner containment to evade a denial.

Before requesting execution, the permitted source owner can prepare a fresh
operation under default permissions with this exact command:

```sh
/usr/bin/python3 -B /home/user/___quick/p/_cur/codex-delegation-kit/studies/autonomous-scientific-depth-2026-11-14/tools/primary_lifecycle.py prepare --directory /tmp/cdk-primary-approval-p25-repeat-01 --task /tmp/cdk-primary-p25/task.txt --fixture /tmp/cdk-primary-p25/fixture
```

Review the produced manifest, generated command and mount plan before requesting
approval. Confirm task/fixture/V5 and executable hashes against p25; allow only
new operation-path substitutions and fresh private runtime state. Reuse the
existing applicable independent code acceptance and non-model checks while bytes
remain unchanged. Do not rerun p25 or reuse its launch/dispatch fences. If the
fresh path is already occupied, stop rather than overwrite it.

The concrete proposed `exec_command` arguments are:

```json
{
  "cmd": "/usr/bin/python3 -B /home/user/___quick/p/_cur/codex-delegation-kit/studies/autonomous-scientific-depth-2026-11-14/tools/primary_lifecycle.py preflight --directory /tmp/cdk-primary-approval-p25-repeat-01 --wall-seconds 1200",
  "workdir": "/home/user/___quick/p/_cur/codex-delegation-kit",
  "login": false,
  "sandbox_permissions": "require_escalated",
  "justification": "Approve one repeat of the already-authorized isolated Codex lifecycle smoke outside the outer execution sandbox? The same-account client retains read-only auth/config, the existing bwrap and native read-only sandbox, private runtime writes, fixed Astra/ultra settings and a 20-minute limit. This tests an unresolved routing failure; it does not change account/provider/routing or presume a network-only cause.",
  "yield_time_ms": 1000,
  "max_output_tokens": 1000
}
```

Omit `prefix_rule`: approval should not create a reusable grant for Python,
Codex or unrelated commands. The review must understand that `require_escalated`
requests an unsandboxed **outer driver**, not a network-only capability. The
verified driver still starts Codex only inside the unchanged read-only-host,
private-home/PID/IPC bwrap view. Its allowed durable writes are fresh owned
runtime/scratch/evidence, including private helper temp and installation-ID
binds. Real auth/config/rules remain read-only; no shared daemon, writable home,
active application chat, installation or source write is added. Do not manually
unset network/permission indicators or supply proxy/endpoint overrides.

Two limits must be stated accurately before approval. First, the driver issues
no login, refresh or authentication-repair RPC, and never reads/hashes/copies
credential bytes. However, the previously inspected official routing code can
attempt same-owner automatic recovery on 401. A read-only credential mount does
not prove zero refresh attempts. If **all** automatic refresh is absolutely
forbidden, the current client cannot establish that contract; do not request a
launch falsely promising it. Second, p25 already showed the client's built-in
transport retries and HTTPS fallback. This request adds no fallback and keeps
model/provider/account fallback prohibited, but cannot claim those built-in
transport behaviors are disabled.

Retain p25 and classify this as one new methodology smoke, not a scientific
episode or a replay erasing failure. The same task sets a 20-minute total
ceiling, at most two helper assignments/two open children, and 20 public web
items; both mandatory advisers consume that allowance. The driver enforces its
wall deadline and configured open-child limit; assignment/web ceilings remain
cooperative and observable, not claimed runtime interception. Preserve the
32 MiB protocol/evidence limit and 30-second cleanup allocation. No aggregate
token, memory or all-files storage bound is established. Capture standard native
events and own-tree metadata, omit credential/config/account dumps and private
reasoning, and verify namespace release.

Stop conditions are concrete:

- Approval denied/unavailable: do not run, repackage the same request or switch
  account/route. Retain the precise review reason; continue independent work.
- Changed inputs, containment, selected pins, unsupported setup or an explicit
  routing/security restriction: retain a hold without a workaround.
- Same discovery failure: retain the new failed attempt; do not repeat merely
  because approval was granted. A changed error is diagnostic evidence, not
  authority for auth repair or further permission changes.
- Lost dispatch acknowledgement: retain `dispatch_uncertain` and reconcile;
  never automatic replay. Timeout/limit/violation: interrupt only owned work and
  verify cleanup, retaining any overrun or incomplete evidence.
- Assistant/native adviser activity succeeds: assess actual initial ordering,
  completion review and follow-through from the captured events. Success would
  establish this smoke under the approved execution context, not identify the
  sole cause of p25 or establish scientific-depth reliability.

No request was submitted and no approval is implied by this design verdict.
