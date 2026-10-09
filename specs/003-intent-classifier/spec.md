# Feature Specification: Option-Scoring Intent Classifier

**Feature Branch**: `003-intent-classifier`
**Created**: 2026-10-09
**Status**: Implemented
**Input**: Move the option-scoring intent classifier from the experiment workspace into the SDK
as a plugin. It builds its options from the loaded intents and keeps the recorded accuracy.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Classify a question among the loaded intents (Priority: P1)

A user loads intents into a harness and then loads the option-scoring classifier with a
language model. When the harness gets a question, the classifier scores the key of each loaded
intent as the model's reply and chooses the most probable key. Nothing is generated and nothing
is parsed.

**Why this priority**: the harness cannot route a question without a classifier.

**Independent Test**: with a small fake language model, load two intents and the classifier;
the classifier returns the key that the fake model scores highest, with probabilities that sum
to 1 and a confidence from 0 to 1.

**Acceptance Scenarios**:

1. **Given** three loaded intents, **When** a question is classified, **Then** the options are
   exactly the three keys, in the order the intents were loaded, each with its description.
2. **Given** a fourth intent loaded later, **When** a question is classified, **Then** the
   options include the fourth key with no change to the classifier.
3. **Given** the scores, **When** they are turned into probabilities, **Then** the
   probabilities are the softmax of the scores and the confidence is (K * max - 1) / (K - 1).

---

### User Story 2 - Load the classifier as a plugin (Priority: P1)

A user loads the classifier in code with `harness.load_classifier(
"intent_harness_classifiers.option_scoring", model="Qwen/Qwen3-4B")`, or from a `.env` file
with `INTENT_HARNESS_CLASSIFIER` and `INTENT_HARNESS_CLASSIFIER_MODEL`.

**Why this priority**: the core loads every part at runtime; the classifier must follow the
same `register(harness, **options)` pattern.

**Independent Test**: load the plugin module with an option that injects a fake language
model; `Harness.answer` routes to the intent that the fake model prefers.

**Acceptance Scenarios**:

1. **Given** no `model` option, **When** the plugin is loaded, **Then** loading fails with a
   clear error that names the missing option.
2. **Given** a model that is not in the local cache, **When** the plugin is loaded, **Then**
   loading fails and no download starts (`local_files_only=True`).

---

### User Story 3 - Keep the recorded accuracy (Priority: P2)

The experiment workspace recorded option scoring with `qwen3-4b` on the 388-item intent
manifest at accuracy 0.714 (`results/04-choice-qwen3-4b-full.parquet`). Through the SDK path
(ten description-only intents with the same ten definitions, loaded in the same order), the
moved classifier gives the same choice on every item.

**Why this priority**: constitution principle II, moved code keeps its numbers.

**Independent Test**: the check script `specs/003-intent-classifier/checks/reproduce_qwen3_4b.py`
runs on the M3 and compares each item's choice and log scores with the recorded file.

**Acceptance Scenarios**:

1. **Given** the first 10 items of the manifest, **When** the check runs through the SDK,
   **Then** the choice agrees with the recorded file on every item and the log scores agree to
   the 4 decimals of the recorded file.
2. The full 388-item reproduction (recorded accuracy 0.714, 277 of 388) is not part of this
   feature. Build features do not run full sets; it runs in feature 007's notebooks on the M3.

### Edge Cases

- One loaded intent: the classifier returns it with probability 1 and confidence 1.
- No loaded intent: the harness raises before it calls the classifier (core behaviour).
- An intent key that takes several tokens: its score is the sum of the log-probabilities of its
  tokens, as in the experiment (no length correction).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The package `intent_harness_classifiers` MUST provide the plugin module
  `option_scoring` with `register(harness, model=..., **options)`.
- **FR-002**: The classifier MUST follow the core `IntentClassifier` contract:
  `classify(question, intents) -> Choice`, with the options built from the given intents' keys
  and descriptions. It MUST NOT hold a fixed list of labels.
- **FR-003**: The prompt MUST be the experiment's prompt shape: the question text labelled
  "Text", the instructions, the options with their descriptions, and "Answer with the option
  name only." The default instructions MUST be the experiment's text.
- **FR-004**: The language model adapter MUST load with `local_files_only=True`, use the
  model's chat template with thinking turned off, and score each option text as the start of
  the reply in one batched forward pass (teacher forcing).
- **FR-005**: Probabilities MUST be the softmax of the log scores; confidence MUST be
  (K * max - 1) / (K - 1), and 1.0 when K is 1.
- **FR-006**: The plugin MUST accept an injected language model object (for tests and for
  other back ends) that has `option_log_probabilities(prompt, options)`.
- **FR-007**: The package MUST NOT import torch or transformers at import time; they load only
  when a real model is loaded.

### Key Entities

- **OptionScoringClassifier**: holds a language model and the instructions; classifies a
  question among the given intents.
- **LanguageModel**: loads a causal language model from the local cache and scores option texts.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All laptop tests pass with a fake language model and no model download.
- **SC-002**: Through the SDK path, `Qwen/Qwen3-4B` on the first 10 manifest items gives the
  same choice as the recorded file on 10 of 10 items. The full 388-item check (0.714) belongs to
  feature 007.
- **SC-003**: Importing `intent_harness_classifiers` does not import torch or transformers.

## Assumptions

- Only causal (text-only) language models are supported in this feature. The experiment also
  ran vision-language models on text alone; that path is not needed for the paper's classifier.
- The `model` option is the HuggingFace id or a local path (for example `Qwen/Qwen3-4B`), not
  the experiment's short name (`qwen3-4b`).
- Options `device` (default `mps`) and `dtype` (default `bfloat16`) select where and how the
  model runs; `instructions` replaces the default instructions.
- The reproduction data (the manifest) is not committed; the check script reads it from a path
  given on the command line.

## Reproduction result

Smoke check, run on the M3 on 2026-10-09 with
`specs/003-intent-classifier/checks/reproduce_qwen3_4b.py --limit 10` (`Qwen/Qwen3-4B`, MPS,
bfloat16). Outputs are kept outside the repository.

| Measure | Result |
|---|---|
| Items | 10 (the first 10 of the 388-item manifest) |
| Same choice as the recorded file | 10 / 10 |
| Accuracy through the SDK | 7 / 10 = 0.700 |
| Recorded accuracy on the same items | 7 / 10 = 0.700 |
| Largest log-score difference | 0.0001 (the recorded scores are rounded to 4 decimals) |

The SDK path gives the same scores as the experiment on these items. The full 388-item
reproduction against the recorded 0.714 runs in feature 007's notebooks on the M3.
