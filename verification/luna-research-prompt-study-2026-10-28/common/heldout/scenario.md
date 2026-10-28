# Prospective regression-routing scenario packet

## Assignment identity and source boundary

This is a prospective planning exercise, not a replay of a historical incident. The project source is `unbundled-home/___quick/p/_cur/dataPump/_lessonsLearned/software-foundation`, Git `HEAD` **4c471cb93702cdc03b5230bfa33372355424b665** (`WIP - DRAFT - simplification and cleanup, simplification and cleanup rules, etc.`). The observed working tree was clean: `git status --porcelain=v1 --untracked-files=all` and `git diff --stat` emitted no changes. No project test, build, configure, or application command was executed for this packet. The source checkouts were read-only throughout.

The delegation-kit checkout identity supplied for context is `unbundled-home/___quick/p/_cur/codex-delegation-kit`, `HEAD` `947ed25d4058e405ecf45d6956671f6fecb12026`, with pre-existing modifications in documentation, policy, role files and verification artifacts. Those changes were not read for scenario content, altered, or treated as project routing inputs.

The excerpts under `sources/` come from the named project revision. They capture a sample of test registrations and test code; their presence does not prove execution, pass/fail status, or complete inventory. Source facts and project limits below are documented facts. The incident reports, run resources and later feedback are invented for this exercise and explicitly labeled hypothetical.

Project guidance read for scope: `AGENTS.md`, `docs/README.md`, `docs/testing.md`, and `docs/building.md`. It requires following relevant topic docs and using `build.sh`; calls for inexpensive checks; withholds expensive full regressions, broad platform/backend matrices and complete release certification absent a qualifying request; says a focused pass proves only its named scope; and forbids weakening correctness assertions merely to obtain green CI. It additionally says appended payload work does not authorize configuring, compiling, linking or installing the retained kernel. The eight reports below concern ordinary source/API and build-helper behavior. No appended payload, retained engine/kernel maintenance, distribution release, optional platform qualification, or publication is in scope.

## Hypothetical initial information

A user reports that a newly prepared development build has a cluster of failures after a routine source update. The summaries below are **invented symptom reports**, not claims about this checkout or its history. The user has no minimized reproducer beyond these short observations. No root cause is known, and the reports may have independent causes.

1. **R01, store contract:** A small caller says a rejected update appears to leave a changed record behind, but its before/after dump omitted record IDs.
2. **R02, CLI contract:** One command batch reportedly prints a valid first row before rejecting a later invalid value; another invocation says `--help` exits unsuccessfully when output is redirected.
3. **R03, text provider boundary:** The C++-provider configuration reports the expected validation error, while a Rust-provider package allegedly accepts one non-ASCII byte sequence. The exact package/provider identity was not captured.
4. **R04, GUI application path:** A user can submit an entry from one adapter, but the status indicator and visible collection disagree until another action occurs. The adapter and event order are unspecified.
5. **R05, native task path:** After cancelling a long task and starting another, progress from the earlier operation is reported once. The user did not retain generation values or a process trace.
6. **R06, browser transport path:** A browser-hosted task reportedly stops refreshing after a transient transport error, although a later action sometimes updates the view. No browser, timing trace, or transport log is attached.
7. **R07, text and wheel behavior:** In a nested view, scrolling over a read-only text area reportedly changes focus or fails to move the containing pane. Whether the child has overflow is unknown.
8. **R08, editor value layer:** A project canvas appears displaced after changing a model value; a separate report says a flow completes but a consumer receives a truncated result. Neither report identifies the project or mode.

These symptoms deliberately under-specify invocation, backend, build configuration, input, output, and timing. Planners must classify uncertainty instead of assuming a shared cause. The actual source and tests can establish plausible caller paths and contracts, but not runtime reproduction.

## Observable objective and fixed acceptance

Produce an investigation plan that addresses all **eight** reports under one fixed rubric, then carry it through only if separately authorized. For each report, identify (a) the observed symptom class and its unknowns, (b) the relevant source entry point/helper/API and at least one affected consumer path, (c) the registered focused test or best existing fixture and its limits, and (d) one discriminating causal check using matched inputs/configuration. Keep reproduced failure, rejected hypothesis, setup failure, and untested work distinct. Cross-check neighboring callers or contracts where a local pass cannot establish the consumer behavior.

Acceptance is eight classified reports with source-grounded paths, causal checks, and explicit coverage limits; plus sample affected-consumer paths across at least three distinct layers (core/provider, executable or GUI, and build or retained-input consumer). If repairs are proposed later, preserve the original failure and all existing correctness thresholds; no tolerance/assertion weakening counts as acceptance. Report unresolved reports as unresolved rather than counting them as passes. The objective and rubric are equal for both planning arms.

## Hypothetical available campaign envelope

