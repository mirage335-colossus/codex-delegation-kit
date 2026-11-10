# Action recovery harness

`harness.py` runs one operation at a time against an immutable copy of the
selected version's `agent_backend.py`. The source fixture, private workspace,
and owned execution records are siblings under `/tmp/action-recovery-runs/`;
the backend rejects a workspace that contains its operation records.

The smoke fixture authorizes one edit to `answer.py` and one unittest command.
The runner fixes the requested settings to Luna, high effort, default service
tier, engineering profile, never approval, workspace-write sandbox, disabled
network, and no nested delegation. It records the generated developer
instructions and their hash before any model turn.

Prepare a per-run source/request fixture without invoking a model:

```sh
python3 -B studies/action-recovery-2026-11-09/harness.py prepare --run-id smoke-a
```

For a supplied participant fixture, pass its directory or registered name,
the case task file, owned write paths, and each required acceptance command:

```sh
python3 -B studies/action-recovery-2026-11-09/harness.py prepare \
  --run-id case-a \
  --workspace-template participant \
  --task-file TASK.md \
  --write-scope src/ \
  --acceptance-command 'python3 -B -m unittest discover -s tests' \
  --role owner
```

Repeat `--write-scope` or pass one JSON list. An empty list yields a scratch-only
write scope. Repeat `--acceptance-command` for supported local Python scripts,
modules, or inline `-c` expressions. `--prompt-file` is optional; the shared delegated-task
preamble is added whether or not one is provided.

The delivered instructions authorize read-only inspection of the workspace and
read-only source fixture, task-required edits within the owned paths, local
task-authorized generation and diagnostics within those paths or scratch, and
the listed acceptance commands. They explain that the main task's initial
review is already complete, the gate is not recursive for delegated work, and
the coordinator handles independent patch review/acceptance after handoff. The
main owner handles any applicable completion review. Network access, background
work, and nested delegation remain prohibited.

After explicit authorization, launch and monitor that same operation, then
collect only after `execution.observe` reports `released: true`:

```sh
python3 -B studies/action-recovery-2026-11-09/harness.py run --run-id smoke-a
python3 -B studies/action-recovery-2026-11-09/harness.py collect --run-id smoke-a
```

`run` uses a durable launch marker and will only observe an existing operation
if called again; it never relaunches a model turn. An unverified release keeps
collection on hold. The collection artifact preserves the backend result,
settings, usage, commands, file-change report, raw stdout/stderr (base64 and
hash), workspace before/after hashes, and a text diff/hash of actual changes.
This is a source-behavior study harness, not an acceptance grader or controller.
