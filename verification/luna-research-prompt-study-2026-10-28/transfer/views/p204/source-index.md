# Source inventory (same excerpts available to both arms)

# R01: Store validation, capacity and state preservation
Source identity: software-foundation at 4c471cb93702cdc03b5230bfa33372355424b665. Excerpts are source evidence only; they do not establish that any test ran or passed.
Project instruction excerpt (applies to this unit): `AGENTS.md` §Development checks: “Run inexpensive checks that address the current change. Defer costly full regressions, broad platform/backend matrices and complete release certification … until implementation is stable and the user has requested either that qualification or an operation requiring it.” `docs/testing.md` §Select the applicable stage: “A focused pass proves only its named scope.” `docs/testing.md` §Test design: “Keep contract regressions when refactoring. Modify an assertion only when the intended public contract changes and the change is reviewed.” These are scope/authorization filters, not execution evidence. No kit routing text is included.

## `src/store.cpp` lines 11-55

```text
  11 Store::Store(std::size_t capacity) : capacity_(capacity) {

# R02: CLI parsing, atomic output and executable contract
Source identity: software-foundation at 4c471cb93702cdc03b5230bfa33372355424b665. Excerpts are source evidence only; they do not establish that any test ran or passed.
Project instruction excerpt (applies to this unit): `AGENTS.md` §Development checks: “Run inexpensive checks that address the current change. Defer costly full regressions, broad platform/backend matrices and complete release certification … until implementation is stable and the user has requested either that qualification or an operation requiring it.” `docs/testing.md` §Select the applicable stage: “A focused pass proves only its named scope.” `docs/testing.md` §Test design: “Keep contract regressions when refactoring. Modify an assertion only when the intended public contract changes and the change is reviewed.” These are scope/authorization filters, not execution evidence. No kit routing text is included.

## `src/main.cpp` lines 13-45

```text
  13 int run(int argc, const char* const* argv) {

# R03: C++ caller and provider ABI for text validation
Source identity: software-foundation at 4c471cb93702cdc03b5230bfa33372355424b665. Excerpts are source evidence only; they do not establish that any test ran or passed.
Project instruction excerpt (applies to this unit): `AGENTS.md` §Development checks: “Run inexpensive checks that address the current change. Defer costly full regressions, broad platform/backend matrices and complete release certification … until implementation is stable and the user has requested either that qualification or an operation requiring it.” `docs/testing.md` §Select the applicable stage: “A focused pass proves only its named scope.” `docs/testing.md` §Test design: “Keep contract regressions when refactoring. Modify an assertion only when the intended public contract changes and the change is reviewed.” These are scope/authorization filters, not execution evidence. No kit routing text is included.

## `src/text_validation.cpp` lines 1-35

```text
   1 #include "text_validation.h"

# R04: Shared GUI application, adapter integration and state transitions
Source identity: software-foundation at 4c471cb93702cdc03b5230bfa33372355424b665. Excerpts are source evidence only; they do not establish that any test ran or passed.
Project instruction excerpt (applies to this unit): `AGENTS.md` §Development checks: “Run inexpensive checks that address the current change. Defer costly full regressions, broad platform/backend matrices and complete release certification … until implementation is stable and the user has requested either that qualification or an operation requiring it.” `docs/testing.md` §Select the applicable stage: “A focused pass proves only its named scope.” `docs/testing.md` §Test design: “Keep contract regressions when refactoring. Modify an assertion only when the intended public contract changes and the change is reviewed.” These are scope/authorization filters, not execution evidence. No kit routing text is included.

## `gui/shared/application.cpp` lines 49-125

```text
  49 void Application::append_entry() {

# R05: Native task worker ownership, cancellation and shutdown
Source identity: software-foundation at 4c471cb93702cdc03b5230bfa33372355424b665. Excerpts are source evidence only; they do not establish that any test ran or passed.
Project instruction excerpt (applies to this unit): `AGENTS.md` §Development checks: “Run inexpensive checks that address the current change. Defer costly full regressions, broad platform/backend matrices and complete release certification … until implementation is stable and the user has requested either that qualification or an operation requiring it.” `docs/testing.md` §Select the applicable stage: “A focused pass proves only its named scope.” `docs/testing.md` §Test design: “Keep contract regressions when refactoring. Modify an assertion only when the intended public contract changes and the change is reviewed.” These are scope/authorization filters, not execution evidence. No kit routing text is included.

## `gui/shared/task_native.cpp` lines 8-70

```text
   8 // One persistent producer owns its copied input. A one-slot latest-progress

# R06: Browser polling lifecycle and transport failure handling
Source identity: software-foundation at 4c471cb93702cdc03b5230bfa33372355424b665. Excerpts are source evidence only; they do not establish that any test ran or passed.
Project instruction excerpt (applies to this unit): `AGENTS.md` §Development checks: “Run inexpensive checks that address the current change. Defer costly full regressions, broad platform/backend matrices and complete release certification … until implementation is stable and the user has requested either that qualification or an operation requiring it.” `docs/testing.md` §Select the applicable stage: “A focused pass proves only its named scope.” `docs/testing.md` §Test design: “Keep contract regressions when refactoring. Modify an assertion only when the intended public contract changes and the change is reviewed.” These are scope/authorization filters, not execution evidence. No kit routing text is included.

## `gui/host/browser_lifecycle.mjs` lines 1-12

```text
   1 // One outstanding poll is sufficient: transport order also orders task steps.

# R07: Text presentation, focus state and nested wheel chaining
Source identity: software-foundation at 4c471cb93702cdc03b5230bfa33372355424b665. Excerpts are source evidence only; they do not establish that any test ran or passed.
Project instruction excerpt (applies to this unit): `AGENTS.md` §Development checks: “Run inexpensive checks that address the current change. Defer costly full regressions, broad platform/backend matrices and complete release certification … until implementation is stable and the user has requested either that qualification or an operation requiring it.” `docs/testing.md` §Select the applicable stage: “A focused pass proves only its named scope.” `docs/testing.md` §Test design: “Keep contract regressions when refactoring. Modify an assertion only when the intended public contract changes and the change is reviewed.” These are scope/authorization filters, not execution evidence. No kit routing text is included.

## `gui/tests/text_frame_test.cpp` lines 8-52

```text
   8 gui::Snapshot scene(){

# R08: Editor model and canvas geometry behavior
Source identity: software-foundation at 4c471cb93702cdc03b5230bfa33372355424b665. Excerpts are source evidence only; they do not establish that any test ran or passed.
Project instruction excerpt (applies to this unit): `AGENTS.md` §Development checks: “Run inexpensive checks that address the current change. Defer costly full regressions, broad platform/backend matrices and complete release certification … until implementation is stable and the user has requested either that qualification or an operation requiring it.” `docs/testing.md` §Select the applicable stage: “A focused pass proves only its named scope.” `docs/testing.md` §Test design: “Keep contract regressions when refactoring. Modify an assertion only when the intended public contract changes and the change is reviewed.” These are scope/authorization filters, not execution evidence. No kit routing text is included.

## `editor/tests/model_test.cpp` lines 14-40

```text
  14 void parsing() {

# R09: SDK and imported dependency path validation across CMake scopes
Source identity: software-foundation at 4c471cb93702cdc03b5230bfa33372355424b665. Excerpts are source evidence only; they do not establish that any test ran or passed.
Project instruction excerpt (applies to this unit): `AGENTS.md` §Development checks: “Run inexpensive checks that address the current change. Defer costly full regressions, broad platform/backend matrices and complete release certification … until implementation is stable and the user has requested either that qualification or an operation requiring it.” `docs/testing.md` §Select the applicable stage: “A focused pass proves only its named scope.” `docs/testing.md` §Test design: “Keep contract regressions when refactoring. Modify an assertion only when the intended public contract changes and the change is reviewed.” These are scope/authorization filters, not execution evidence. No kit routing text is included.

## `cmake/DependencyPaths.cmake` lines 1-77

```text
   1 include_guard(GLOBAL)

# R10: Process-tree observation and child cleanup
Source identity: software-foundation at 4c471cb93702cdc03b5230bfa33372355424b665. Excerpts are source evidence only; they do not establish that any test ran or passed.
Project instruction excerpt (applies to this unit): `AGENTS.md` §Development checks: “Run inexpensive checks that address the current change. Defer costly full regressions, broad platform/backend matrices and complete release certification … until implementation is stable and the user has requested either that qualification or an operation requiring it.” `docs/testing.md` §Select the applicable stage: “A focused pass proves only its named scope.” `docs/testing.md` §Test design: “Keep contract regressions when refactoring. Modify an assertion only when the intended public contract changes and the change is reviewed.” These are scope/authorization filters, not execution evidence. No kit routing text is included.

## `tools/process_tree.py` lines 1-70

```text
   1 #!system-fixture/usr/bin/env python3

# R11: Retained GUI input group verification and configured consumer selection
Source identity: software-foundation at 4c471cb93702cdc03b5230bfa33372355424b665. Excerpts are source evidence only; they do not establish that any test ran or passed.
Project instruction excerpt (applies to this unit): `AGENTS.md` §Development checks: “Run inexpensive checks that address the current change. Defer costly full regressions, broad platform/backend matrices and complete release certification … until implementation is stable and the user has requested either that qualification or an operation requiring it.” `docs/testing.md` §Select the applicable stage: “A focused pass proves only its named scope.” `docs/testing.md` §Test design: “Keep contract regressions when refactoring. Modify an assertion only when the intended public contract changes and the change is reviewed.” These are scope/authorization filters, not execution evidence. No kit routing text is included.

Project instruction excerpt (applies to this unit): `AGENTS.md` §Development checks: “Run inexpensive checks that address the current change. Defer costly full regressions, broad platform/backend matrices and complete release certification … until implementation is stable and the user has requested either that qualification or an operation requiring it.” `docs/testing.md` §Select the applicable stage: “A focused pass proves only its named scope.” `docs/testing.md` §Test design: “Keep contract regressions when refactoring. Modify an assertion only when the intended public contract changes and the change is reviewed.” These are scope/authorization filters, not execution evidence. No kit routing text is included.

## `gui/source_group.py` lines 30-80


# R12: Build-capacity planning and limit enforcement
Source identity: software-foundation at 4c471cb93702cdc03b5230bfa33372355424b665. Excerpts are source evidence only; they do not establish that any test ran or passed.
Project instruction excerpt (applies to this unit): `AGENTS.md` §Development checks: “Run inexpensive checks that address the current change. Defer costly full regressions, broad platform/backend matrices and complete release certification … until implementation is stable and the user has requested either that qualification or an operation requiring it.” `docs/testing.md` §Select the applicable stage: “A focused pass proves only its named scope.” `docs/testing.md` §Test design: “Keep contract regressions when refactoring. Modify an assertion only when the intended public contract changes and the change is reviewed.” These are scope/authorization filters, not execution evidence. No kit routing text is included.

## `tools/build_capacity.py` lines 1-80

```text
   1 #!system-fixture/usr/bin/env python3

# R13: Editor flow execution and terminal-state behavior
Source identity: software-foundation at 4c471cb93702cdc03b5230bfa33372355424b665. Excerpts are source evidence only; they do not establish that any test ran or passed.
Project instruction excerpt (applies to this unit): `AGENTS.md` §Development checks: “Run inexpensive checks that address the current change. Defer costly full regressions, broad platform/backend matrices and complete release certification … until implementation is stable and the user has requested either that qualification or an operation requiring it.” `docs/testing.md` §Select the applicable stage: “A focused pass proves only its named scope.” `docs/testing.md` §Test design: “Keep contract regressions when refactoring. Modify an assertion only when the intended public contract changes and the change is reviewed.” These are scope/authorization filters, not execution evidence. No kit routing text is included.

## `visual/flow/flow.cpp` lines 417-467

```text
 417             if (result.consumed.size() != ctx.inputs_.size() || result.produced.size() != ctx.outputs_.size() ||
