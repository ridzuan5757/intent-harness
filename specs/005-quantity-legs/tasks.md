# Tasks: Quantity Intent, Animal Legs

**Input**: [spec.md](spec.md), [plan.md](plan.md)

**Tests**: requested (pytest, SC-001); the M3 check is SC-002 and SC-003.

## Phase 1: Tools

- [X] T001 [P] `intent_harness_tools/sam3.py`: `segment_concept` (lazy model, local cache only),
  `keep_smaller_regions`, `remove_duplicate_regions`, with the constants of notebook 07
- [X] T002 [P] `intent_harness_tools/grounding_dino.py`: `best_box`
- [X] T003 `intent_harness_tools/sam3_plugin.py` and `grounding_dino_plugin.py`: `register(harness)`
- [X] T004 `tests/test_regions.py`: size filter and duplicate removal on drawn masks
- [X] T005 [P] `tests/test_model_imports.py`: importing `intent_harness_tools` loads no torch or
  transformers, and no core module

## Phase 2: User Story 1 - Count legs through the harness (P1)

- [X] T006 [US1] `intent_harness_quantity/legs.py`: `LegsPipeline`
- [X] T007 [US1] `intent_harness_quantity/intent.py` and `plugin.py`: `QuantityIntent`, `register`
- [X] T008 [US1] `tests/test_quantity.py`: scenarios 1 to 3 with fake tools, through `Harness.answer`

## Phase 3: User Story 3 - Pipelines and selector (P2)

- [X] T009 [US3] `tests/test_quantity.py`: one pipeline without selector, two with selector,
  two without selector raises, `required_tools` union

## Phase 4: User Story 2 - Reproduce the recorded counts (P1)

- [X] T010 [US2] `checks/reproduce_legs.py`: all images through `Harness.answer`, resumable,
  `--pairs N` for the smoke run
- [X] T011 [US2] `checks/compare_legs.py`: summary and per-image agreement with
  `07-full-counts.parquet`
- [X] T012 [US2] M3: sync, smoke run on 5 pairs, full run under nohup, pull
- [ ] T013 [US2] Record the result in spec.md

## Phase 5: Polish

- [ ] T014 Full test run; staged diff checked for the assistant's name; rebase; pull request
