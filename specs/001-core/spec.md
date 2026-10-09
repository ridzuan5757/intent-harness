# Feature Specification: Core

**Feature Branch**: `001-core`

**Created**: 2026-10-09

**Status**: Draft

**Input**: User description: "The core of the SDK: contracts, types, registry, Harness, and
loading at runtime, in code and from a .env file. The core knows no concrete tool, intent or
classifier."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Answer a question with loaded parts (Priority: P1)

A developer loads one intent classifier, some tools and some intents into a `Harness`. The
developer then calls `answer(image, question)` and gets one `Answer`. The answer names the
intent, the pipeline, the value, the confidence of the intent choice, and the trace of each
tool step.

**Why this priority**: this is the public call of the SDK. Every later feature plugs into it.

**Independent Test**: load a fake classifier, a fake tool and a fake intent; call `answer`;
check each field of the `Answer`.

**Acceptance Scenarios**:

1. **Given** a harness with two loaded intents, **When** the classifier chooses the second,
   **Then** the second intent runs and the answer names it.
2. **Given** an intent that calls a tool twice, **When** it runs, **Then** the answer trace has
   two steps, in call order, each with the tool name, its inputs and its output.
3. **Given** a harness with no classifier or no intent, **When** `answer` is called, **Then**
   it raises a clear error.

---

### User Story 2 - Register parts and fail early (Priority: P2)

A developer registers tools, intents and a classifier. The registry checks each part against
its contract when it is registered. An intent states the tool names it needs. If a tool name
is missing, the error comes when the intent is registered, not when a question is answered.

**Why this priority**: errors at load time are cheaper to find than errors during a run.

**Independent Test**: register parts with missing attributes or missing tools and check the
error each one gives.

**Acceptance Scenarios**:

1. **Given** an object without `key`, `description`, `required_tools` or `run`, **When** it is
   registered as an intent, **Then** registration fails with a message that names the
   missing attribute.
2. **Given** an intent that needs tool `x`, **When** no tool `x` is registered, **Then**
   registration of the intent fails and names `x`.
3. **Given** two tools with the same name, **When** the second is registered, **Then**
   registration fails.
4. **Given** a plain function, **When** it is registered with a name, **Then** the registry
   wraps it as a `Tool` and returns it by that name.

---

### User Story 3 - Load from module paths and from a .env file (Priority: P3)

A developer names the parts to load as module paths, in code or in a `.env` file. The
harness imports each module and asks it to register its parts.

**Why this priority**: an application (for example a notebook) can then load a fixed set of
parts from one file, and the paper's tables all load the same set.

**Independent Test**: write fake plugin modules in the test folder, list them in a `.env`
file, call `Harness.from_env(path)` and answer a question.

**Acceptance Scenarios**:

1. **Given** a module with a `register(harness, **options)` function, **When** its path is
   loaded, **Then** the parts it registers are in the harness.
2. **Given** a `.env` file with `INTENT_HARNESS_TOOLS`, `INTENT_HARNESS_INTENTS`,
   `INTENT_HARNESS_CLASSIFIER` and `INTENT_HARNESS_CLASSIFIER_MODEL`, **When**
   `Harness.from_env(path)` runs, **Then** the tools load first, then the intents, then the
   classifier, and the model name is passed to the classifier module.
3. **Given** a module path that does not import, or a module with no `register` function,
   **When** it is loaded, **Then** loading fails with a message that names the module.

### Edge Cases

- A tool raises an error: the step is recorded with `ok=False` and the error text, and the
  error is raised again so that the caller sees it.
- The classifier returns a key that is not a loaded intent: `answer` raises an error.
- The classifier returns probabilities that do not sum to 1: the core does not correct them;
  it reports them as given.
- An empty item in a comma-separated list (for example `a,,b`) is skipped.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The core MUST define three contracts as Python protocols: `Tool` (`name`,
  callable), `Intent` (`key`, `description`, `required_tools`, `run(image, question, tools)`),
  and `IntentClassifier` (`classify(question, intents) -> Choice`).
- **FR-002**: The core MUST define the types `Choice` (key, probabilities, confidence),
  `Step` (tool name, inputs, output, ok, error), `Result` (value, pipeline; what an intent's
  `run` returns) and `Answer` (intent, pipeline, value, confidence, probabilities, trace).
- **FR-003**: The core MUST provide a wrapper that turns a plain function into a named
  `Tool`. Each call MUST record one `Step` in the trace of the current answer.
- **FR-004**: The registry MUST check each part against its contract when it is registered
  and MUST reject duplicate names.
- **FR-005**: The registry MUST reject an intent whose `required_tools` names a tool that is
  not registered.
- **FR-006**: The classifier MUST receive the loaded intents (key and description). The core
  MUST NOT hold a fixed list of intent labels.
- **FR-007**: `Harness.answer(image, question)` MUST classify the question, run the chosen
  intent with only the tools it declared, and return an `Answer` with the trace.
- **FR-008**: The harness MUST load parts from module paths. A plugin module MUST expose
  `register(harness, **options)`.
- **FR-009**: `Harness.from_env(path)` MUST read the four `INTENT_HARNESS_*` keys with
  python-dotenv and load tools, then intents, then the classifier.
- **FR-010**: The core package MUST NOT import any concrete tool, intent or classifier.
- **FR-011**: The repo MUST have a `pyproject.toml` that installs every package whose name
  starts with `intent_harness`, with the runtime pins from `requirements.txt` and a `test`
  extra with pytest.

### Key Entities

- **Tool**: a named callable that does one job. A plain function becomes a tool through the
  wrapper.
- **Intent**: a pipeline for one kind of question. It has a key, a description that the
  classifier reads, the names of the tools it needs, and a `run` method.
- **IntentClassifier**: chooses one loaded intent for a question.
- **Choice**: the classifier's result: the key, a probability for each loaded intent, and a
  confidence from 0 to 1.
- **Step**: one tool call in the trace.
- **Answer**: the harness result for one question.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: every acceptance scenario above has a pytest test, and all tests pass.
- **SC-002**: a search of `intent_harness/` finds no import of a tool, intent or classifier
  module.
- **SC-003**: `pip install -e .` in a new `.venv` installs the package, and
  `python -m pytest` passes.

## Assumptions

- A plugin module registers its parts through one function, `register(harness, **options)`.
  This is the only convention the loader needs. Entry points come later.
- Only the classifier module receives an option from the `.env` file: `model`, from
  `INTENT_HARNESS_CLASSIFIER_MODEL`. Tool and intent modules receive no options in this
  feature.
- The trace is collected per call of `answer`. A tool that is called outside `answer` runs
  normally and records nothing.
- `Answer.pipeline` is the name the intent reports in its `Result` for the sub-pipeline it ran
  (for example `"legs"`). When the `Result` has no pipeline name, the answer uses the intent
  key.
- `Answer.value` is whatever the intent returns as its result (a count, "Yes" or "No").
- The core does no image handling; it passes the image object through unchanged.
