# Tasks: Quantity Intent, VLMBias Counting Sub-topics

**Input**: spec.md and plan.md in `specs/006-quantity-subtopics/`

## Phase 1: Tools

- [X] T001 Move the generic image operations (luminance, colour_runs, line_profile, cluster,
  box_cells, template_distance, solidity, radial_peaks, palette_labels) into
  `intent_harness_tools/counting.py`, unchanged
- [X] T002 Add `intent_harness_tools/counting_plugin.py` that registers them by name
- [X] T003 [P] Tests for the counting tools on fixed arrays in `tests/test_counting_tools.py`

## Phase 2: User Story 1 - Counters and selector (P1)

- [X] T004 `intent_harness_quantity/targets.py`: the target rules and `read_target`
- [X] T005 `intent_harness_quantity/references.py`: build, save and load the board references;
  ship `board_references.npz`
- [X] T006 `boards.py`, `flags.py`, `cells.py`, `logos.py`: the twelve counters as pipelines that
  call tools by name; None when the target is not found
- [X] T007 `selector.py`: `select_counter` with the rule table and the aspect check
- [X] T008 `intent.py`: a selector given as a tool name; no counter gives pipeline `none`
- [X] T009 `plugin.py`: register the selector tool, the thirteen pipelines and the intent
- [X] T010 [P] Tests: selector rules, counters on drawn figures and fake regions, the harness path
  and its trace; update `tests/test_quantity.py`

## Phase 3: User Stories 2 and 3 - Checks (P1)

- [X] T011 `checks/build_references.py`: the shipped references equal the experiment's
  `board_references()` (SC-003)
- [X] T012 `checks/check_selector.py`: every counting prompt vs the gold sub-topic (SC-001)
- [X] T013 `checks/check_counters.py`: 5 items per pixel sub-topic on the laptop vs the record
  (SC-002); `tests/test_counters_benchmark.py` with the same sample, skipped without images
- [X] T014 M3 smoke: a few car and shoe logo items through `Harness.answer` vs the record
- [X] T015 Record the results in `checks/RESULT.md` and the spec

## Phase 4: Polish

- [X] T016 pytest with and without `INTENT_HARNESS_VLMBIAS_DIR`; grep the diff; rebase; PR
