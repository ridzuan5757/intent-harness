# Tasks: Option-Scoring Intent Classifier

**Input**: spec.md, plan.md in `specs/003-intent-classifier/`

## Phase 1: Package

- [X] T001 [US1] Create `intent_harness_classifiers/scoring.py` with `build_prompt`, `softmax`,
  `confidence_from_probabilities`, copied from the experiment's `classifiers.py`
- [X] T002 [US1] Create `intent_harness_classifiers/language_model.py` with `LanguageModel`
  (local files only, chat template without thinking, batched option scoring, `unload`)
- [X] T003 [US1] [US2] Create `intent_harness_classifiers/option_scoring.py` with
  `OptionScoringClassifier` and `register(harness, model=None, language_model=None, **options)`
- [X] T004 [US1] Create `intent_harness_classifiers/__init__.py` (no torch import)

## Phase 2: Tests

- [X] T005 [US1] [US2] Write `tests/test_option_scoring.py`: options follow the loaded intents and
  their order; a later intent adds an option; softmax and confidence values; one intent gives
  confidence 1; prompt text; missing `model` raises; plugin loading routes `Harness.answer`;
  import does not load torch
- [X] T006 Run `.venv/bin/python -m pytest` until green

## Phase 3: Recorded number

- [X] T007 [US3] Write `specs/003-intent-classifier/checks/reproduce_qwen3_4b.py`
- [X] T008 [US3] Sync to the M3 (`~/intent-harness-runs/003/`), smoke-test on 10 items, pull
  outputs to `~/Documents/workspace/intent-harness-runs/003/` (the full 388 moves to feature 007)
- [X] T009 [US3] Record the result in spec.md

## Phase 4: Close

- [X] T010 Grep for the assistant name, commit, rebase on origin/main, test, push, open the PR
