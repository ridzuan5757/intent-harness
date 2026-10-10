# Implementation Plan: Paper Notebooks

**Branch**: `007-paper-notebooks` | **Date**: 2026-10-09 | **Spec**: [spec.md](spec.md)

## Summary

One script per set writes a result file on the M3; one notebook per table reads it. The item
lists ship in `data/`, built once from the experiment's files by `scripts/build_data.py`. The
classifier gets a text-mode path for vision-language models. `.env.paper` holds what the paper
loads; machine paths come from environment variables.

## Technical Context

**Language/Version**: Python 3.12
**Primary Dependencies**: the SDK packages; for the notebooks: pandas, pyarrow, nbconvert,
ipykernel (new `notebooks` extra, pinned to the M3's versions)
**Storage**: parquet result files under `results/` (small; no images)
**Testing**: pytest for the new code (text-mode detection, the run-file helpers)
**Target Platform**: the M3 (Apple silicon, MPS) for the runs; the laptop for the notebooks
**Performance Goals**: one job at a time on the M3; the 24-model sweep is the long job
**Constraints**: the M3 disk has about 30 GB free; result files stay small

## Constitution Check

- I. Core knows nothing concrete: no change to `intent_harness/`. PASS.
- II. Moved code keeps its numbers: this feature is the full-set check; every notebook compares
  item by item with the record. PASS.
- III. Public repository hygiene: grep before every commit, no agent files. PASS.
- IV. Environment: the notebook packages are pinned in `requirements.txt` and in the `notebooks`
  extra in the same change. PASS.
- V. Scope: paper scope only; the vision-model baseline is feature 008. PASS.

## Project Structure

```text
.env.paper                       # what the paper loads
data/                            # item lists (built by scripts/build_data.py)
  intent-definitions.json        # the ten recorded intent definitions, in order
  intent-manifest.parquet        # 388 prompts with the gold intent
  models.json                    # the 24 models: name, HuggingFace id, kind, dtype, size
  illusion-items.parquet         # 396 illusion images with gold name and gold answer
  counting-items.parquet         # 795 counting items with prompt and gold count
scripts/
  runs.py                        # paths from the environment, resumable writer, marker, reader
  build_data.py                  # builds data/ from the experiment's files (provenance)
  run_classifier.py              # 24 models x 388 prompts
  run_structural.py              # 396 illusion images
  run_legs.py                    # 2,196 animal images (1,098 pairs)
  run_counting.py                # 795 counting items
  run_end_to_end.py              # VLMBias benchmark-main, 2,784 prompts
notebooks/
  01-intent-classifier.ipynb ... 05-end-to-end.ipynb
results/                         # result files and .done markers
intent_harness_classifiers/language_model.py   # + vision-language models on text only
```

## Complexity Tracking

None.
