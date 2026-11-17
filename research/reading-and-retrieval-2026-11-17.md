# Comprehensive reading in ChatGPT and modern coding agents

Research date: November 17, 2026. Repository baseline:
`be8021debb489d4d2045edd7e4baad70e45dafbe`.

The reported improvement has a credible technical basis. Modern coding agents
can acquire larger bodies of evidence, use them more effectively, and sustain
investigations across many tool calls and context windows. Compared with the
built-in Knowledge path of early Custom GPTs, repository agents also offer much
more explicit access to source and feedback from execution. There is unusually
direct first-party support for less prompting being necessary to obtain
appropriate reading and verification from GPT-6 Astra. However, public evidence
does not establish that all the named models routinely read entire repositories,
or that retrieval-augmented generation has disappeared. The user's clarified
observation concerns very large amounts of repeated, chiefly cached Luna input;
that is consistent with useful sustained access to substantial source context.

The practical advance is **more capable, persistent evidence acquisition and
integration**. It combines substantial reading with search, execution, context
reuse, delegation, and selective revisiting of original material. The behavior
worth protecting is willingness to develop the necessary understanding, including
discovering information the initial query did not anticipate. Token consumption
alone is an inadequate measure of that behavior.

This report documents the evidence and its limits. It proposes a reading
preference for later consideration; it does not change runtime policy,
installation, model pins, or configuration.

A follow-up investigation adds an important historical qualification: the change
also occurred progressively inside ChatGPT's web experience. Contemporaneous
users reported more independent investigation with Deep Research and o3/o4-mini
in 2025, followed by more sustained ordinary Chat execution and visible subagent
activity in 2026. These accounts help identify intermediate steps between early
Knowledge retrieval and current coding agents. They support improved autonomous
evidence gathering more strongly than universal, complete-document reading.

The user's further clarification is more specific than longer investigations:
they remember visible commands increasingly requesting whole files and larger
contiguous excerpts, with reversals along the way. That observation concerns
the agent's choice of reading scope. It should be preserved separately from
source counts, execution time, and overall answer quality. Newly located
2025–2026 reports directly address repository exploration and small-read
tendencies, although they do not reconstruct the user's historical sessions.

## What counts as reading

Four different operations are often conflated:

| Operation | What it establishes | What it leaves open |
| --- | --- | --- |
| Search or retrieve a passage | A query found candidate evidence | Whether omitted material changes its meaning |
| Receive complete source text | The source was available in a model context | Whether all relevant relationships were used correctly |
| Read and integrate a coherent body of evidence | The answer accounts for mechanisms, dependencies, assumptions, exceptions, and contradictions | Whether the selected body was sufficiently complete |
| Inspect an entire bounded corpus | Every declared source region was delivered through an observable route | Understanding, retention, and correctness still need outcome evidence |

For code, useful reading often means a complete function or module together with
callers, state transitions, tests, configuration, and relevant design documents.
For scientific work, it means methods, results, assumptions, limitations, and
contrary findings, rather than abstracts or isolated quotations. A large generated
file need not be treated as the same kind of evidence as a carefully authored
research account.

The user's concern is especially compelling for dense, curated knowledge.
Initial queries may fail to reveal concepts the agent has not yet learned;
semantic, broad, and adaptive searches can sometimes discover them.
A few apparently relevant snippets can conceal a different mechanism, a critical
exception, or a better formulation of the problem. Reading the surrounding
account can change the questions themselves. That is a substantive reason for
broad reading, independent of whether the workflow is called RAG.

## The specific behaviors to discourage and encourage

The operational distinction is whether search **expands understanding or fixes
its boundaries prematurely**. A useful excerpt is selected and interpreted in
relation to a sufficiently understood source and task. An inadequate excerpt
may look relevant while omitting the conditions that determine what it means.
Increasing excerpt length helps some failures, but cannot repair every failure
of source selection, coverage, or reasoning.

The following matrix is a proposed behavioral specification derived from the
evidence in this report. It is not a claim that every favorable behavior appeared
in a particular model release, or that every prescription has been experimentally
validated. Historical accounts establish selected changes; studies illuminate
mechanisms; the prescriptions express the user's desired practice.

| Decision | Discourage | Encourage | Observable distinction |
| --- | --- | --- | --- |
| Establishing scope | Treat a redesign, global synthesis, or curated foundation as a lookup for words already present in the prompt. | For bounded authored material, establish broad subject and dependency coverage before committing to a framing. Use an overview to organize substantive reading, not to replace it. | Important concepts absent from the initial query can affect the approach. |
| Choosing queries | Keep searching variations of the initial explanation and interpret similar hits as independent confirmation. | Let inspected evidence introduce new vocabulary, entities, mechanisms, and competing explanations; investigate contrary evidence too. | Later searches have reasons grounded in discoveries, not just different wording. |
| Expanding a hit | Treat a match, abstract, or retrieved paragraph as a complete account of behavior. | Read the enclosing argument or implementation, its definitions and qualifications, and the relevant references or callers. | The conclusion accounts for conditions outside the matching lines. |
| Choosing read size | Use the same short preview regardless of source structure; repeatedly recover avoidable boundary fragments. | Prefer complete useful files or sections when practical. Otherwise use coherent ranges and complete the needed coverage across their boundaries. | Boundaries follow meaning; a fixed line count is not mistaken for adequate understanding. |
| Covering relationships | Collect many passages from the same narrow area and infer system-wide understanding. | Follow state ownership, initialization, callers, consumers, teardown, configuration, tests, or cross-document assumptions as the task requires. | Cross-component relationships are supported, not merely individual facts. |
| Navigating after discovery | Repeatedly search the whole corpus to rediscover a source or step through every match mechanically. | Use known paths, symbols, headings, and locations for direct inspection; batch independent reads when their outputs remain usable. | Navigation adds needed evidence without repeatedly rebuilding the same source map. |
| Handling unsuccessful retrieval | Guess the missing connection or turn a lack of matches into a claim that something is absent. | Examine search scope, alternate terminology, referenced sources, and broader context; distinguish an unsuccessful search from evidence of absence. | Negative claims describe the coverage that supports them. |
| Handling partial output | Regard a successful command as proof its full content reached the model; overlook omitted middle sections or stopped pagination. | Check actual returned content and omission markers, recover material gaps, and distinguish UI clipping from model-input truncation. | Required regions were delivered, or remaining gaps are disclosed. |
| Reusing context | Discard useful foundation material to minimize input, or repeatedly reread it without a purpose. | Reuse available context; revisit originals when new questions, changed source, conflicting evidence, or lost detail make them useful again. | A repeated read can support a new interpretation even when it adds no unique source tokens. |
| Delegating and summarizing | Allow a concise summary to erase qualifications, uncertainty, adverse findings, or the source needed to check a claim. | Preserve consequential relationships, disagreements, scope limits, and recoverable source locations; inspect decisive originals when needed. | The coordinator can distinguish evidence from inference and recover omitted detail. |
| Deciding to act or stop | Stop at the first plausible explanation, or wait for the user to prescribe each next source. | Independently resolve consequential gaps before committing to conclusions or changes, and complete the requested breadth before concluding; report genuine remaining limits. | Completion follows supported understanding of the task, not a query count, token target, or polished answer. |

