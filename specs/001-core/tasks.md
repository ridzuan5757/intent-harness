# Tasks: Core

**Input**: [spec.md](spec.md), [plan.md](plan.md)

**Tests**: requested (pytest, SC-001).

## Phase 1: Setup

- [ ] T001 Write `pyproject.toml`: setuptools, packages `intent_harness*`, Python >=3.12,
  runtime pins from `requirements.txt`, extra `test` with pytest, pytest options
- [ ] T002 Install the package in editable mode into `.venv` and check the import

## Phase 2: Foundational

- [ ] T003 [P] `intent_harness/types.py`: `Choice`, `Step`, `Result`, `Answer`, `IntentInfo`
- [ ] T004 [P] `intent_harness/contracts.py`: `Tool`, `Intent`, `IntentClassifier` protocols
- [ ] T005 `intent_harness/tools.py`: trace context, `FunctionTool`, `as_tool`

## Phase 3: User Story 1 - Answer a question (P1)

- [ ] T006 [US1] `intent_harness/harness.py`: `Harness.answer` with classification, routing,
  declared-tools mapping, trace and `Answer`
- [ ] T007 [US1] `tests/fakes.py` and `tests/test_harness.py`: scenarios 1 to 3 and the edge
  cases (unknown key, tool error recorded and raised)
- [ ] T008 [P] [US1] `tests/test_tools.py`: trace in call order, no trace outside `answer`

## Phase 4: User Story 2 - Register and fail early (P2)

- [ ] T009 [US2] `intent_harness/registry.py`: checks by attribute name, duplicates, missing
  required tools, wrapping of plain functions
- [ ] T010 [US2] `tests/test_registry.py`: scenarios 1 to 4

## Phase 5: User Story 3 - Load from paths and .env (P3)

- [ ] T011 [US3] `intent_harness/loading.py` and the `Harness.load_*` and `from_env` methods
- [ ] T012 [US3] `tests/plugins/` fake plugin modules and `tests/test_loading.py`: scenarios
  1 to 3 and the empty-item edge case

## Phase 6: Polish

- [ ] T013 `intent_harness/__init__.py` public names; README "Use" section
- [ ] T014 Check SC-002: no import of a concrete part in `intent_harness/`
- [ ] T015 Run all tests; check SC-003 in a new `.venv`

## Dependencies

T001–T002 first; T003–T005 before the stories; US1 before US2 tests that use `Harness`; US3
after US1 and US2.
