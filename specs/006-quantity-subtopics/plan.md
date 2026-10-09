# Implementation Plan: Quantity Intent, VLMBias Counting Sub-topics

**Branch**: `006-quantity-subtopics` | **Date**: 2026-10-09 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/006-quantity-subtopics/spec.md`

## Summary

Move the twelve counters of the experiment's `harness/counting.py` into the quantity intent. The
generic image operations of the experiment's `harness/tools.py` (items 9 to 15) become plain
functions in a new tools file, `intent_harness_tools/counting.py`, named by a new plugin. The
counter logic (board squares, xiangqi crops, flag cloth, star candidates, cell shapes, logo
marks) stays in `intent_harness_quantity/`. A selector tool, `select_counter`, chooses the
counter from the question with an ordered rule table and one aspect-ratio check. The quantity
plugin registers the selector, the thirteen pipelines and the intent.

## Technical Context

**Language/Version**: Python 3.12

**Primary Dependencies**: numpy, scipy, pillow; SAM 3 and GroundingDINO through the registered
tools (`models` extra, loaded only on call); pandas in the check scripts only, from the
experiment environment

**Storage**: board reference crops shipped as `intent_harness_quantity/board_references.npz`
(uint8, about 130 KB); check outputs in `~/Documents/workspace/intent-harness-runs/006/`

**Testing**: pytest; pure tests on drawn figures and fake regions; benchmark tests read
`INTENT_HARNESS_VLMBIAS_DIR` and skip without it

**Target Platform**: macOS laptop (pixel counters); M3 Ultra with MPS (logo smoke check)

**Project Type**: library plugin

**Constraints**: same rules and thresholds as the experiment; no change to the core, README,
requirements or pyproject; small samples only (no full sets)

**Scale/Scope**: 12 counters, 795 gold items (192 development, 603 evaluation); the checks use
5 items per sub-topic plus every counting prompt for the selector

## Constitution Check

- **I. Core knows nothing concrete**: pass. No change to `intent_harness/`. New tools are plain
  functions; the plugin names them; counters call them by name.
- **II. Moved code keeps its numbers**: pass by the sample check (SC-002) and the reference
  check (SC-003). Rules and thresholds are copied unchanged.
- **III. Public repository hygiene**: the staged diff is checked before each commit.
- **IV. Environment**: no new package.
- **V. Scope**: the twelve sub-topics and the selector only.
- **VI. Plain writing**: docstrings and docs in ASD-STE100 style.

## Project Structure

### Documentation (this feature)

```text
specs/006-quantity-subtopics/
├── spec.md
├── plan.md
├── tasks.md
└── checks/
    ├── build_references.py   # rebuild the board references with the experiment code; compare
    ├── check_selector.py     # selector on every counting prompt vs the gold sub-topic
    ├── check_counters.py     # sample per sub-topic through Harness.answer vs the record
    └── RESULT.md             # the measured agreement
```

### Source Code (repository root)

```text
intent_harness_tools/
├── counting.py               # NEW: luminance, colour_runs, line_profile, cluster, box_cells,
│                             #      template_distance, solidity, radial_peaks, palette_labels
└── counting_plugin.py        # NEW: registers them by name

intent_harness_quantity/
├── intent.py                 # selector may be a tool name; no counter -> pipeline "none"
├── plugin.py                 # selector, 13 pipelines, the intent
├── selector.py               # NEW: select_counter, rule table
├── targets.py                # NEW: COUNT_TARGET_RULES, read_target
├── references.py             # NEW: build and load the board references
├── board_references.npz      # NEW: shipped reference crops
├── boards.py                 # NEW: chess_grid, line grids, chess and xiangqi pieces
├── flags.py                  # NEW: flag_stripes, flag_stars
├── cells.py                  # NEW: dice, tally
└── logos.py                  # NEW: car_logos, shoe_logos

tests/
├── test_counting_tools.py    # NEW
├── test_selector.py          # NEW
├── test_counters.py          # NEW (drawn figures)
├── test_counters_benchmark.py  # NEW (skips without images)
└── test_quantity.py          # updated: the plugin now needs the counting tools
```

## Complexity Tracking

| Item | Why | Simpler option rejected because |
|---|---|---|
| Shipped reference crops | the piece counters match squares against crops of the unedited boards | rebuilding them at run time needs the benchmark images, which a user may not have |
| Logo regions converted from full masks to box crops | the experiment's counter works on box crops | changing the counter to full masks risks a different count |
