# Feature Specification: Quantity Intent, VLMBias Counting Sub-topics

**Feature Branch**: `006-quantity-subtopics`
**Created**: 2026-10-09
**Status**: Implemented
**Input**: Move the twelve VLMBias counting sub-topic counters of the experiment workspace
(`grounded-count-harness`, spec 004, notebooks 21 to 27) into the quantity intent as named
pipelines, and add the selector that chooses a counter from the question (user decision
2026-10-09: text rules plus one image check).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Count a VLMBias counting image through the harness (Priority: P1)

A researcher gives the harness an image and its VLMBias counting question, for example "How
many stripes are there in this flag?". The quantity intent chooses the counter for the question,
the counter counts in code, and the answer gives the count, the counter name and a trace of every
step, the selector included.

**Why this priority**: this is the paper's quantity scope beyond animal legs.

**Independent Test**: load the counting tools, the SAM 3 and GroundingDINO tools, and the quantity
intent; ask a VLMBias question on a VLMBias image; the answer has the counter name as its
pipeline and the recorded count as its value.

**Acceptance Scenarios**:

1. **Given** a flag image and "How many stripes are there in this flag?", **When** the harness
   answers, **Then** the pipeline is `flag_stripes`, the value is the recorded count, and the
   first quantity step in the trace is `select_counter`.
2. **Given** a dice image and "How many circles are there in cell C3?", **When** the harness
   answers, **Then** the pipeline is `dice` and the count is the count in cell C3.
3. **Given** a question that no rule matches, **When** the harness answers, **Then** the pipeline
   is `none` and the value is None.

---

### User Story 2 - Show that the SDK keeps the recorded counts (Priority: P1)

The moved counters must give the same count as the experiment, item by item, on a small sample of
each sub-topic, known failures included. The full-set numbers come from feature 007.

**Why this priority**: the constitution (Principle II) requires item-by-item agreement on a
sample before a move is merged.

**Independent Test**: a check script runs a sample of each sub-topic through `Harness.answer`
and compares each count with `results/23..27-*.parquet` of the experiment.

**Acceptance Scenarios**:

1. **Given** 5 items per pixel sub-topic (laptop), **When** the check runs, **Then** every count
   equals the recorded count.
2. **Given** a few car and shoe logo items (SAM 3 on the M3), **When** the smoke check runs,
   **Then** every count equals the recorded count.

---

### User Story 3 - Check the selector on every counting prompt (Priority: P1)

The selector must choose the right counter for every VLMBias counting prompt, so that the paper's
counting numbers do not depend on the benchmark's sub-topic label.

**Independent Test**: a check script runs the selector on every counting prompt of
`benchmark-main` and `benchmark-original` (identification prompts "What ... is this?" left out)
and compares its choice with the gold sub-topic.

**Acceptance Scenarios**:

1. **Given** every counting prompt with its image, **When** the selector runs, **Then** it
   chooses the gold sub-topic (animal prompts: `legs`) for every prompt.

### Edge Cases

- A target that the counter cannot find (no flag cloth, no named cell, no logo region): the
  value is None, as structural does. The experiment wrote -1 for this case.
- "Knight pieces" is a piece of both chess and xiangqi; "horizontal lines on this board" is a
  question of both go and xiangqi. The image check splits both (FR-006).
- A question that names a cell that the grid does not have: the value is None.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The quantity intent MUST hold thirteen named pipelines: `legs` (feature 005) and
  `chess_grid`, `sudoku_grid`, `xiangqi_grid`, `go_grid`, `chess_pieces`, `xiangqi_pieces`,
  `flag_stars`, `flag_stripes`, `dice`, `tally`, `car_logos`, `shoe_logos`.
- **FR-002**: Each counter MUST give the same count as the experiment's `harness/counting.py` on
  the same image and target: same rules, same frozen thresholds.
- **FR-003**: Each counter MUST read its target from the question with the experiment's target
  rules (`COUNT_TARGET_RULES`): all pieces, one kind, a named cell, rows, columns, horizontal or
  vertical lines, stars, stripes, star points, prongs, overlapping circles, shoe element.
- **FR-004**: Generic image operations MUST be plain functions in a new tools file and be
  registered by name by a plugin; the counters MUST call them by name from the registry.
- **FR-005**: The logo counters MUST get SAM 3 regions through the registered tool
  `segment_concept`, not by import.
