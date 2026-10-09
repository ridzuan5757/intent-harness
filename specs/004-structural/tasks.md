# Tasks: Structural Intent

**Input**: [spec.md](spec.md), [plan.md](plan.md)

**Tests**: pytest. Drawn-figure tests always run; benchmark tests need `INTENT_HARNESS_VLMBIAS_DIR`.

## Phase 1: Tools plugin (User Story 3)

- [X] T001 [US3] Write `intent_harness_tools/measurement_plugin.py`: `TOOL_NAMES` and
  `register(harness)` for the eight measurement tools, under their function names

## Phase 2: Moved code (User Stories 1, 2)

- [X] T002 [P] [US2] Write `intent_harness_structural/illusions.py`: the seven classes moved
  unchanged, plus the VLMBias image folder of each
- [X] T003 [P] [US2] Write `intent_harness_structural/pixel_rules.py`: thresholds, ordered
  rules, `pixel_features`, `matched_rules`, `classify_image`, `rules_hash`; moved unchanged
- [X] T004 [P] [US1] Write `intent_harness_structural/tolerances.py`: the six frozen
  tolerances with their source files
- [X] T005 [US1] Write `intent_harness_structural/pipelines.py`: `Measurement` and the six
  `measure_*` functions on a tools mapping; same tool sequence and arithmetic as the experiment
- [X] T006 [US1] Write `intent_harness_structural/intent.py` (`StructuralIntent`),
  `plugin.py` (`register`) and `__init__.py`

## Phase 3: Tests

- [X] T007 [US1, US2, US3] Write `tests/structural_figures.py` and `tests/test_structural.py`:
  tool registration, load order error, rules on drawn figures, Yes/No on drawn figures, trace
  order, `none` case, no import of `intent_harness_tools` in the structural package
- [X] T008 [US4] Write `tests/test_structural_benchmark.py`: 396/396 names, per-illusion
  accuracy; skipped without the image directory

## Phase 4: Reproduction (User Story 4)

- [X] T009 [US4] Write `specs/004-structural/checks/reproduce.py`: run the 396 images through
  the harness; names, accuracy table, notebook 13 section 10 quantities; outputs to
  `~/Documents/workspace/intent-harness-runs/004/`; plus `compare_recorded.py` for the per-item
  comparison with the recorded results (`INTENT_HARNESS_RECORDED_DIR`)
- [X] T010 [US4] Run the check; record the numbers in `checks/RESULT.md`
- [X] T011 Run the full test suite; grep the staged diff for the assistant's name; commit;
  rebase on `origin/main`; push; open the pull request

## Dependencies

T001 and T002–T004 can run in any order. T005 needs T004. T006 needs T001–T005. Tests need
T006. T009–T010 need T006.
