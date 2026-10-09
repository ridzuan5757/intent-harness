# Feature Specification: Quantity Intent, Animal Legs

**Feature Branch**: `005-quantity-legs`

**Created**: 2026-10-09

**Status**: Implemented

**Input**: User description: "Add SAM 3 concept segmentation and its duplicate removal as plain
tools, and the quantity intent as a plugin with one pipeline, legs: SAM 3 with the concept
'leg', the nested merge that passed in the experiment, and a count in code. Write the intent so
that a later feature can add more counting pipelines and a selector without a change to the
core. Reproduce the recorded leg counts on the 1,098 animal pairs through the harness."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Count the legs of an animal through the harness (Priority: P1)

A researcher loads the localizer tools and the quantity intent into a harness and asks "How many
legs does this animal have?" about an image. The harness routes the question to the quantity
intent. The legs pipeline finds the animal, finds every leg region with SAM 3, removes duplicate
regions, and counts the regions that remain. No language model writes the number.

**Why this priority**: Counting animal legs is the result of the paper's quantity section: a
localizer that writes no text finds the added leg that the vision-language models miss.

**Independent Test**: With a fake segmenter and a fake box finder registered under the tool
names, the harness answers with the count of distinct regions above the threshold, and the
trace lists each tool call in order.

**Acceptance Scenarios**:

1. **Given** the tools and the quantity intent are loaded and a classifier chooses "quantity",
   **When** the harness answers a leg question about an image, **Then** the answer has intent
   "quantity", pipeline "legs", an integer value, and a trace with the box finder, the
   segmenter, the size filter and the duplicate removal, in that order.
2. **Given** regions where two masks overlap with IoU of at least 0.5, or one mask lies at least
   70% inside a region with a higher score, **When** the duplicate removal runs, **Then** only
   the region with the higher score is counted.
3. **Given** regions with scores below 0.48, **When** the legs pipeline runs, **Then** those
   regions are not counted.

---

### User Story 2 - Show that the SDK keeps the recorded leg counts (Priority: P1)

A reviewer runs the check script on the M3 and compares its counts with the experiment's
`results/07-full-counts.parquet` (arm `sam3`, merge `nms+nested`).

**Why this priority**: The paper reports these numbers. Moving the code into the SDK must not
change what it counts.

**Independent Test**: Run `specs/005-quantity-legs/checks/reproduce_legs.py` on the 2,196 images
of `train-animals.parquet`, then `compare_legs.py` on its output.

**Acceptance Scenarios**:

1. **Given** the full set, **When** the check runs, **Then** originals correct, edited correct,
   and the edited-higher, same and lower pair counts match 0.856, 0.839, 985, 100 and 13, and
   the per-image agreement with the recorded counts is reported.
2. **Given** 5 pairs, **When** the smoke check runs, **Then** it finishes and its counts match
   the recorded counts for those images.

---

### User Story 3 - Add a counting pipeline later without changing the core (Priority: P2)

A later feature (006) adds pipelines for other things to count (board squares, flag stars) and a
selector that chooses among them. It does this inside the quantity intent.

**Why this priority**: The paper's counting scope covers the VLMBias counting sub-topics. The
intent must accept them without a change to `intent_harness/`.

**Independent Test**: A test builds the intent with two fake pipelines and a fake selector and
checks that the selector's choice runs and names the pipeline in the answer.

**Acceptance Scenarios**:

1. **Given** an intent with one pipeline and no selector, **When** it runs, **Then** that
   pipeline runs.
2. **Given** an intent with two pipelines and a selector, **When** it runs, **Then** the
   pipeline that the selector names runs, and `required_tools` is the union of the pipelines'
   tools.
3. **Given** an intent with two pipelines and no selector, **When** it runs, **Then** it raises
   an error that names the pipelines.

### Edge Cases

- No animal box is found: the box is the whole image, as in the experiment.
- SAM 3 returns no region, or every region is below the threshold: the count is 0.
- A mask is empty: the region is dropped (no box can be made).
- More than 150 regions pass the size filter: the 150 with the highest scores are kept.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `intent_harness_tools/sam3.py` MUST give SAM 3 concept segmentation as a plain
  function: image and concept in, a list of regions (box as image fractions, score, full-size
  boolean mask) out. The model loads lazily from the local cache only (`facebook/sam3`).
- **FR-002**: The same module MUST give the region helpers as plain functions: the size filter
  (box area below a fraction of a reference box, highest scores first, at most a limit) and the
  duplicate removal (score threshold, then IoU at or above 0.5, or with the nested rule a share
  inside at or above 0.7, on masks reduced to 128 px on the long side).
- **FR-003**: `intent_harness_tools/grounding_dino.py` MUST give the animal box as a plain
  function: GroundingDINO tiny, query "animal", the box with the highest score as image
  fractions, the whole image when none is found.
- **FR-004**: The tools modules MUST NOT import the core. Importing `intent_harness_tools` MUST NOT
  import torch or transformers.
- **FR-005**: `intent_harness_tools/sam3_plugin.py` and `grounding_dino_plugin.py` MUST register
  the tools by name with `register(harness)`.
- **FR-006**: `intent_harness_quantity/` MUST give the quantity intent (key `quantity`) with the
  pipeline `legs`, and a plugin module with `register(harness)`.
- **FR-007**: The legs pipeline MUST use the settings chosen on originals in the experiment:
  minimum score 0.01, size rule 0.5, at most 150 regions, threshold 0.48, nested merge.
- **FR-008**: The intent MUST hold its pipelines by name and accept an optional selector. Its
  `required_tools` MUST be the union of its pipelines' tools.
- **FR-009**: Laptop tests MUST NOT need a model or the images.
- **FR-010**: The check script MUST run through `Harness.answer`, write its counts outside the
  repository, and resume after an interruption.

### Key Entities

- **Region**: one candidate, a dict with `box` (x1, y1, x2, y2 as image fractions), `score` and
  `mask` (full-size boolean array).
- **CountPipeline**: a named pipeline with `required_tools` and `count(image, question, tools)`.
- **QuantityIntent**: the intent; holds pipelines by name and an optional selector.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All tests pass on the laptop with `.venv/bin/python -m pytest`.
- **SC-002**: On the M3, the SDK counts reproduce originals correct 0.856 and edited correct
  0.839 within 0.005, and the edited-higher, same and lower counts within 5 pairs of 985, 100
  and 13.
- **SC-003**: The per-image agreement with the recorded counts is at least 0.99.

## Reproduction on the M3

To be filled after the run.

## Assumptions

- **The animal box is part of the legs pipeline.** The experiment applied a size rule to every
  localizer: a region counts only when its box is smaller than half the animal box from
  GroundingDINO tiny. The recorded 0.856 depends on it, so GroundingDINO tiny becomes a second
  tool. Its code is in two new files, `grounding_dino.py` and `grounding_dino_plugin.py`, in the
  tools package. No other file of the tools package changes.
- **The pipeline does not read the question.** With one pipeline, the intent counts legs for
  every quantity question. Feature 006 adds the selector that reads the question.
- **The device** is MPS when it is there, then CUDA, then CPU. The experiment ran on MPS.
- **Masks reduced to 128 px** are used only for the duplicate removal, as in the experiment. The
  regions keep their full-size masks.
- **The trace keeps the full regions.** Each step records its output, so a trace of one answer
  holds the masks. This is acceptable for one image at a time.
