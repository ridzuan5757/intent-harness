# Feature Specification: Structural Intent

**Feature Branch**: `004-structural`

**Created**: 2026-10-09

**Status**: Implemented

**Input**: User description: "The structural intent as a plugin: the illusion classifier by
pixel rules selects one of six per-illusion measurement pipelines; the pipelines call the
measurement tools by name; the decision uses the frozen tolerances. Also a plugin module that
registers the eight measurement tools under stable names. Keep the recorded numbers."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Answer an illusion question through the harness (Priority: P1)

A developer loads the measurement tools and the structural intent into a `Harness` and asks
the VLMBias question for an optical illusion image. The harness returns `Yes` when the two
compared parts are equal within the tolerance and `No` when they differ. The answer names the
illusion as its pipeline, and the trace shows each tool step.

**Why this priority**: this is the paper's structural result, now through the SDK.

**Independent Test**: load both plugins and a fixed classifier that always chooses
`structural`; answer a drawn figure with a known answer; check the value, the pipeline and the
trace.

**Acceptance Scenarios**:

1. **Given** a drawn figure with two equal horizontal segments, **When** it is answered,
   **Then** the value is `Yes`.
2. **Given** the same figure with one segment 30% longer, **When** it is answered, **Then**
   the value is `No`.
3. **Given** any answer, **When** the trace is read, **Then** it starts with the illusion
   pixel-rule step, holds the tool steps of the selected pipeline in call order, and ends
   with the `decide` step.

---

### User Story 2 - Name the illusion from the image (Priority: P1)

Inside the intent, the pixel rules read the image and name one of six illusions, or `none`.
The name selects the pipeline. This choice is internal to the intent; the core does not
change.

**Why this priority**: without the right name, the wrong pipeline measures the figure.

**Independent Test**: drawn figures with the shapes that each rule reads; the benchmark
images when they are available.

**Acceptance Scenarios**:

1. **Given** two red discs, **When** the rules run, **Then** the name is `ebbinghaus`.
2. **Given** a figure that no rule matches, **When** it is answered, **Then** the pipeline is
   `none` and the value is `None`.

---

### User Story 3 - Register the measurement tools under stable names (Priority: P2)

A developer loads `intent_harness_tools.measurement_plugin`. It registers the eight
measurement tools under their function names: `colour_mask`, `group_shapes`, `find_runs`,
`direction_filter`, `equivalent_diameter`, `fit_line`, `point_line_distance`, `decide`.

**Why this priority**: the structural intent needs these names; other intents can use them.

**Independent Test**: load the module into a harness and list the registered names.

**Acceptance Scenarios**:

1. **Given** an empty harness, **When** the module is loaded, **Then** eight tools with the
   names above are registered.
2. **Given** the structural intent, **When** it is loaded before the tools, **Then**
   registration fails and names the missing tools.

---

### User Story 4 - Keep the recorded numbers (Priority: P1)

A maintainer runs the check script on the 396 VLMBias illusion images. The SDK path gives the
same numbers that the experiment recorded.

**Why this priority**: constitution Principle II, moved code keeps its numbers.

**Independent Test**: `specs/004-structural/checks/reproduce.py` with the image directory set.

**Acceptance Scenarios**:

1. **Given** the 396 images, **When** the pixel rules run, **Then** 396 of 396 are named
   correctly.
2. **Given** the 396 images, **When** they are answered through the harness, **Then** the
   accuracy per illusion is: Müller-Lyer 36/36 originals and 36/36 edited, Ponzo 36/36 and
   24/36, Vertical-Horizontal 18/18 and 18/18, Ebbinghaus 36/36 and 36/36, Poggendorff 36/36
   and 36/36, Zöllner 36/36 and 36/36.
3. **Given** the recorded experiment results, **When** they are compared item by item,
   **Then** the answer and the measured quantity agree for every item.
4. **Given** the first original figure of each illusion at three sizes, **When** it is
   measured, **Then** the quantity matches notebook 13 section 10.

### Edge Cases

- A pipeline cannot find its shapes (for example not two segments): the value is `None` and
  the trace shows the steps that ran. In the recorded results this did not happen (396 of 396
  measured).
