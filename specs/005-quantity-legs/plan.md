# Implementation Plan: Quantity Intent, Animal Legs

**Branch**: `005-quantity-legs` | **Date**: 2026-10-09 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/005-quantity-legs/spec.md`

## Summary

Move the leg counting of the experiment (notebooks 06 to 08 of the grounded-count-harness
workspace) into the SDK. Two localizers become plain tools: SAM 3 concept segmentation with its
region helpers, and the GroundingDINO tiny animal box. The quantity intent becomes a plugin with
one pipeline, `legs`, that calls the tools by name. A check script runs the 2,196 animal images
through `Harness.answer` on the M3 and compares the counts with `07-full-counts.parquet`.

## Technical Context

**Language/Version**: Python 3.12

**Primary Dependencies**: numpy, pillow (tools and pipeline); torch and transformers from the
`models` extra (loaded only inside the model functions); pandas in the check scripts only, from
the M3 experiment environment

**Storage**: none in the repository; check outputs go to `~/Documents/workspace/intent-harness-runs/005/`

**Testing**: pytest with a fake segmenter and a fake box finder; no model on the laptop

**Target Platform**: macOS (laptop tests), M3 Ultra with MPS (models and the full check)

**Project Type**: library plugin

**Performance Goals**: the full check finishes in one M3 session (about 1 to 1.5 s per image)

**Constraints**: models load from the local cache only; tools never import the core

**Scale/Scope**: 2,196 images, 1,098 pairs, 139 species

## Constitution Check

- **I. Core knows nothing concrete**: pass. No change to `intent_harness/`. Tools are plain
  functions; the plugins name them. The intent gets tools by name from the mapping it receives.
- **II. Moved code keeps its numbers**: pass by the M3 check (SC-002, SC-003). The rules and
  constants are copied from notebooks 07 and 08 unchanged.
- **III. Public repository hygiene**: the staged diff is checked before each commit.
- **IV. Environment**: no new package. torch and transformers come from the `models` extra.
- **V. Scope**: one pipeline. The selector is a parameter only; 006 builds a real one.
- **VI. Plain writing**: docstrings and docs in ASD-STE100 style.

## Project Structure

### Documentation (this feature)

```text
specs/005-quantity-legs/
├── spec.md
├── plan.md
├── tasks.md
└── checks/
    ├── reproduce_legs.py   # M3: counts through Harness.answer, resumable
    └── compare_legs.py     # laptop: summary and per-image agreement with the record
```

### Source Code (repository root)

```text
intent_harness_tools/
├── sam3.py                   # segment_concept, keep_smaller_regions, remove_duplicate_regions
├── sam3_plugin.py            # register(harness)
├── grounding_dino.py         # best_box
└── grounding_dino_plugin.py  # register(harness)

intent_harness_quantity/
├── __init__.py
├── intent.py                 # QuantityIntent: pipelines by name, optional selector
├── legs.py                   # LegsPipeline and its constants
└── plugin.py                 # register(harness)

tests/
├── test_regions.py           # size filter and duplicate removal on drawn masks
├── test_quantity.py          # legs pipeline and intent with fake tools; harness end to end
└── test_model_imports.py     # importing the tools package loads no model package
```

**Structure Decision**: a separate package per intent (`intent_harness_quantity`), found by the
existing `intent_harness*` package rule, so no change to `pyproject.toml`.

## Complexity Tracking

| Item | Why needed | Simpler choice rejected because |
|---|---|---|
| GroundingDINO tiny as a second tool | the recorded counts used its animal box for the size rule | SAM 3 alone gives other counts than the paper reports |