- **FR-006**: The selector MUST be a registered tool, `select_counter(image, question)`, so its
  choice is a trace step. It MUST choose by rules on the question; the two text ties ("Knight
  pieces", "horizontal/vertical lines on this board") MUST be split by one image check. A
  question no rule matches MUST give no counter.
- **FR-007**: The chess and xiangqi piece counters MUST use the experiment's reference crops,
  shipped with the package, and a check MUST show they equal the crops the experiment builds.
- **FR-008**: The core (`intent_harness/`), README, requirements and pyproject MUST NOT change.

### Key Entities

- **Counting pipeline**: `name`, `required_tools`, `count(image, question, tools)` that returns
  an int, or None when the target is not found.
- **Selector rule table**: ordered rules, first match wins (see "Selector rules").
- **Board references**: grey 32 x 32 crops of the unedited chess and xiangqi boards, with their
  piece kind, and the xiangqi intersection grid.

## Selector rules

Derived from every counting prompt in `benchmark-main.parquet` and `benchmark-original.parquet`.
Applied in order to the question; the first match wins.

| # | Rule on the question | Counter |
|---|---|---|
| 1 | "leg" or "legs" | `legs` |
| 2 | "in cell X9" and "circles" | `dice` |
| 3 | "in cell X9" and "lines" | `tally` |
| 4 | "chess pieces", or King, Queen, Rook, Bishop or Pawn "pieces" | `chess_pieces` |
| 5 | "xiangqi pieces", or General, Advisor, Elephant, Horse, Chariot, Cannon or Soldier "pieces" | `xiangqi_pieces` |
| 6 | "Knight pieces" | image check: `xiangqi_pieces` if tall, else `chess_pieces` |
| 7 | "horizontal lines" or "vertical lines" | image check: `xiangqi_grid` if tall, else `go_grid` |
| 8 | "rows" or "columns", and "puzzle" | `sudoku_grid` |
| 9 | "rows" or "columns", and "board" | `chess_grid` |
| 10 | "logo" and "car" | `car_logos` |
| 11 | "logo" and "shoe" | `shoe_logos` |
| 12 | "flag" and "stars" | `flag_stars` |
| 13 | "flag" and "stripes" | `flag_stripes` |

**Image check**: the image is "tall" when its height is more than 1.06 times its width. Every
VLMBias xiangqi image is 1.125 times as tall as it is wide; every chess and go image is square
(checked on all 234 board images of the gold table).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The selector chooses the gold sub-topic on 100% of the counting prompts.
- **SC-002**: On the sample, every count equals the recorded count, known failures included.
- **SC-003**: The shipped board references equal the experiment's `board_references()` exactly.
- **SC-004**: All tests pass, with and without `INTENT_HARNESS_VLMBIAS_DIR`.

## Verification (2026-10-09)

Small samples only; the full sets run in feature 007's notebooks on the M3. Details:
`checks/RESULT.md`.

- **SC-001**: the selector chooses the gold sub-topic on 2,155 of 2,155 counting prompts.
- **SC-002**: 64 of 64 sampled items give the recorded count through `Harness.answer`: 50 pixel
  items on the laptop (5 per sub-topic, 6 of them recorded errors) and 14 logo items with SAM 3
  on the M3 (6 of them recorded errors; every car target is in the sample).
- **SC-003**: the shipped board references equal the experiment's crops exactly.
- **SC-004**: pytest: 271 passed and 23 skipped without `INTENT_HARNESS_VLMBIAS_DIR`; 294 passed
  with it.

## Assumptions

- Recorded counts are the experiment's `results/23..27-*.parquet` (column `count`, -1 when not
  found). The SDK value None stands for -1.
- The image check (aspect ratio) is fitted to the VLMBias rendering; it is the only image check.
- The board references are derived from two benchmark images (the unedited chess and xiangqi
  boards) and are shipped as uint8 arrays (lossless: the experiment's crops are resized uint8
  images).
- The logo counters call SAM 3 with the concepts the experiment cached ("car logo" and
  "emblem" for cars, "shoe" for shoes) and the cache's minimum score, 0.05. The concept "logo"
  of the shoe cache was not used by the counter and is not called.
- Each counter answers the question it is given; it does not check that the image belongs to its
  sub-topic.
- The counting plugin also registers `group_shapes` and `fit_line` (the shoe and cell counters
  need them) when no other plugin has registered them.
- The piece counters call one new tool, `nearest_template`, in place of the experiment's private
  `_nearest` loop over `template_distance`; the loop is the same. One trace step per square
  keeps the trace short (the xiangqi counter would otherwise record 8,100 distance steps).
- The quantity plugin now registers all thirteen pipelines, so loading it needs the counting,
  GroundingDINO and SAM 3 tools. The leg tests were updated to load the counting tools.