- Ponzo, smallest edit (0.15): 12 of 36 edited images are answered `Yes`. Two 384 px
  originals measure too long, which sets the tolerance above that edit. This is a recorded
  limitation; the answer stays binary (user decision, 2026-10-09).
- Ebbinghaus and Zöllner have a tolerance of 0. That holds for figures from this generator
  only.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `intent_harness_tools/measurement_plugin.py` MUST expose `register(harness)` that
  registers the eight measurement tools under their function names. It is a new file; no
  other file in `intent_harness_tools/` changes.
- **FR-002**: Package `intent_harness_structural/` MUST expose a plugin module with
  `register(harness)` that registers the tool `illusion_pixel_rules` and the intent
  `structural`.
- **FR-003**: The intent MUST have key `structural`, a description of the questions it
  answers, and `required_tools` = the eight measurement tools plus `illusion_pixel_rules`.
- **FR-004**: The intent MUST get every tool from the mapping it receives, by name. It MUST
  NOT import `intent_harness_tools`.
- **FR-005**: The pixel rules, thresholds and descriptions MUST be moved unchanged from the
  experiment (`harness/classifiers.py`, `harness/illusions.py`).
- **FR-006**: The six pipelines MUST be moved from the experiment (`harness/pipelines.py`)
  with the same tool sequence and the same arithmetic; only the tool access changes.
- **FR-007**: The tolerances MUST be constants equal to the recorded values, with their
  source file named.
- **FR-008**: `run` MUST return `Result(value, pipeline)`: value `Yes`, `No` or `None`;
  pipeline = the illusion key or `none`.
- **FR-009**: The core (`intent_harness/`), `README.md`, `requirements.txt` and
  `pyproject.toml` MUST NOT change. No new package.
- **FR-010**: Tests that need the benchmark images MUST be skipped when
  `INTENT_HARNESS_VLMBIAS_DIR` is not set.

### Key Entities

- **Illusion**: key, name, description (what is drawn), the VLMBias image folder.
- **Measurement**: value_a, value_b, quantity, and whether the shapes were found.
- **Tolerance**: one frozen number per illusion, with its source.

## Success Criteria *(mandatory)*

- **SC-001**: The pixel rules name 396 of 396 images through the intent.
- **SC-002**: The per-illusion accuracies equal the recorded ones (User Story 4).
- **SC-003**: Per item, the answer and the quantity agree with the recorded results for all
  396 items (quantity within 1e-9).
- **SC-004**: All tests pass; the benchmark tests pass when the images are present.
- **SC-005**: Nothing committed mentions the coding assistant.

## Assumptions

- **Question text**: the intent does not read the question. The illusion named from the image
  fixes which VLMBias question is answered. A later feature may check the question.
- **Not found**: the experiment answered `not found`; the SDK returns `None` so that the value
  is always `Yes`, `No` or `None`.
- **Trace**: the pixel-rule step is a registered tool, `illusion_pixel_rules`, so the trace
  shows which illusion was chosen. The arithmetic steps (relative difference, junction
  correction, distance ratio, angle difference) are plain code, not tools.
- **Ground truth for the check**: an image with `diff0` in its file name is an original
  (answer `Yes`); every other image is edited (answer `No`). The illusion is the image
  folder. This gives the same 396 items and gold answers as the experiment manifest.
- **Image root**: `INTENT_HARNESS_VLMBIAS_DIR` points to the `benchmark-main` folder of the
  VLMBias dataset. The images are not committed.
- **Recorded results**: `checks/compare_recorded.py` compares item by item when
  `INTENT_HARNESS_RECORDED_DIR` points to the experiment's `results/` folder. It reads parquet
  with pandas, which the SDK does not depend on, so it runs with any Python that has pandas.
- **Result**: see `checks/RESULT.md`. All recorded numbers are reproduced: 396/396 names, the
  six accuracy pairs, 396/396 items with the same answer and the same quantity (largest gap
  4.4e-16), and notebook 13 section 10.
- **No SAM 3 arm**: the experiment allowed a SAM 3 mask function; it is not moved (Ponzo
  stays a recorded limitation).