For the proposed controlled campaign, assume **six reasoning-work slots total, including the coordinator and any reviewers**, **four test-execution slots**, and one shared, already-configured build tree with an 8-CPU / 16-GiB ceiling. The tree is ready for targeted checks; this statement is a scenario resource assumption, not evidence that this agent configured or validated a build. Slots and resources are shared; they do not multiply by opening more sessions. The plan should reserve resources within those limits and identify when configuration or an unready prerequisite would make an experiment setup-failed. This packet itself executed no experiment.

## Source-unit map

Each excerpt file names paths and preserves source line numbers. Test declarations establish only that a case is registered in this source. A discovered test is not an executed test, and a focused fixture does not establish a broad platform/backend claim.

| Unit | Source/test family | Main source references | Registration/consumer references |
| --- | --- | --- | --- |
| R01 | Store validation, capacity and state | `src/store.cpp:11-55` | `tests/store_test.cpp:26-55`, `CMakeLists.txt:468-479` |
| R02 | CLI parsing and emitted output | `src/main.cpp:13-45` | `tests/check_cli.py:11-46`, `CMakeLists.txt:468-479` |
| R03 | Text ABI and provider | `src/text_validation.cpp:1-35` | `tests/rust_component_test.cpp:14-69`, `tests/rust_component_status_test.cpp:27-70`, `CMakeLists.txt:502-526` |
| R04 | Shared GUI application transitions | `gui/shared/application.cpp:49-125` | `gui/tests/application_test.cpp:40-97`, `gui/CMakeLists.txt:25-35,91-96` |
| R05 | Native task worker lifecycle | `gui/shared/task_native.cpp:8-70` | `gui/tests/task_native_test.cpp:7-41`; executor selected at `gui/CMakeLists.txt:25-35` |
| R06 | Browser polling and lifecycle | `gui/host/browser_lifecycle.mjs:1-12` | `gui/tests/browser_lifecycle_test.mjs:1-15`, `gui/CMakeLists.txt:164-173,190-205` |
| R07 | Text frame, retained state and wheel | `gui/tests/text_frame_test.cpp:8-52`, `gui/tests/wheel_chaining_test.cpp:7-36`, `gui/patches/wheel-chaining-interaction.patch:1-22`, `gui/patches/text-frame-framebuffer.patch:1-19` | `gui/CMakeLists.txt:145-159,548-553` |
| R08 | Editor model and canvas | `editor/model/project.cpp:603-624`, `editor/ui/canvas.cpp:157-180`, `editor/tests/model_test.cpp:14-40`, `editor/tests/canvas_test.cpp:38-50` | `editor/CMakeLists.txt:130-148` |
| R09 | SDK/imported path containment | `cmake/DependencyPaths.cmake:1-80` | `tests/test_sdk_paths.py:26-69`; suite named in root CMake list at `CMakeLists.txt:603` |
| R10 | Process-tree cleanup | `tools/process_tree.py:1-70` | `tests/test_process_tree.py:1-90`; suite named in root CMake list at `CMakeLists.txt:584` |
| R11 | Retained GUI source-group consumer | `gui/source_group.py:30-80` | `tests/test_gui_source_group.py:69-115`, `cmake/GuiInputs.cmake:1-55`, `gui/CMakeLists.txt:1-20` |
| R12 | Build-capacity helper | `tools/build_capacity.py:1-80` | `tests/test_build_capacity.py:1-85`; suite named in root CMake list at `CMakeLists.txt:584` |
| R13 | Editor flow execution and terminal state | `editor/tests/flow_test.cpp:300-410` | `editor/CMakeLists.txt:110-156` |

R09-R13 are neighboring evidence for consumer/configuration and execution-integrity checks; they are not asserted to be implicated by any initial symptom. Search only relevant tracked source and registrations for this planning task. Do not recursively mine retained history/build trees or claim these 13 units enumerate every test or supported platform.

The source registration excerpt shows that `core.store` and `core.cli` are available in ordinary CTest setup, provider-facing text tests have their own registrations, GUI functional cases are selected through `gui/CMakeLists.txt`, and a number of Python helper suites are registered from the root CMake suite list. The actual build configuration and platform gates determine whether a particular test is enabled. No test execution evidence is supplied.

## Common experiment discipline

Plans should prefer a focused fixture or existing targeted test that distinguishes two plausible layers, retain exact source/configuration/input identity, and follow the existing wrapper where building is required. For shared GUI behavior, compare the same event sequence and snapshot through the relevant adapters, then trace whether the defect is in event normalization, shared state, rendering, or transport. For provider behavior, identify the configured provider and package/library marker before comparing byte inputs through the actual C++ caller. For reported helper behavior, use a small offline fixture when it can answer the question and inspect its caller before broadening. A missing prerequisite is a setup result, not a source failure. No tests or builds have been run as part of preparing this scenario.
