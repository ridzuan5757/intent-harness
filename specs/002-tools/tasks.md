---
description: "Task list for the measurement tools"
---

# Tasks: Measurement Tools

**Input**: Design documents from `specs/002-tools/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/tools-api.md

**Tests**: requested (the 116 checks of notebook 13 are the acceptance test of User Story 2).

## Format: `[ID] [P?] [Story] Description`

## Phase 1: Setup

- [X] T001 Create the package folder `intent_harness_tools/` and the test folder `tests/`

## Phase 2: Foundational

- [X] T002 [P] Move `colour_mask` and `COLOUR_RULES` to `intent_harness_tools/masks.py`
- [X] T003 [P] Move `group_shapes` and `equivalent_diameter` to `intent_harness_tools/shapes.py`
- [X] T004 [P] Move `_row_runs`, `find_runs` and `direction_filter` to `intent_harness_tools/segments.py`
- [X] T005 [P] Move `fit_line` and `point_line_distance` to `intent_harness_tools/lines.py`
- [X] T006 [P] Move `decide` to `intent_harness_tools/decision.py`
- [X] T007 [P] Move `SUPERSAMPLE`, `_canvas`, `_shrink`, `draw_segments`, `draw_discs` and `segment_at_angle` to `intent_harness_tools/drawing.py`
- [X] T008 Re-export the public functions and constants in `intent_harness_tools/__init__.py`

**Checkpoint**: `from intent_harness_tools import find_runs` works.

## Phase 3: User Story 1 - Measure a drawn figure with plain functions (P1)

- [X] T009 [US1] Add `tests/test_tools_basic.py`: the three acceptance scenarios of User Story 1 and the edge cases of the spec (empty mask, small shapes and short runs dropped, unknown colour and axis raise ValueError, quantity equal to tolerance answers "Yes")
- [X] T010 [US1] Add `tests/test_independence.py`: a fresh process imports the package and loads no `intent_harness` module

## Phase 4: User Story 2 - Keep the recorded numbers (P1)

- [X] T011 [US2] Add `tests/test_drawn_shapes.py`: build the checks of notebook 13 sections 3 to 8 in the same order (find_runs 27, equivalent_diameter 9, group_shapes 12, fit_line 21, point_line_distance 12, direction_filter 18, colour_mask 12, decide 5), one parametrized case per check, 116 in all
- [X] T012 [US2] In `tests/test_drawn_shapes.py`, add the test that the check count is 116 and that the largest absolute error per tool equals notebook 13 to six decimals

## Phase 5: User Story 3 - Draw test shapes (P2)

- [X] T013 [US3] In `tests/test_tools_basic.py`, add the drawing helper scenarios: image size and mode, stroke colour, and `segment_at_angle` end points

## Phase 6: Polish

- [X] T014 Run `.venv/bin/python -m pytest tests -q`; confirm all pass in under one minute
- [X] T015 Grep the staged diff for the assistant's name; commit; rebase on `origin/main`; push; open the pull request

## Dependencies

- T001 before T002 to T007; T002 to T007 in parallel; T008 after them.
- T009 to T013 after T008; T011 and T012 in the same file, in order.
- T014 after all; T015 last.