### When a snippet is sufficient, and when expansion is necessary

A short excerpt can be sufficient for a narrow fact if the source identity and
version are established, the excerpt actually answers that fact, and omitted
context is not needed to interpret its scope. For example, a constant's
declaration may establish its declared value; it does not establish every
effective runtime value if configuration or mutation can override it.

Expansion is especially important when a claim depends on qualifications,
negation, units, preconditions, ordering, side effects, ownership, or interaction
with another component. In a paper, a reported gain may depend on a particular
baseline, workload, operating range, or exclusion. In code, a locally correct
operation may be unsafe because of a caller's lifecycle. Extra surrounding
lines help only if they expose the relevant relationship.

Two separate questions must therefore be answered: **Is each inspected excerpt
adequate to interpret its claim? Have the necessary subjects and relationships
been inspected at all?** Longer snippets can solve the first while leaving the
second untouched. Reading a full file does not answer questions about omitted
files. Conversely, several well-chosen excerpts can establish a specific
cross-file contract when their enclosing context is understood.

For dense, deliberately supplied knowledge, broad reading must not be made
conditional on first finding a keyword that proves each document's relevance.
Learning which concepts matter is part of the requested work. For an unbounded
corpus, searches and structural navigation necessarily select material, but
selection must remain revisable as understanding develops. Explicit user
requests to read a designated collection retain that scope.

### An illustrative code investigation

Suppose the task concerns buffer lifetime during cancellation. This is a
synthetic example, not a diagnosis of the user's code.

An inadequate approach searches for `release` or `cancel`, reads a few matching
lines, and declares the lifetime safe because a release operation is present.
It can miss a pending callback that still holds the buffer or a shutdown path
that bypasses the usual ownership transfer. Even a much longer excerpt around
the release operation can miss that separate consumer.

A stronger approach first establishes the relevant ownership and execution
paths. Search locates declarations and uses; substantive reads cover acquisition,
asynchronous consumers, cancellation, and teardown, together with pertinent
tests and configuration. Discovering another queue or reference changes the
next read. Complete small files can make this easier; larger modules may require
several coherent sections. Any claim of correctness must still follow from the
actual contract and appropriate verification, not from the amount read.

### Evidence and limits behind this specification

