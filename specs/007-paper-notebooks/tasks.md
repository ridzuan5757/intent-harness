# Tasks: Paper Notebooks

**Input**: spec.md and plan.md in `specs/007-paper-notebooks/`

## Phase 1: Setup

- [ ] T001 Add pandas, pyarrow, nbconvert and ipykernel to `requirements.txt` and as the
  `notebooks` extra in `pyproject.toml`; install into the worktree `.venv`
- [ ] T002 `.env.paper`; document the data variables in the README
- [ ] T003 `scripts/runs.py`: paths, resumable JSON-lines writer, result file, `.done` marker,
  reader that refuses an incomplete run
- [ ] T004 `scripts/build_data.py` and the files in `data/`

## Phase 2: User Story 1 and 2 - Scripts (P1)

- [ ] T005 Text mode for vision-language models in `intent_harness_classifiers/language_model.py`
  (kind detected from the model config); tests
- [ ] T006 `scripts/run_classifier.py`; 10-item sample per vision model on the M3, then the
  24-model sweep under nohup
- [ ] T007 `scripts/run_structural.py`; smoke, then full on the M3
- [ ] T008 `scripts/run_legs.py`; smoke, then full on the M3
- [ ] T009 `scripts/run_counting.py`; smoke, then full on the M3
- [ ] T010 `scripts/run_end_to_end.py`; smoke, then full on the M3

## Phase 3: User Stories 1, 3 and 4 - Notebooks (P1)

- [ ] T011 Notebooks 01 to 05: opening cell, tables from result files, item-by-item comparison
  with the record when `INTENT_HARNESS_RECORDED_DIR` is set, "Reading the result", "Conclusion"
- [ ] T012 Execute the notebooks on the laptop with the pulled result files; check each is at or
  below 600 KB

## Phase 4: Polish

- [ ] T013 README "Reproduce the paper"; record the results and any difference in the spec
- [ ] T014 pytest; grep for the assistant's name; rebase; PR
