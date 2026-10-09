# Feature Specification: Measurement Tools

**Feature Branch**: `002-tools`

**Created**: 2026-10-09

**Status**: Implemented

**Input**: User description: "Move the eight illusion measurement tools and their drawing helpers
into a standalone tools package of plain functions. The package does not depend on the core.
Port the drawn-shape checks of the experiment (116 checks, all inside limits set before they
ran) to automatic tests, and keep the same numbers."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Measure a drawn figure with plain functions (Priority: P1)

A researcher or a later pipeline loads an image of a drawn figure and measures it with the tools:
the pixels of one colour, the separate shapes, the long straight runs, the strokes along one
direction, the diameter of a disc, the straight line through a shape, the distance from a point
to a line, and the Yes or No decision against a tolerance. Each tool is a plain function. It
takes normal values (an image, an array, numbers) and gives normal values back.

**Why this priority**: Every illusion pipeline in the paper is a fixed sequence of these tools.
Without them, no later feature can measure anything.

**Independent Test**: Import the tools package alone, with no other package of this repository
installed, and measure a figure drawn in the test.

**Acceptance Scenarios**:

1. **Given** a 384 px image with one horizontal black stroke of known length, **When** the dark
   colour mask and the line-segment finder run on it, **Then** one segment comes back and its
   length is within 2 px of the known length.
2. **Given** two red discs of known diameter, **When** the red colour mask, shape grouping and
   area-to-diameter run, **Then** two shapes come back and each diameter is within 1.5 px.
3. **Given** a quantity and a tolerance, **When** the decision tool runs, **Then** it answers
   "Yes" when the absolute quantity is at or below the tolerance, and "No" otherwise.

---

### User Story 2 - Show that the moved tools keep the recorded numbers (Priority: P1)

A reviewer runs the automatic tests and sees the same checks as the experiment's notebook 13:
116 checks on shapes drawn with a known answer, at the three benchmark sizes (384, 768 and
1152 px), every one inside the limit set before the checks ran.

**Why this priority**: The paper reports results computed with these tools. Moving the code must
not change what it measures.

**Independent Test**: Run the test suite of the tools package. It reports 116 checks passed and
the largest error per tool.

**Acceptance Scenarios**:

1. **Given** the moved tools, **When** the tests run, **Then** all 116 checks pass with the same
   limits as notebook 13: 2.0 px for lengths, 1.5 px for diameters, 0.3 degrees for angles,
   1.5 px for distances, 1 px for stroke thickness, and exact for shape counts, colour masks and
   decisions.
2. **Given** the moved tools, **When** the tests run, **Then** the largest errors are the same
   as in notebook 13: 0.8 px for lengths, 0.17 px for diameters, 0.06 degrees for line angles,
   0.12 degrees after the direction filter, and 0.17 px for distances.

---

### User Story 3 - Draw test shapes with a known answer (Priority: P2)

A tool author draws strokes and discs with known positions and sizes, at four times the target
size and then shrunk, so that the edges are soft like the benchmark figures.

**Why this priority**: The checks in User Story 2 and the checks of any new tool need shapes with
a known answer.

**Independent Test**: Draw a segment at a known angle and a disc of known diameter, and confirm
the image size and the colour of the shape.

**Acceptance Scenarios**:

1. **Given** a size, a list of segments and a stroke width, **When** the segment drawing helper
   runs, **Then** it returns an RGB image of that size with the strokes in the given colour.
2. **Given** a centre, a length and an angle, **When** the segment helper runs, **Then** it
   returns the two end points of a segment through the centre at that angle, rising to the right
   for a positive angle.

### Edge Cases

- A mask with no marked pixels: shape grouping returns an empty list, and the line-segment finder
  returns no segments.
- Shapes smaller than the minimum pixel count are dropped by shape grouping.
- Runs shorter than the minimum length are dropped by the line-segment finder.
- An unknown colour name or an unknown axis name raises an error that names the accepted values.
- A quantity exactly equal to the tolerance answers "Yes".

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The tools package MUST provide the eight measurement tools of the experiment:
  colour mask, shape grouping, line-segment finder, stroke-direction filter, area to diameter,
  line fit, point-to-line distance and the tolerance decision.
- **FR-002**: The tools package MUST provide the drawing helpers used to make test shapes:
  segments, discs and a segment at a given angle.
- **FR-003**: Each tool MUST be a plain function that takes normal values and returns normal
  values. It MUST NOT know about tool names, traces, registration or intents.
- **FR-004**: The tools package MUST NOT import the core package or any other package of this
  repository.
- **FR-005**: Each tool MUST give the same output as the experiment code for the same input.
- **FR-006**: The automatic tests MUST contain the 116 drawn-shape checks of notebook 13, with
  the same cases, sizes and limits, and MUST report the largest error per tool.
- **FR-007**: The tools package MUST use only packages that are already pinned in
  `requirements.txt` (numpy, scipy, pillow).
- **FR-008**: The counting tools, the illusion pixel rules, the pipelines and the SAM 3 code MUST
  NOT be part of this feature.

### Key Entities

- **Mask**: a two-dimensional true/false array, one value per pixel.
- **Shape**: one connected group of marked pixels, with its pixel count, coordinates, bounding
  box and centroid.
- **Segment**: one long straight run of a mask along rows or columns, with its position, first
  and last line, thickness, start, end and length.
- **Line**: the straight line through a shape, with its centre, direction, angle and two end
  points.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 116 of 116 drawn-shape checks pass, each inside the limit set before it ran.
- **SC-002**: The largest error per tool matches notebook 13 to the reported precision.
- **SC-003**: The tools package imports and its tests run with only the packages in
  `requirements.txt`, and with no other package of this repository present.
- **SC-004**: The full test run takes less than one minute on a laptop.

## Assumptions

- The reference-original part of notebook 13 (section 10, the six pipelines on 18 benchmark
  images) is not ported. It needs the pipelines and the benchmark images, which belong to the
  structural feature (004).
- The Zöllner direction-filter length of 41 px is a pipeline constant in the experiment. The
  tests use the same value as a test constant; the pipeline constant moves with feature 004.
- The package name is `intent_harness_tools`. Packaging (`pyproject.toml`) belongs to feature
  001. Tests run from the repository root with `python -m pytest`, which puts the root on the
  import path.
- The colour thresholds are the feature 002 thresholds of the experiment and do not change.