The [global-synthesis and retrieval comparisons below](#research-comparisons)
support matching acquisition strategy to the kind of question. The
[reading-related historical accounts](#community-records-that-address-reading-itself)
document exploration differences and small-read tendencies. Neither establishes
an optimal universal snippet length or a measured adoption date for the whole
specification.

There is also concrete harness guidance behind some practices. OpenAI's
February 2026 Codex guide combines proactive context gathering, enough reading
before edits, and batches of independent reads followed by newly discovered
reads. It separately recommends a model-facing output cap with an explicit
middle-omission marker. This illustrates why autonomy, batching, and recovery of
omitted text must work together. It is historical guidance for that model
family, not a new limit or instruction being imposed on current agents.
[Codex prompting guide, exploration and truncation sections](https://developers.openai.com/cookbook/examples/gpt-5/codex_prompting_guide).

The favorable strategy also permits computation. Counting or aggregating all
records can be more reliable with a program whose schema and assumptions are
checked than with selected examples or manual reading of every record. Such a
pass establishes what the computation checked, not that the model understood
every byte. Source coverage and correct interpretation remain separate.

## The historical change from Custom GPT Knowledge to repository agents

Custom GPTs launched in November 2023 with instructions, uploaded knowledge,
and optional capabilities and actions. They were not universally tool-free.
The relevant comparison is their built-in **Knowledge retrieval path**, not
everything a specially configured GPT could do.
[Introducing GPTs, November 6, 2023](https://openai.com/index/introducing-gpts/).

The former official Knowledge help article now redirects. A June 3, 2024
community post preserves a contemporaneous quotation describing upload-time
chunking and embeddings, followed by either semantic search for relevant chunks
or document review using complete short documents and excerpts from larger
ones. This is a quoted historical account, not an independently recovered
official archive. In particular, the separate Assistants API chunk settings
quoted in that discussion must not be assigned to Custom GPT Knowledge.
[Contemporaneous quotation of Knowledge documentation](https://community.openai.com/t/file-search-pricing-retreive-the-docs-info/793834).

Original community reports make the historical problem concrete:

| Date and surface | Reported experience | Supported inference |
| --- | --- | --- |
| November 12, 2023, Custom GPT | Three uploaded PDFs failed to supply an answer to a general question; directing the GPT to page 40 succeeded. Another participant reported an appendix miss. | Available content could require location-specific prompting to become usable evidence. [Original discussion](https://community.openai.com/t/custom-gpt-not-reading-from-uploaded-pdfs/496208) |
| August 15, 2024, Custom GPT | Generic answers despite instructions to use a knowledge CSV; naming the file and asking for search produced the answer. A later participant reported successful automatic retrieval on a 101-row CSV. | Retrieval activation could be unreliable, with successful counterexamples. [Original discussion](https://community.openai.com/t/custom-gpt-only-uses-knowledge-when-specifically-asked-to/908077) |
| March 14, 2025, Custom GPT | Known terms stopped being found despite rephrasing and reuploading; the same documents worked in ordinary ChatGPT. | Product-surface behavior and regressions could matter independently of whether a model could understand the content. [Original discussion](https://community.openai.com/t/issue-with-custom-gpt-not-reading-uploaded-documents-properly/1143059) |
| November 16, 2025, Codex CLI 0.57/0.58 | A user reported 200-line reads and incomplete context despite requesting a full local document. | Explicit file access did not eliminate partial-reading failures. [Original issue 6733](https://github.com/openai/codex/issues/6733) |

These are deliberately selected firsthand reports, not a survey or reproduced
benchmark. They establish that the user's kind of difficulty was reported by
others over time. They cannot identify the backend cause, estimate prevalence,
or demonstrate a controlled same-user migration from Custom GPTs to current
Codex. Parsing, indexing, retrieval activation, excerpt selection, and answer
generation are distinct possible failure points; a generic answer does not
tell us which failed.

Current official Enterprise file-upload documentation acknowledges a related
structural limitation: text is partly placed in context and partly made
searchable, a combination better suited to specific questions than to summarizing
very large documents or comparing multiple large files. This is current
Enterprise guidance, not evidence of the exact 2023 personal-GPT backend.
[Enterprise file handling](https://help.openai.com/en/articles/10029836-optimizing-file-uploads-in-chatgpt-enterprise).

The May 16, 2025 Codex launch documents a different operating environment:
a task has a repository on disk, can read and edit files, execute commands,
and run tests, linters, and type checkers. It also describes reinforcement
learning on real software tasks and iterative test execution. This establishes
that richer source access and feedback predate GPT-6. The later models and
harnesses can improve how effectively those capabilities are used.
[Introducing Codex, historical launch](https://openai.com/index/introducing-codex/).

The consequential change is **control over evidence acquisition**. An agent
with file tools can go from a hit to the surrounding function, inspect its
callers, open related documents, and use a failing test to revisit earlier
assumptions. It need not accept the initial excerpt as its complete view of the
source. This is an interpretation of the documented interfaces, not a guarantee
that every coding agent follows through. Stronger prompting alone cannot
guarantee recovery of source that a particular tool path never returns.

## Visible file reading and an irregular model transition

### The user's observation and the identifiable o3 lineage

The user recalls a progression across Custom GPTs, ordinary ChatGPT, web Codex,
and later desktop Codex: more whole-file reads or larger excerpts; improvement
with an unusually capable o3-related web Codex; a regression after its
replacement; and subsequently much stronger reading with newer harnesses and
the GPT-6 family. This is firsthand recollection recorded on November 17, 2026.
The user does not remember the replacement date, so a nearby documented model
transition must not be presented as the confirmed date of their regression.

The o3-related product has a strong historical match:

| Date | Documented model or capability | Interpretation for this recollection |
| --- | --- | --- |
| May 16, 2025 | Cloud Codex used **codex-1**, an o3 version optimized through software-engineering training. Its environment exposed source files and executable tools. | A concrete match for remembering a distinct o3-derived model in web Codex. Specialization does not establish a larger parameter count. [Contemporaneous Codex system card](https://cdn.openai.com/pdf/8df7697b-c1b2-4222-be00-1fd3298f351d/codex_system_card.pdf) |
| September 15, 2025 | **GPT-5-Codex** became the cloud-task and code-review default. OpenAI described adaptive allocation of thinking and longer work on complex tasks. | A plausible transition to investigate, not a verified explanation of this user's regression. Adaptive allocation can change task behavior without establishing a change in model size. [Historical announcement](https://openai.com/index/introducing-upgrades-to-codex/) |
| November 19, 2025 | **GPT-5.1-Codex-Max** introduced native training for operating across multiple context windows with compaction, supporting cumulative work over millions of tokens. | A documented intermediate advance in sustained source use before GPT-6. It concerns a task's trajectory, not millions of unique source tokens necessarily read. [Historical announcement](https://openai.com/index/gpt-5-1-codex-max/) |
| September 2026 | Astra guidance explicitly described less need to prescribe which files to read. | Supports a later improvement in independent reading choices, as discussed below. It does not quantify whole-file reading frequency. [Astra prompting guidance](https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra) |

The May 2025 launch also introduced an o4-mini-derived **codex-mini-latest**
for the CLI. That contemporaneous smaller model should not be mistaken for
evidence that cloud codex-1 was replaced by it.
[Launch, Updates to Codex CLI](https://openai.com/index/introducing-codex/).

No authoritative total or active parameter counts supporting the proposed
codex-1-to-successor size comparison or Astra's size-based explanation were
found in the inspected official material. The parameter explanation remains a
hypothesis. The observable reading changes can still be studied independently;
model specialization, effort allocation, prompts, tools, and context handling
are other candidate influences.

### Community records that address reading itself

| Date and surface | More specific evidence | What it establishes |
| --- | --- | --- |
| March 2025, ChatGPT Projects and ordinary Chat | A user reported previously successful file tasks suddenly returning only the beginning of long project files, and different behavior in ordinary Chat, while testing 4o and 4.5. | Firsthand testimony of an abrupt source-coverage regression across web surfaces. No matched documents or command trace were published; approximate word counts and inferred backend substitution are not verified limits or model identities. [Original discussion](https://community.openai.com/t/chatgpt-is-unable-to-read-project-files-properly-suspected-to-be-4-turbo-instead-of-4-o/1155234) |
| September 28, 2025, Codex CLI | A commenter described GPT-5 high gathering much more context and thoroughly exploring the repository before its first response, in contrast with earlier models. The surrounding issue compared GPT-5 high favorably with GPT-5-Codex high on difficult codebases. | Direct positive testimony about autonomous exploration depth, with a contemporaneous contrary comparison between models. It supplies no measured coverage or controlled trace. The CLI evidence cannot establish cloud Codex's behavior. [Direct comment](https://github.com/openai/codex/issues/3826#issuecomment-3344406001) |
| January 9, 2026, Codex CLI 0.79.0, GPT-5.2 xhigh | A user reported difficulty reading a 400-line Markdown file; the pasted trace discusses 200 lines and another `sed` range. An OpenAI contributor, after skimming the session, described 200-line reads as a context-conserving model tendency. | This distinguishes read granularity from a universal hard limit. More lines could follow; the public excerpt cannot establish final coverage or isolate model from harness. [Issue and contributor response](https://github.com/openai/codex/issues/8982#issuecomment-3730234528) |

These observations are closer to the user's claim than reports of long answer
generation. They concern what source the agent seeks and how it divides that
source into reads. They also support an irregular progression: improved broad
exploration in one model can coexist with narrower or less effective behavior
in another model offered during the same period. Neither the vendor's aggregate
capability claims nor the passage of time establishes a monotonic reading trend.

The January issue also exposes a disagreement about efficiency: the contributor
emphasized context conservation, while the reporter found the extra attempts
wasteful. Eventual coverage, reading granularity, and the work required to reach
that coverage are separate outcomes. Shorter reads need not mean less total work.

### Requested text, delivered text, and displayed text

Visible commands are material evidence about reading choices. A request for a
whole file or a wider contiguous range differs from asking only for matching
lines. However, the command, returned payload, and interface display are
separate layers. An October 2025 Codex issue provides actual `cat longfile`
transcripts with different visible output lengths; its author then retracted
the interpretation that the agent's input was truncated, identifying the
difference as display-only. That is the author's correction, not an independent
audit of raw model requests.
[Issue 5095 and correction](https://github.com/openai/codex/issues/5095#issuecomment-3393647913).

Likewise, a Python program can load a whole file into a variable without sending
all its contents back to the model. Current ChatGPT documentation confirms that
data analysis can execute Python in a stateful environment with access to
session files, so visible file-processing commands are not exclusive to Codex.
This current capability documentation does not date the historical changes in
read size or establish how a particular Custom GPT accessed its knowledge.
[Data analysis with ChatGPT](https://help.openai.com/en/articles/8437071-data-analysis-with-chatgpt).

The bounded public-source investigation did not establish a dated, general
increase in model-facing file-output allowances, especially for web ChatGPT or
cloud Codex. CLI source cannot establish those services' historical limits.
The better-supported explanation remains a combination of **reading choices,
tool delivery, context retention, and follow-through**. A larger allowed context
can help, while a narrow default reading habit can still constrain what enters
it. Conversely, coherent successive reads can cover a source without one large
tool result.

## How investigation expanded inside ChatGPT itself

The relevant history is not just a migration from Custom GPTs to Codex. A user
could remain in the ChatGPT web interface while the available models, tool
loops, execution time, and presentation of work changed substantially. It is
therefore useful to separate the behavior observed in ordinary Chat from
explicitly selected Deep Research, agent mode, and Work. This distinction does
not dismiss observations of ordinary Chat becoming more agentic: several of
the reports below concern exactly that surface.

### Community observations of improvement and variation

These are original practitioner accounts, selected for identifiable behavior
rather than general enthusiasm. Source counts, elapsed time, and visible
subagents are useful observations, but none alone establishes comprehension.

| Date and reported surface | Firsthand observation | What it contributes and what remains uncertain |
| --- | --- | --- |
| February 6, 2025, Deep Research | An author described a 25-page report using 38 sources, mostly arXiv, after 24 minutes, and preferred it to their previous research service. | Early testimony of extended autonomous investigation. The research mode was explicitly selected; the original prompt and a matching inspectable trace are absent. [Original discussion](https://www.reddit.com/r/ChatGPTPro/comments/1iis4wy/deep_research_is_hands_down_the_best_research/) |
| April 21, 2025, ordinary Chat with o3/o4-mini | Simon Willison contrasted disappointing 2023 assistants with useful current research requiring fewer corrections to search choices. He also supplied full application code and one broad migration request; o4-mini-high reportedly found the replacement library and migration documentation and produced working code. | The clearest experienced-user before-and-after account of reduced supervision. It includes screenshots, conversation links, and a published code change. This investigation could not read the shared ChatGPT transcript or independently run the result; exhaustive documentation reading is not demonstrated. [Original account](https://simonwillison.net/2025/Apr/21/ai-assisted-search/) |
| May 22, 2025, ordinary o3 Chat | A commenter described routine questions and code inquiries as benefiting from a small-scale research workflow, with only a tone customization disclosed. | Supports investigation becoming useful during routine chat. Other participants reported fabricated PDF references and quotations, so activity and reliability must be evaluated separately. [Original discussion](https://www.reddit.com/r/ChatGPTPro/comments/1ksj7tw/what_do_you_guys_use_o3_for/) |
| July 2026, ordinary Chat, GPT-5.6 | A user reported Chat completing lists of ten substantial items over 20–30 minutes. Participants described steering work while it continued and supplying test results. | Closely matches the observation that Chat began behaving like an agent. The thread also reports slower work and worse existing-codebase results; a comment attributing this to a subagent architecture is speculation. No source-reading trace is supplied. [Original discussion](https://www.reddit.com/r/ChatGPT/comments/1uvs8vf/chat_has_started_acting_more_like_an_agent_since/) |
| September 11, 2026, ordinary Chat, GPT-5.6 Sol Extra High | An author reported completing an explicitly specified 1,200-page fetch in 31m46s, with distinct final URLs and content hashes, and corrected their earlier hypothesis of a universal approximately 26-minute limit. | Concrete reported acquisition coverage, not proof that the model received or integrated every page. This was a deliberately demanding test, not an unprompted reading choice. Earlier and later runs also differed in effort/account conditions; the author's routing explanation remains an interpretation of their telemetry. [Original update, post 48](https://community.openai.com/t/gpt-5-6-high-execution-regression-ordinary-chat-went-102m26s-repeated-25-26m-stops-on-same-plus-account-work-still-gets-long-run-handoff/1391943/48) |
| September 22, 2026, ordinary Chat, GPT-6 Pro | A commenter reported independently updating subagent activity controls, a task tracker, and hours of work, explicitly distinguishing the event from Work or Codex and from agents merely described in generated text. | Very close corroboration of the visible-subagent observation. The commenter could not reproduce it in later chats; proposed rollout and routing causes were guesses. This is an account of a UI event, not a verified backend trace. [Direct comment](https://www.reddit.com/r/ChatGPTPro/comments/1wa8hs4/comment/pbdvmmn/) |
| September 29, 2026, Work | A user reported that previously careful file inspection and sustained work had become less reliable and required more correction. | Contrary longitudinal testimony: useful reading can regress independently of a product's advertised capabilities. The author explicitly lacked visibility into the cause. [Original regression report](https://community.openai.com/t/work-quality-regression-observed-in-japan-region-since-september-29/1401796) |

The July post's search metadata specifies July 13; its opened page exposes only
a relative date, so the table conservatively uses the month. The September 22
subagent comment date was checked against its own Reddit timestamp, not the
earlier parent thread. Reports were not reproduced or treated as a population
survey. A promising August 2025 account about a long scientific document could
not be recovered reliably and is excluded from the substantive evidence.

The strongest positive observations concern **less supervision and more
persistent investigation**. The public accounts are considerably weaker on
complete coverage of uploaded documents, and do not provide a matched
longitudinal test of early Custom GPT Knowledge against current Chat. They also
do not establish that the number of searches declined. More extensive reading
can be accompanied by more searches as the agent discovers additional sources.

### Documented changes that plausibly explain the progression

| Milestone | Documented change | Relevance to the observed behavior |
| --- | --- | --- |
| February 2, 2025: Deep Research | A selected research mode used an o3 variant trained with reinforcement learning on browsing and reasoning tasks. It could pursue multiple steps, reconsider its approach, and combine browsing with analysis. | A product explicitly allocated sustained work to investigation. This was an opt-in research workflow, not a new default for every Chat response. [Historical launch](https://openai.com/index/introducing-deep-research/) |
| April 16, 2025: o3/o4-mini in ChatGPT | Reasoning models could combine ChatGPT tools, with training on when and how to use them, including search, file analysis, and Python. | This supplies a documented mechanism for the contemporaneous reports of ordinary chat following evidence with less supervision: tool use was integrated into the reasoning process. [Historical launch](https://openai.com/index/introducing-o3-and-o4-mini/) |
| July 17, 2025: ChatGPT agent | A selected agent mode combined research and computer interaction, with text and visual browsers, a terminal, and API access. | The agent gained additional ways to obtain and process source material when a search result alone was insufficient. Selection of this mode matters when comparing experiences. [Historical launch](https://openai.com/index/introducing-chatgpt-agent/) |
| Current documentation, inspected November 17, 2026 | Work can research, read files, run code, and continue longer tasks. Web Work runs in a hosted environment. Work and Codex have overlapping capabilities; the desktop choices also change presentation and technical detail. | Codex-like behavior in the web product is consistent with documented capability convergence. Similar presentation does not establish identical settings or a shared backend for every ordinary Chat session. [Current product guide](https://learn.chatgpt.com/docs/use-chatgpt) |
| Current subagent controls | Web Work exposes hosted subagent activity. Most intelligence levels require an explicit delegation request; Ultra permits proactive delegation. | Delegation defaults depend on mode and effort. UI availability and autonomous use are separate facts. [Current subagent guidance](https://learn.chatgpt.com/docs/agent-configuration/subagents) |

The Deep Research announcement's April 24, 2025 update also documents automatic
fallback to a lightweight o4-mini version after the original allowance is used.
This is a concrete historical example of the same named feature having different
execution conditions. It does not diagnose any particular community complaint.
[Dated update on the launch page](https://openai.com/index/introducing-deep-research/).

The alignment of the April 2025 release with Willison's report is stronger than
an unexplained claim that a model suddenly became better. It still is not a
controlled causal experiment. In his May 2025 workshop account, Willison
explicitly preferred tool-driven repeated investigation to retrieving material
once and then answering without another opportunity to obtain evidence. This
is a contemporaneous practitioner's explanation of the change, separate from
the vendor's account of its training.
[May 15 workshop account](https://simonwillison.net/2025/May/15/building-on-llms/).

### What these observations add to a reading preference

The consequential behavior to preserve is a continuing cycle: understand the
task, inspect substantive evidence, identify gaps or contradictions, obtain the
needed source, and reconsider the answer. Broader source access, better choices
about tools, and enough execution time can all make that cycle more effective.
The available evidence does not rank their individual contributions.

For the kit, this supports preserving **autonomous follow-through on evidence
gaps** in addition to adequate reading depth. An agent should not need the user
to name each missing file, search phrase, or next reading step. A useful
regression record should distinguish an agent that finds and reads the required
material itself from one that succeeds only after detailed source-specific
coaching. It should also distinguish reading that was attempted but truncated,
reading prevented by a missing tool, and reading abandoned because the agent
decided to answer early. These failures need different remedies.

## What is documented for the current products

### Larger context is real but is not a billion token window

The current API model cards list the following capacities. These are API
specifications, not measurements of the current desktop session's effective
configuration.

| Model | API context window | Maximum API input | Maximum output |
| --- | ---: | ---: | ---: |
| [GPT-6 Astra](https://developers.openai.com/api/docs/models/gpt-6-astra) | 1,050,000 | 922,000 | 128,000 |
| [GPT-6.1 Sol](https://developers.openai.com/api/docs/models/gpt-6.1-sol) | 1,050,000 | 922,000 | 128,000 |
| [GPT-6.1 Terra](https://developers.openai.com/api/docs/models/gpt-6.1-terra) | 1,050,000 | 922,000 | 128,000 |
| [GPT-6 Luna](https://developers.openai.com/api/docs/models/gpt-6-luna) | 1,050,000 | 922,000 | 128,000 |

Sol's model card separately specifies a **500,000-token default in Codex and
ChatGPT Work**, with no additional long-context surcharge for subscription
allowance usage. API capacity must therefore not be substituted for the actual
app default. Nor does available capacity prove that any particular source was
loaded. The named models are documented products; their individual reading
policies and coverage rates are not published by these specification tables.

### Less handholding is supported most directly for Astra

OpenAI's September 11 developer article says Astra can determine the files it
needs to read without a compulsory whole-project review before every edit. It
also says testing and checking increasingly happen without the encouragement
older models needed. This is close to the user's observation, although it is
first-party practical guidance rather than a controlled measurement of file
coverage. The same article warns that Astra can return after an initial
implementation while useful work remains, and recommends explicit completion
conditions. Thus autonomous reading, verification, and persistence do not improve
as one inseparable property.
[Rethinking skills and prompts for GPT-6 Astra](https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra).

The current GPT-6 guide attributes better coherence over long tasks and stronger
instruction following to Astra. It also notes sensitivity to skills and
`AGENTS.md`, possible under-delegation, and testing broader than a small task
requires. It supplies explicit follow-through guidance. These observations
support a changed behavioral balance, not a universal default to exhaustive
reading. They also explain why the same instruction can produce a different
amount of work after a model update.
[Using GPT-6](https://developers.openai.com/api/docs/guides/latest-model).

Sol's launch reports stronger performance on long-horizon software-engineering
and professional-document tasks. These are useful outcome signals, but they do
not isolate the amount of source reading as the cause. Terra and Luna's model
cards establish large-context and tool capability; they supply much less direct
evidence of spontaneous comprehensive reading. Applying Astra's behavioral
claims to all four models would exceed the evidence.
[GPT-6.1 Sol announcement](https://openai.com/index/introducing-gpt-6-1-sol/).

### A harness turns reading into a continuing activity

The published Codex agent loop repeatedly invokes a model, executes requested
tools, appends their results, and continues. Source reading can therefore be
spread across hundreds of steps instead of one initial prompt. The harness also
assembles project instructions and manages context limits. This architecture
was already documented in January 2026; the recent change is not the invention
of tool-assisted reading itself.
[Unrolling the Codex agent loop](https://openai.com/index/unrolling-the-codex-agent-loop/).

Earlier Codex prompting guidance already combined search, file reading,
parallel exploration, sufficient context before edits, and long-running
autonomy. Its GPT-5.3-Codex discussion includes compaction for multi-hour work.
Consequently, a sharp historical story in which old agents could only retrieve
snippets and new agents suddenly acquired reading is too simple. Capability,
reliability, economics, and default choices can improve even when the broad
workflow already exists.
[Codex prompting guide](https://developers.openai.com/cookbook/examples/gpt-5/codex_prompting_guide).

### Compaction and memory extend work without preserving everything verbatim

Current compaction documentation describes reducing the active context while
carrying forward state and reasoning in an opaque compaction item. This permits
longer trajectories; it is not a promise that every original detail remains
available verbatim or is always used correctly.
[Compaction](https://developers.openai.com/api/docs/guides/compaction).

Astra's launch describes another approach: notes across context windows and
search over earlier messages and tool outputs. It identifies losses from
repeated summarization as a motivation. **Availability remains unresolved:** the
launch described an experiment intended to become the default, while the current
configuration reference says `features.context_management.experimental_mode`
is not currently available. A targeted check of current documentation did not
establish a replacement activation path or its use in this desktop session.
Treat this as an announced design, not a verified present default. Its use of
search also illustrates that better continuity can incorporate retrieval.
[Astra launch, Coding](https://openai.com/index/gpt-6-astra/),
[configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference).

### Parallel agents expand coverage and cumulative usage

The product documentation explicitly recommends subagents for exploration,
triage, and other reading-heavy work. Each performs its own model and tool work;
the main agent ordinarily receives a condensed result. The documentation gives
multi-million-token documents as an example of material that can be divided
among agents. Ultra permits proactive delegation in supported experiences;
other triggering behavior depends on surface and applicable instructions.
This is aggregate working capacity, not a single context of that size. A
coordinator can still miss an exception omitted from a worker's summary.
[Subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents),
[model and effort controls](https://learn.chatgpt.com/docs/models).

## Why token totals can become enormous

Let `I_j` be the input tokens counted for model request `j`, `C_j` its cached
input subset, and `O_j` its output. Over agents and requests, cumulative input is
`sum(I_j)`. It is not the size of the union of source passages encountered.
Reasoning, instructions, tool descriptions, generated text, and repeated source
can all contribute to the workload without being newly read source material.

Prompt caching reuses previously computed key-value states for matching prompt
prefixes. It avoids recomputing that prefix while leaving it usable for subsequent
generation. This is neither reading new documents nor merely replaying a stored
answer. Current API documentation gives large cached-input discounts and separate
cache-write accounting. Those API economics help explain why sustained use of
large contexts is practical; they do not establish the user's subscription
allowance formula.
[Prompt caching](https://developers.openai.com/api/docs/guides/prompt-caching).

This makes the user's Luna observation substantively interesting. A new failure,
constraint, or dependency can change what should be inferred from code already
in context. Reusing that code allows a new comparison or interpretation without
first rediscovering every relevant fragment. Cached input therefore can support
new reasoning even when it contains no new source. This is an inference about
why repeated broad context can help, not a measurement of the benefit of every
repeated token, and it does not imply updates to model weights.

An illustrative calculation, **not a measurement of the user's sessions**:
twenty agents each make one hundred requests containing the same 500,000-token
source prefix. That prefix alone contributes
`20 * 100 * 500,000 = 1,000,000,000` cumulative input tokens. If all agents use the
same source, the distinct source content is only 500,000 tokens. If they use
twenty disjoint prefixes, it is 10,000,000. Other request content would add usage.
Both examples are compatible with genuinely useful work; neither establishes a
billion distinct tokens read.

Useful accounting distinguishes:

| Quantity | Interpretation |
| --- | --- |
| Active context | What fits in a particular inference call |
| Cumulative input | Context counted over requests, including repetition |
| Cached input | A subset of input that reused prefix computation |
| Output and reasoning | Generated work; not additional source coverage |
| Distinct source regions delivered | Observable opportunity to read source, deduplicated by revision and span |
| Evidence incorporated correctly | Coverage and comprehension demonstrated in the result |

Use per-request increments or consistent session totals, not a sum of repeated
cumulative snapshots. Avoid double-counting a parent total that already includes
children. Tokenizer differences also limit cross-model comparisons. The user
clarified that the interesting older redesign sessions were dominated by
**Luna cached input during repeated reading of large amounts of code**. This is
consistent with the reuse mechanism above and does not assert a billion distinct
tokens. The interval and totals remain unaudited because no representative
session trace was identified. The question is whether repeated access supports
deeper understanding than earlier knowledge tools, not whether repeated input
should be dismissed as meaningless.

## Local evidence and attribution limits

The checkout was clean at the baseline above. Its existing
[evidence-discovery policy](../policy.md#evidence-discovery-and-terra-screening)
already requests broader investigation, neighboring source/callers/tests/docs,
alternatives, and continuation while consequential uncertainty remains. Its
[scientific literature guidance](../policy.md#scientific-literature-research-and-development-uptake)
goes further, asking for substantial autonomous grounding when warranted,
independent inquiries, primary-source reading, and reconciliation.

The curated [future-work account](../FURTHER-agents.md) records that producing
spontaneous extensive research was an explicit recent development objective. It
also retains the distinction between useful research in configured exercises and
unproven reliable generalization to ordinary chats. This investigation did not
rerun or regrade that campaign. Its existence makes local instructions a serious
confound when attributing the user's observations entirely to model updates.

There is also deployment drift: the installed
`/home/user/.codex/delegation-kit/policy.md` lacks the checkout's extensive
scientific literature section. This chat read the checkout's guidance; that does
not establish which version another chat loaded. Neither installed nor source
policy was changed here.

The local executable reports `codex-cli 0.163.0`. The matching public
[`rust-v0.163.0` release](https://github.com/openai/codex/releases/tag/rust-v0.163.0)
identifies commit `8308618`. Its
[asynchronous compaction code](https://github.com/openai/codex/blob/rust-v0.163.0/codex-rs/core/src/session/async_compaction.rs)
conditions background compaction on features, provider support, and context
thresholds. Its
[remote compaction implementation](https://github.com/openai/codex/blob/rust-v0.163.0/codex-rs/core/src/compact_remote_v2.rs)
records usage and filters/truncates retained history. These inspected paths
substantiate the mechanism and some additional usage sources. The CLI package
version does not identify the running desktop backend, prove feature activation,
or reveal actual source coverage in a past chat.

Tool-output truncation is a further observable boundary. In this investigation,
some large policy and web outputs were clipped and required smaller follow-up
reads. A command that opens a whole file does not prove its whole output reached
the model. Comprehensive reading must account for delivered output, not just
the command's intent.

## Research comparisons

### Global understanding can require broad exposure before query selection

The GraphRAG study is particularly relevant to the user's concern. On two
collections of about 1.0M and 1.7M tokens, methods processing the collection
broadly beat vector retrieval on judged answer comprehensiveness in roughly
72–83% and 72–80% of comparisons. A source-text map-reduce comparator also
improved comprehensiveness: the evidence is not exclusively an endorsement of
graphs. The study addresses global questions that a few locally relevant chunks
cannot adequately answer. Limits include two corpora, GPT-4-Turbo-era models,
generated questions and LLM judgments; counting more claims does not establish
their truth. The paper leaves fabrication-rate evaluation open.
[Edge et al., GraphRAG, v2 February 2025, sections 4–6 and Table 6](https://arxiv.org/html/2404.16130v2).

This supports a distinction between locating an answer and learning enough of a
collection to discover what matters. An initial question about implementation
may omit the mechanism that a prior research document explains. A broad reading
pass can uncover it before the agent commits to a design. This inference is
especially relevant to bounded, high-density authored knowledge; the cited
study does not quantify its benefit for the user's repositories.

Self-Route's EMNLP 2024 experiments compare full-context processing with a
default retrieval setup of five 300-word chunks across nine datasets and three
older models. Full context generally performs better; routing difficult cases
from retrieval to full context preserves much of that performance. Its failure
analysis identifies general, implicit, complex, and multistep questions as
problems for narrow retrieval. This directly supports expanding beyond the first
retrieved passages. It does not compare today's coding agents or all possible
retrievers. Different presentations of the paper's aggregate scores were not
fully reconciled, so no exact aggregate accuracy claim is used here.
[Li et al., EMNLP Industry 2024, sections 3–5](https://aclanthology.org/2024.emnlp-industry.66/).

The cache-augmented generation paper tests preloading bounded knowledge sets
of approximately 21K–85K tokens. Its revised results support benefits on several
cases but also show a reversal: on the larger HotpotQA condition, full-context
caching scores 0.7407 BERTScore against 0.7535 for sparse top-five retrieval.
These are semantic-similarity scores, not factual-accuracy percentages. The
large latency improvement is principally against uncached full-context inference;
it is not a universal speed advantage over sparse retrieval. The useful idea
is amortizing repeated access to a manageable foundation of knowledge, with
capacity and attention limits kept explicit.
[Chan et al., revised February 2025, Tables 1–3; WWW 2025 short paper](https://arxiv.org/html/2412.15605v2).

### Agents can choose how to inspect information rather than accept a fixed retrieval stage

The March 2026 preprint *Coding Agents are Effective Long-Context Processors*
uses Codex v0.46.0/GPT-5, sampling 200 cases per benchmark. BrowseComp-Plus
scores are 88.50 versus RAG's 65.00; LongBench-v2 is 61.50 versus full context's
61.00. Large full-context baselines involve windowing or sampling; 3T denotes
available corpus size, not material all read.

A 100-case BrowseComp-Plus ablation is particularly relevant: navigable files
versus one JSON dictionary reduced average `rg` calls from 31.05 to 18.46 and
increased `sed` calls from 0.61 to 4.48, without a dedicated retriever. The
observed shift was toward targeted range reading, not necessarily whole files.
The paper also observes evidence-dependent query revision. These older-model
experiments do not establish current defaults or isolate all mechanisms.
Representation changes confound the structure comparison; command counts are
not coverage, and repeated-run uncertainty is unreported.
The authors' suggestion that retrievers can displace broader exploration remains
a hypothesis. Costs exceed lightweight retrieval.
[Cao et al., March 2026 preprint, Tables 1 and 3, sections 5.1–5.3](https://arxiv.org/html/2603.20432).

Recursive Language Models put a large input in a programmable environment and
let a model inspect portions and invoke submodels. In the inspected GPT-5 setup,
the BrowseComp+ inputs contain 6–11M tokens; the RLM result is 91.3 versus 70.5
for a summary agent, at higher average cost in that comparison. Trajectories
include regex filtering and selective inspection; dense aggregation can require
many subcalls. Shorter-input performance can be worse and expensive outliers
occur. The experiments used synchronous calls and recursion depth one. This
demonstrates a way to reason over material beyond a single context window,
not a requirement to expose every token to the root model or evidence that Codex
implements this exact design.
[Zhang et al., RLM v2 January 2026, sections 2–4 and 6](https://arxiv.org/html/2512.24601v2).

### Evidence also rejects indiscriminate loading as a universal optimum

LaRA, published at ICML 2025, evaluates 2,326 cases across eleven older models,
four question types, and three document types. Its aggregate ranking changes
with context length: full context leads by 2.4 percentage points at 32K, while
retrieval leads by 3.68 at 128K. Comparison questions tend to benefit from full
context; unanswerability detection favors retrieval. At 128K, GPT-4o, Claude 3.5
Sonnet, and Gemini 1.5 Pro still favor full context despite the pooled retrieval
advantage, which includes weaker models. These are conditional findings about document QA, not estimates
of GPT-6 performance or open-ended scientific discovery.
[Li et al., LaRA, full methods and results](https://arxiv.org/html/2502.09977v2),
[ICML proceedings](https://proceedings.mlr.press/v267/li25dv.html).

SWE-agent's GPT-4-era interface ablation is a useful causal counterexample: on
SWE-bench Lite a 100-line viewer scored 18.0%, compared with 12.7% for its
full-file viewer. Keeping five observations also outperformed retaining full
history. Its iterative search interface encouraged exhausting matches and
budgets. Interface design can therefore alter both behavior and outcomes with
the same model. This does not justify imposing those historical line limits on
current models; it shows why reading quality cannot be inferred from volume.
[Yang et al., SWE-agent, November 2024 version, interface ablations](https://arxiv.org/html/2405.15793v3).

A recent repository-QA preprint supplies contrary evidence to an unconditional
delegation preference. Across 720 questions on 15 Python repositories, a
semantic-search agent achieves a pooled 65.2% pass rate against 46.2% for the
tested delegated-exploration system. Models, orchestration, and tool designs
limit transfer; this is not a clean retrieval-only ablation. The authors restrict
the conclusion to isolated questions on stable repositories, not long editing
sessions or global discovery.
[Oskooei et al., August 2026 preprint, under review](https://arxiv.org/html/2608.01507).

Older long-context work also cautions against equating availability with use.
*Lost in the Middle* tests position sensitivity and distractors; RULER adds
multi-value retrieval, multihop tracking, and aggregation beyond simple needle
tests. These task distinctions remain relevant even when newer models perform
far better. Their historical failure rates should not be attributed to the
current model family.
[Lost in the Middle, TACL 2024](https://aclanthology.org/2024.tacl-1.9/),
[RULER, task design](https://arxiv.org/html/2404.06654v3).

An October 2026 compaction preprint finds relatively stable scores across several
compaction thresholds on some tested workloads, but losses in another model/task
combination. Separately, judges assessing 44 real Claude Code sessions estimated
19% or 24.5% constraint loss, with process and scope instructions more vulnerable
than feature requirements. Its small controlled samples and different models
prevent direct extrapolation to present Codex. The finding suggests checking
whether important constraints survive long investigations, not assuming that
either compaction or retaining everything is always superior.
[Benchmarks Are Surprisingly Compaction-Friendly, October 2026 preprint](https://arxiv.org/html/2610.31778v1).

## Retrieval has not disappeared

Current OpenAI file search still combines semantic and keyword retrieval over
uploaded knowledge stores. The model can invoke it as a tool. That directly
rules out extinction of RAG as a product capability.
[File search](https://developers.openai.com/api/docs/guides/tools-file-search).

The narrower claim is much more defensible: a fixed retrieve-a-few-chunks then
answer pipeline is often inadequate for corpus understanding. Today's agents
can identify a source, open the full relevant unit, inspect its neighbors,
reformulate the question, check counterevidence, and continue. Search becomes
one operation inside an investigation rather than the final arbiter of what
the agent is allowed to know.

Anthropic's 2025 account similarly describes Claude Code combining initially
loaded project context with glob/grep and further exploration as needed. This
is another first-party example of sophisticated contextual work retaining
retrieval. It is evidence about a different product, not a statement of current
Codex defaults.
[Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents).

## Which explanations are established

| Explanation | Evidence status | Remaining distinction |
| --- | --- | --- |
| More context can be available per inference | Documented for all four API models | Actual app configuration and reliable use of every part |
| Less prompting is needed for useful reading and verification | Direct first-party Astra guidance | Frequency across tasks; transfer to Sol, Terra, Luna |
| Reading scope and granularity varied across earlier models | September 2025 exploration testimony and January 2026 contributor account of 200-line tendencies | CLI reports do not reconstruct the user's cloud sessions; requested, delivered, and displayed text differ |
| Investigation became more autonomous within ChatGPT before GPT-6 | Dated firsthand o3/o4-mini accounts align with documented tool-use changes; later ordinary Chat reports describe longer work | Selected reports are not a measure of complete-document coverage or a universal default |
| Sustained tool loops permit extensive inspection | Documented harness mechanism and older agent studies | How much any particular session actually inspected |
| Caching makes repeated context reuse cheaper | Documented computation and API accounting | Subscription allowance and observed session economics |
| Parallel agents can widen total evidence coverage | Product capability and studies | Overlap, coordination loss, and quality of synthesis |
| Training improves long-task behavior | Vendor accounts and capability outcomes | No public ablation attributing the observed reading shift to specific training changes |
| The kit contributes to broad research behavior | Direct local instruction evidence | Which instructions governed historical sessions and how strongly they affected behavior |
| RAG has become obsolete | Contradicted as a general claim | Fixed shallow retrieval can still be a poor fit for the user's work |
| The user's recent improvement is caused by one model update | Unresolved | No matched historical comparison separating model, harness, tools, instructions, and task |

The most plausible explanation is an interaction: stronger models make
exploration useful; richer tools make source inspection possible; persistent
harnesses let it continue; caching and parallel work make it affordable; and
instructions determine when to stop. Public evidence does not apportion the
effect among these causes.

## A strong reading preference worth preserving

The evidence supports a forceful preference against premature narrowing,
especially when the user has already supplied dense, curated material. It does
not require maximizing tokens or mechanically reading an unrelated repository
in full. The goal is enough independent exposure to discover mechanisms,
exceptions, and alternatives before deciding that only the first search results
matter.

The following is **proposed wording for later policy consideration**, not an
installed instruction:

> For substantial work grounded in an available codebase or curated knowledge
> collection, develop broad understanding before narrowing to the first plausible
> explanation or implementation. Treat the relevant authored knowledge as
> substantive grounding. Read complete coherent arguments and implementations,
> including assumptions, limitations, alternatives, failures, and dependencies.
> Do not let matches to the initial query or favored hypothesis alone define
> what deserves reading.
>
> Let substantive reading revise the questions and search terms. Pursue newly
> discovered mechanisms, dependencies, alternatives, and counterevidence. For
> bounded curated foundations, establish broad understanding even when decisive
> concepts are absent from the user's wording. A lack of search matches is not
> sufficient evidence that a behavior, constraint, or alternative is absent.
>
> Independently obtain the evidence the task requires. Do not wait for the user
> to name each missing source or prescribe each next reading step. When a source
> exposes a consequential gap or contradiction, follow it through before treating
> the investigation as complete.
>
> Use search to navigate, cross-check, and revisit evidence. Search snippets,
> abstracts, filenames, and delegated summaries do not substitute for inspecting
> the original material needed to understand a consequential claim. For global
> questions, cover the material subjects across the designated collection; a few
> highly ranked passages are not sufficient evidence of that coverage.
>
> Choose reading scope from the source's structure and the task, rather than an
> arbitrary short preview. Prefer a complete coherent file or section when it is
> useful and practical to inspect together. When chunking is necessary, follow
> through to the required coverage and preserve relationships across boundaries.
> Check both the meaning of each excerpt and coverage of the relevant subjects
> and dependencies; longer excerpts alone do not establish broader coverage.
>
> If the relevant material exceeds a context window or tool-output limit, continue
> through coherent sections or appropriately scoped agents. Preserve source
> locations, substantive relationships, contradictions, and coverage gaps. Check
> truncation and revisit originals when a new finding changes their significance.
> Reuse available context when useful; do not discard needed evidence merely to
> minimize input tokens.
>
> Use known source locations to avoid repeated discovery loops. Re-reading is
> useful when a new question or finding changes the significance of existing
> evidence; do not require every useful read to add previously unseen text.
>
> Continue while feasible reading could materially change the explanation,
> alternatives, or result. Complete the requested breadth and depth before
> concluding. Match scope to the task: a localized mechanical change need not
> trigger whole-project study, while a redesign or scientific synthesis must not
> inherit the narrow evidence budget of a simple lookup.

This direction strengthens existing evidence and scientific-grounding sections
instead of adding a competing workflow. Its practical application depends on
the task:

| Task | Reading expectation | Evidence that it helped |
| --- | --- | --- |
| Bounded curated scientific foundation | Read across material subjects before selecting an approach; preserve alternative mechanisms and adverse results | A consequential assumption, alternative, or operating limit is incorporated correctly |
| Unfamiliar repository redesign | Understand architecture, state ownership, interfaces, callers, tests, and historical rationale | Cross-component requirements survive the proposed change |
| Localized defect | Read the complete relevant behavior and dependencies; broaden when the first explanation fails | A causal account and check cover the real contract |
| Global comparison or synthesis | Systematic coverage across the declared collection | Conclusions account for dispersed and contrary evidence |
| Large structured aggregation | Use validated computation with targeted semantic inspection | Correct aggregation with explicit schema and interpretation |

The user's preference can be adopted as a preference without claiming a
universal empirical optimum. If future model or harness changes reduce depth,
the symptom to address is missing consequential coverage or premature stopping,
not merely a smaller token total.

## How to document a regression without rewarding waste

A future comparison should preserve model, effort, client/backend identity,
loaded instructions, source revision, tools, and task. Historical versions may
be unavailable; when they are, compare observable present variants rather than
claim a controlled reconstruction of the past.

Use cases with consequential information absent from the initial wording:
a cross-document contradiction, an unexpected scientific alternative, an
exception in a caller, a historical failed approach, or a constraint distributed
across modules. Include straightforward local work as a contrast, so broad
reading is assessed where it is useful rather than rewarded everywhere.

Compare existing behavior, a stronger comprehensive-reading instruction, and
adaptive search plus complete-source expansion. Assess accepted outcomes,
missed requirements, unsupported conclusions, discovered alternatives, source
coverage, and time. Record cumulative input, cached input, output, and repeated
reads separately. Where traces permit, deduplicate delivered source regions by
path or URL, revision, and offsets; distinguish a program scanning data from the
model receiving its contents. Hold independent outcome criteria fixed and retain
negative results. A better explanation of a proposed test is not an executed test.

For the user's command-level observation, additionally record the requested
read ranges, actual returned ranges, omission notices, and subsequent reads.
Keep UI display clipping separate from model-input truncation. Compare whether
broader scope was chosen autonomously or only after a user correction, and
whether smaller reads ultimately achieved the same coverage with more work.
Do not count an announced or planned read as an executed one.

Use the behavioral matrix to diagnose which choice regressed. For example,
distinguish a wrong initial framing from a correctly located source clipped
before its exception, or from a complete source whose meaning was misunderstood.
Candidate comparisons should include a decisive concept absent from the prompt,
a qualification just outside an initial excerpt, an interaction in another
module, and a precise local fact where a small excerpt is enough. These are
proposed discriminating cases, not tests executed in this investigation. Judge
coverage and the resulting decisions; a larger snippet or fewer searches alone
is not success.

This report supplies the explanatory research and a reviewable preference. It
does not claim such a matched behavioral comparison was run. The historical
sources and public studies already establish enough to reject snippet-only
coverage as a universal strategy; session-specific causal attribution would
require the actual historical traces or a controlled comparison.

## Evidence scope and review

The investigation covered official product and API documentation, historical
launches and firsthand community reports, pinned public Codex source, local kit
instructions/history, and comparative research on full context, retrieval,
global synthesis, agent interfaces, and compaction. Two independent inquiries
developed full-problem accounts before reconciliation. A separate scientific
critic examined primary literature before receiving the draft, then checked its
claims and transfer limits. The scientific review found the account ready after
corrections to unknown-concept discovery wording, benchmark sampling/baselines,
and LaRA's strong-model counterpattern.

Material papers were inspected through relevant methods, results, and
limitations rather than abstracts alone; this was not an exhaustive review of
every appendix or a formal systematic review. The research distinguishes
verified venue records from versioned manuscripts and explicitly identified
preprints. Original benchmark results were not reproduced. The old Knowledge
help page could not be recovered as an independent official archive; its
contemporaneous quotation retains that weaker provenance. The studies do not
measure current Astra/Sol/Terra/Luna spontaneous-reading frequency under matched
desktop harnesses.

No private chat-history sweep was performed. The local CLI version and source
capabilities do not establish the desktop backend's resolved settings. Public
documentation was accessed on November 17, 2026; mutable pages can change.
The follow-up community investigation used separate historical and recent
ChatGPT evidence branches, then compared their findings with dated product
announcements. It sought positive before-and-after accounts as well as failures;
it found no matched trace demonstrating universal complete-document reading.
The subsequent command-focused investigation examined original reading-related
issues, contributor replies, model-transition announcements, and bounded public
CLI source evidence. It preserved the user's undated recollection as such and
did not infer private parameter counts or cloud settings from CLI behavior.
The behavioral specification separates historical observations, experimental
mechanisms, and proposed practice. Two further read-only syntheses examined
literature-based distinctions and command-level examples. The source-structure
ablation was checked separately; no present-day behavioral benchmark was run.
This investigation changed only this report. It did not edit curated research,
policy, runtime inventory, model settings, or installed files. A concurrent
modification to `FURTHER-agents.md` appeared during the final review; its
provenance was not established here, and it was preserved without alteration.
