# Implementation Plan: Measurement Tools

**Branch**: `002-tools` | **Date**: 2026-10-09 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/002-tools/spec.md`

## Summary

Move the eight illusion measurement tools and the three drawing helpers from the experiment
workspace (`grounded-count-harness/harness/tools.py`, lines 1 to 251) into a new package,
`intent_harness_tools`, as plain functions with the same behaviour. Split them into small modules
by job. Port the 116 drawn-shape checks of notebook 13 to pytest, one test case per check, with
the same cases, sizes and limits, and one test that compares the largest error per tool with the
numbers recorded in notebook 13.

## Technical Context

**Language/Version**: Python 3.12

**Primary Dependencies**: numpy 2.5.3, scipy 1.18.1 (`ndimage`), pillow 12.3.0 — all pinned in
`requirements.txt`, the same versions as the experiment

**Storage**: N/A

**Testing**: pytest 9.1.1, run as `.venv/bin/python -m pytest tests` from the repository root

**Target Platform**: macOS and Linux, CPU only

**Project Type**: library (one package of plain functions)

**Performance Goals**: the full test run under one minute on a laptop (SC-004)

**Constraints**: no import of any other package of this repository; no new package; identical
output to the experiment code

**Scale/Scope**: 8 tools, 3 drawing helpers, 116 drawn-shape checks

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Check | Result |
|---|---|---|
| I. Core knows nothing concrete | Tools are plain functions; no import of `intent_harness`; no names, traces or registration | Pass |
| II. Moved code keeps its numbers | 116 checks of notebook 13 ported with the same limits; largest errors compared | Pass |
| III. Public repository hygiene | Staged diff grepped before each commit; no agent files committed; branch and PR flow | Pass |
| IV. Environment | Only packages already pinned in `requirements.txt` | Pass |
| V. Scope and simplicity | Only the eight tools and three helpers; counting tools, pixel rules, pipelines and SAM 3 left out | Pass |
| VI. Plain, precise writing | Docstrings and docs in short, active sentences | Pass |

Re-check after Phase 1: no change. Pass.

## Project Structure

### Documentation (this feature)

```text
specs/002-tools/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── tools-api.md
├── checklists/
│   └── requirements.md
└── tasks.md
```

### Source Code (repository root)

```text
intent_harness_tools/
├── __init__.py      # re-exports the public functions
├── masks.py         # colour_mask, COLOUR_RULES
├── shapes.py        # group_shapes, equivalent_diameter
├── segments.py      # find_runs, direction_filter
├── lines.py         # fit_line, point_line_distance
├── decision.py      # decide
└── drawing.py       # draw_segments, draw_discs, segment_at_angle, SUPERSAMPLE

tests/
├── test_drawn_shapes.py    # the 116 checks of notebook 13 and the largest-error comparison
├── test_tools_basic.py     # edge cases and the drawing helpers
└── test_independence.py    # the package imports nothing else from this repository
```

**Structure Decision**: one flat package at the repository root, next to the core package that
feature 001 adds. Tests in a root `tests/` folder. No `conftest.py` and no `pyproject.toml` in this
feature: `python -m pytest` from the root puts the root on the import path.

## Complexity Tracking

No violations.
