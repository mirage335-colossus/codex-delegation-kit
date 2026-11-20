# Install personal Codex preferences with an agent

Give this file and the request below to an agent with access to the machine
that runs your Codex chats.

> Follow `install-agents.md` and install the task follow-up preference for my
> personal Codex chats.

To set it yourself, paste the [task follow-up preference](#task-follow-up-preference)
into your personal `AGENTS.md` in **Settings → Personalization** for the selected
machine. If a nonempty `AGENTS.override.md` is active, edit that file as
described below. Start a fresh Codex chat to load the edited instructions.
[Desktop settings](https://learn.chatgpt.com/docs/app/settings#personalization)

The preference tells Codex when to offer follow-ups and how to format them as
clickable actions in its Desktop replies. On Desktop builds with inline
follow-ups enabled, selecting an action puts its prompt in the composer as a
draft. The inspected build, 26.1111.71704, displays the action label as plain
text when the rollout is off.

ChatGPT's automatic suggestions under a reply are generated separately. The
Desktop composer's Tab predictions use **Settings → General → Composer → Show
predictions**. OpenAI documents an on/off switch for those predictions.
[Composer predictions](https://help.openai.com/en/articles/20001601-composer-predictions-in-codex)

## Instructions for the installing agent

1. Use the host and Codex home for the chats the user wants to configure. On
   that host, use its active `CODEX_HOME` or the default `~/.codex`. For a
   remote Codex chat, check the selected remote machine and its Codex home.
   Install personal guidance in the nonempty `AGENTS.override.md` if present.
   Otherwise, use `AGENTS.md` and create it if needed. Use repository guidance
   only when the user requests repository scope.
   [Instruction discovery](https://learn.chatgpt.com/docs/agent-configuration/agents-md#how-codex-discovers-guidance)
2. Read the destination and insert the Markdown section below in the user's
   personal content. Update an existing copy of the section or a clearly
   identifiable earlier version of this same preference in place. Leave an
   identical installation as is. Preserve unrelated content and keep the edit
   outside tool-managed blocks, including the Codex Global Delegation Kit
   activation block. If other instructions conflict, identify the conflict and
   ask about any consequential choice needed to reconcile it.
3. Change the native **Show predictions** switch only if the user requests
   that change. Prefer the documented UI control for the local desktop app
   when available. If the agent lacks access to that control, report the
   pending switch separately from the instruction-file edit.
4. Read the edited section back, check the scoped diff and verify that the
   active instruction file contains one copy of the preference. Report the
   host, file path, and changes made. In a fresh Codex chat, verify that the
   instruction loads if that check is available. Ask Codex to summarize its
   task follow-up guidance and check that it includes both kinds of
   alternatives. Report instruction loading and observed behavior separately.

## Task follow-up preference

```markdown
## Task follow-ups

Before ending a task, complete the work that is feasible, authorized, and
needed for the requested outcome.

Offer a follow-up only when evidence or a concrete reason for concern points
to a material shortfall in the original outcome and there is a specific
action likely to improve it. State the shortfall, the action, and the expected
benefit. If progress depends on my input, a scope decision, or authorization,
identify what you need.

Offer multiple follow-ups only when I have a meaningful choice between
mutually exclusive approaches or between increasingly extensive versions of
the same work. For conflicting options, state the trade-off that makes them
alternatives. For increasingly extensive options, state the shared work and
what each larger option adds. Combine compatible steps into one follow-up
when they belong together.

End without a follow-up when the task is adequately complete or when only
generic polish, speculative extensions, or unrelated work remain.

In ChatGPT Desktop Codex final replies, format each eligible follow-up as an
unescaped Markdown list item using the inline action directive.
`- :codex-followup[Short action label]{prompt="Complete continuation request"}`
Use a label that makes sense on its own and a prompt that specifies the work
and its scope. Avoid `]` in the label and escape any double quotes inside the
prompt with a backslash. Explain relevant trade-offs next to the actions.
Use ordinary text in clients that do not support inline actions.
```

## Install a similar preference

Use the user's intended scope and verify the supported control for the behavior.
Put guidance about how Codex should work or reply in the applicable `AGENTS.md`
instruction file. For a documented runtime setting, update its existing entry
or add it to the appropriate user or project `config.toml` when the request
authorizes that scope. Verify the key, type, and config layer in the current
reference and validate the edited TOML. For an app-only setting, use its
supported app control. Apply the smallest edit and verify the resulting file
or app setting. If the product exposes no matching control, describe the
nearest supported behavior and get the user's choice before applying it.
[Codex configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference)
