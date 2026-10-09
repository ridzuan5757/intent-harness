# Implementation Plan: Core

**Branch**: `001-core` | **Date**: 2026-10-09 | **Spec**: [spec.md](spec.md)

## Summary

Build the SDK core: three protocols, five data types, a tool wrapper that records trace
steps, a registry that checks parts when they are registered, a `Harness` that classifies a
question among the loaded intents and runs the chosen one, and loading from module paths
and from a `.env` file. The core imports no concrete part. Tests use fakes.

## Technical Context

**Language/Version**: Python 3.12
**Primary Dependencies**: python-dotenv (for `.env`); standard library otherwise
**Storage**: none
**Testing**: pytest
**Target Platform**: macOS and Linux, CPU
**Project Type**: library
**Performance Goals**: none for this feature (the core adds only Python calls)
**Constraints**: the core must not import any tool, intent or classifier
**Scale/Scope**: six modules, about 400 lines with tests

## Constitution Check

| Principle | Check |
|---|---|
| I. Core knows nothing concrete | Pass: the core has protocols, types, registry, loading and `Harness` only. SC-002 checks the imports. |
| II. Moved code keeps its numbers | Not applicable: no code is moved in this feature. |
| III. Public repository hygiene | Pass: the staged diff is searched before each commit; worktree and pull request. |
| IV. Environment | Pass: no new package; python-dotenv and pytest are already pinned. |
| V. Scope and simplicity | Pass: only the parts in the spec. No entry points yet. |
| VI. Plain writing | Pass: docstrings in short active sentences. |

## Design

### Trace collection

A `contextvars.ContextVar` holds the list of steps of the current `answer` call. The tool
wrapper appends one `Step` per call when the variable is set, and records nothing when it is
not set. This keeps tools free of any trace argument, and nested calls stay in call order.

### Contracts

`typing.Protocol` classes with `runtime_checkable`. The registry does not rely on
`isinstance` alone, because a protocol check does not name the missing attribute. It checks
each required attribute by name and reports the first one that is missing.

### Data types

Frozen `dataclasses`: `Choice`, `Step`, `Result`, `Answer`, plus `IntentInfo` (key and
description) that the classifier receives. Mappings are plain `dict`; the trace is a
`tuple` of steps.

### Tools given to an intent

`Harness.answer` passes the intent a read-only mapping that holds only the tools named in
`required_tools`. An intent cannot reach a tool it did not declare.

### Loading

`load_module(harness, path, **options)` imports the module with `importlib.import_module` and
calls its `register(harness, **options)`. `Harness.load_tools`, `load_intents` and
`load_classifier` call it. `Harness.from_env(path)` reads the file with
`dotenv.dotenv_values` (it does not change `os.environ`) and loads in the order tools,
intents, classifier.

## Project Structure

```text
intent_harness/
├── __init__.py      # public names
├── contracts.py     # Tool, Intent, IntentClassifier
├── types.py         # Choice, Step, Result, Answer, IntentInfo
├── tool_wrapper.py  # FunctionTool, as_tool, the trace context
├── registry.py      # Registry, RegistrationError
├── loading.py       # load_module, parse_list, read_env, LoadError
└── harness.py       # Harness
tests/
├── fakes.py         # fake tools, intents, classifier
├── plugins/         # fake plugin modules for loading tests
├── test_types.py
├── test_tools.py
├── test_registry.py
├── test_harness.py
└── test_loading.py
pyproject.toml
```

**Structure Decision**: one flat package; the tools package of feature 002
(`intent_harness_tools`) sits beside it and is found by the `intent_harness*` pattern.

## Complexity Tracking

None.
