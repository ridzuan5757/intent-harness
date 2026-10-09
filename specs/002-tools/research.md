# Research: Measurement Tools

## R1. Module split

- **Decision**: six modules by job (masks, shapes, segments, lines, decision, drawing) and one
  `__init__.py` that re-exports the public functions.
- **Rationale**: each later pipeline uses a few tools; small modules keep each file readable and
  let a reader find a tool by its job. The public import stays `from intent_harness_tools import
  find_runs`.
- **Alternatives considered**: one `tools.py` as in the experiment (simple, but the file also held
  15 counting tools there and grew to 443 lines); one module per tool (too many files for 8 short
  functions).

## R2. Behaviour must not change

- **Decision**: copy the function bodies unchanged; change only docstrings and private helper
  placement (`_row_runs` moves with `find_runs`; `_canvas` and `_shrink` move with the drawing
  helpers).
- **Rationale**: the paper's illusion results were computed with this code; any change, even a
  refactor, could move a number.
- **Alternatives considered**: tidy the code (for example, typed dataclasses for segments and
  lines). Rejected for this feature: later pipelines and the recorded traces read these dict keys.

## R3. How the 116 checks become tests

- **Decision**: build the list of checks in plain Python at import time of the test module, in the
  same order and with the same cases as notebook 13 sections 3 to 8. Parametrize one pytest case
  per check (116 cases). A separate test computes the largest absolute error per tool and compares
  it with notebook 13 to six decimals.
- **Rationale**: one case per check makes the pass count visible in the pytest summary; the
  largest-error test proves the numbers did not move, not only that they stay inside the limits.
- **Alternatives considered**: one test per tool with an inner loop (hides the count); reading
  `results/13-tool-checks.parquet` from the experiment (the file is not in this repository and
  pandas is not a dependency).

## R4. The Zöllner filter length

- **Decision**: the test uses 41 px as a test constant, with a comment that it is the Zöllner
  pipeline's filter length in the experiment.
- **Rationale**: the pipeline constant belongs to feature 004; the tools package must not hold
  pipeline settings.

## R5. Proof of independence

- **Decision**: a test runs a fresh Python process that imports `intent_harness_tools` and checks
  that no module whose name starts with `intent_harness.` or equals `intent_harness` is loaded.
- **Rationale**: feature 001 adds the core package in parallel; the test fails if a later change
  adds such an import.
