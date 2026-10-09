# Feature Specification: Paper Notebooks

**Feature Branch**: `007-paper-notebooks`
**Created**: 2026-10-09
**Status**: Implemented
**Input**: Produce every paper number of the harness through the SDK, on the full sets, on the
M3. The build features 001 to 006 checked small samples only; this feature runs everything. Paper
scope: the intent classifier, the quantity intent (animal legs and the twelve VLMBias counting
sub-topics) and the structural intent (illusions). The vision-model direct-answer baseline is not
in scope (feature 008).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Reproduce each paper table from one notebook (Priority: P1)

A reader clones the repository, sets the data folder, and opens a notebook. The notebook reads
the result files that a script wrote and shows the table. Each table comes from the SDK only.

**Why this priority**: the paper's numbers must come from the code that the paper publishes.

**Independent Test**: execute a notebook with the committed result files; it shows its table
without a model or an image.

**Acceptance Scenarios**:

1. **Given** the result files in `results/`, **When** notebook 01 runs, **Then** it shows, for
   24 models, the accuracy on the 388 prompts and the mean confidence on right and wrong answers.
2. **Given** the result files, **When** notebooks 02 to 04 run, **Then** they show the illusion
   naming and measurement accuracy, the leg-count table and the per-sub-topic counting table.

---

### User Story 2 - Run the full sets on the M3 with resumable scripts (Priority: P1)

A researcher starts one script per set on the M3. The script writes one line per item as it
goes, continues after a stop, and writes a result file and a completion marker at the end.

**Why this priority**: the runs take hours; a stop must not lose work or mix a partial file into
a table.

**Independent Test**: start a script with `--limit`, stop it, start it again; it continues and
writes the result file and the marker only when every item is done.

**Acceptance Scenarios**:

1. **Given** a smoke run on a few items, **When** it ends, **Then** its file is separate from the
   full-run file and has no marker of a full run.
2. **Given** an incomplete run, **When** a notebook reads the results, **Then** it refuses the
   file and says that the run is not complete.

---

### User Story 3 - Compare with the experiment, item by item (Priority: P1)

Each notebook compares its numbers with the recorded experiment files, item by item, when the
folder of the recorded files is set.

**Why this priority**: the move into the SDK must keep the experiment's numbers; any difference
must be found and explained.

**Independent Test**: with `INTENT_HARNESS_RECORDED_DIR` set, each notebook prints the number of
items with the same answer as the recorded file.

---

### User Story 4 - Answer the VLMBias benchmark end to end (Priority: P2)

The harness, with the qwen3-4b option-scoring classifier choosing between the loaded intents
(quantity and structural), answers every VLMBias benchmark prompt of the paper's scope, and the
notebook reports routing accuracy, answer accuracy and where each error comes from.

**Why this priority**: this is the system number that feature 008 compares with the vision
models' own answers.

**Independent Test**: notebook 05 reads the end-to-end result file and shows the tables.

### Edge Cases

- A model that fails to load: the script records the failure and continues with the next model.
- A counter that finds no target: the value is None and the answer is wrong.
- An item whose image is missing: the script stops with the item id.
- A question that the classifier routes to the wrong intent: the answer is wrong; the notebook
  counts it as a routing error.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `.env.paper` at the repository root MUST list the classifier, its model, the tools
  and the intents that the paper loads. It MUST hold no machine path and no secret.
- **FR-002**: Data locations MUST come from environment variables (or a git-ignored `.env`):
  `INTENT_HARNESS_DATA_DIR` (the VLMBias data folder), `INTENT_HARNESS_RESULTS_DIR` (default
  `results/`), `INTENT_HARNESS_RECORDED_DIR` (optional, the experiment's result files).
- **FR-003**: The option-scoring classifier MUST also load a vision-language model and use it on
  text only, as the experiment's adapter did, so that all 24 models run through the SDK.
- **FR-004**: Each full set MUST run through `Harness.answer` (or, for the classifier table,
  through the loaded classifier's `classify` with the ten recorded intent definitions).
- **FR-005**: Each script MUST be resumable (one JSON line per item), MUST write a separate file
  for a smoke run, and MUST write a completion marker only when every item is done.
- **FR-006**: Notebooks MUST read result files only, MUST refuse incomplete files, and MUST be at
  or below 600 KB.
- **FR-007**: The item lists (prompts, image paths, gold answers) MUST ship in `data/`; images do
  not ship.
- **FR-008**: Nothing committed may mention the coding assistant.

### Key Entities

- **Item list**: one row per item: id, image path relative to the data folder, question, gold
  answer, and the set's own columns (sub-topic, split, condition, pixel size).
- **Result file**: one row per item with the SDK's answer, pipeline, value and the time; plus a
  `.done` marker that holds the item count and the end time.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Notebook 01 shows 24 models on 388 prompts; for each model the choice equals the
  recorded experiment choice on at least 99% of items (differences are explained).
- **SC-002**: Notebook 02: the pixel rules name 396 of 396 images; measurement accuracy per
  illusion equals the record (Ponzo 24 of 36 edited).
- **SC-003**: Notebook 03: 1,098 pairs; originals and edited accuracy and higher/same/lower counts
  equal the record (0.856, 0.839, 985/100/13) or the difference is explained item by item.
- **SC-004**: Notebook 04: 795 items; per sub-topic evaluation accuracy equals the record (453 of
  603 overall); the selector chooses the gold sub-topic for every item.
- **SC-005**: Notebook 05: every benchmark prompt in scope has an answer; routing accuracy, answer
  accuracy and the error sources are reported.
- **SC-006**: A case-insensitive search for the coding assistant's name finds nothing in the
  committed files.

## Assumptions

- The 24 models are the 25 of the experiment registry without `llava-ov-72b` (user decision
  2026-10-09). Each loads with the dtype that the experiment used.
- The classifier table uses the experiment's ten intent definitions (Eyes Wide Shut patterns plus
  `other`) as ten description-only intents, so that it compares with the record. The end-to-end
  run (notebook 05) uses the real loaded intents: quantity and structural only.
- The leg set is the 1,098-pair linear-probing split (`train-animals.parquet`), as in the
  experiment; the question is "How many legs does this animal have?", as in feature 005.
- The end-to-end set is every prompt of `benchmark-main.parquet` (VLMBias, 2,784 prompts on
  1,392 images, two prompts per image), all seven topics. An answer is correct when its value as
  text equals `ground_truth`.
- Notebooks execute on the laptop after the result files are pulled from the M3; the scripts run
  on the M3 with the M3's existing environment and the PYTHONPATH set to a copy of this branch.
