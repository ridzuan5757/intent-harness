# Implementation Plan: Structural Intent

**Branch**: `004-structural` | **Date**: 2026-10-09 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/004-structural/spec.md`

## Summary

Move the illusion pixel rules and the six measurement pipelines from the experiment workspace
into a plugin package, `intent_harness_structural`. The intent names the illusion with the
pixel rules, runs that illusion's pipeline with tools taken by name from the harness, and
decides with the frozen tolerance. A second new file, `intent_harness_tools/measurement_plugin.py`,
registers the eight measurement tools. A check script reproduces the recorded numbers on the
396 VLMBias illusion images.

## Technical Context

**Language/Version**: Python 3.12

**Primary Dependencies**: numpy, scipy, pillow (already pinned); the core `intent_harness`

**Storage**: none; images are read from `INTENT_HARNESS_VLMBIAS_DIR`; check outputs go to
`~/Documents/workspace/intent-harness-runs/004/` (outside the repository)

**Testing**: pytest; drawn-shape tests always run; benchmark tests run only with the image
directory set

**Target Platform**: laptop (CPU); no model is needed

**Project Type**: library plugin

**Performance Goals**: the 396 images in a few minutes on the laptop

**Constraints**: no change to `intent_harness/`, `README.md`, `requirements.txt`,
`pyproject.toml` or the existing files of `intent_harness_tools/`; no new package

**Scale/Scope**: 6 illusions, 396 images

## Constitution Check

| Principle | Check |
|---|---|
| I. Core knows nothing concrete | Pass. The core is not changed. The intent gets tools by name from the mapping it receives; it imports only core types. The pixel rules are registered as a tool by the plugin. |
| II. Moved code keeps its numbers | Pass by design: the rules and pipelines are moved with the same arithmetic; the check script compares per item with the recorded results. |
| III. Public repository hygiene | Pass: grep the staged diff before each commit; images and outputs are not committed. |
| IV. Environment | Pass: no new package. |
| V. Scope and simplicity | Pass: structural only; no VLM classifier, no SAM 3 arm. |
| VI. Plain writing | Docstrings in plain style. |

## Project Structure

### Documentation (this feature)

```text
specs/004-structural/
├── spec.md
├── plan.md
├── tasks.md
└── checks/
    ├── reproduce.py          # the 396-image check through the SDK (repository .venv)
    ├── compare_recorded.py   # item-by-item comparison; needs pandas, so any Python with it
    └── RESULT.md             # the numbers of the run
```

### Source Code (repository root)

```text
intent_harness_tools/
└── measurement_plugin.py      # new: register(harness) for the eight tools

intent_harness_structural/
├── __init__.py                # public names
├── illusions.py               # the seven classes, descriptions, VLMBias folders
├── pixel_rules.py             # pixel features, ordered rules, rules hash
├── pipelines.py               # six measurement pipelines on a tools mapping
├── tolerances.py              # frozen tolerances with their source
├── intent.py                  # StructuralIntent
└── plugin.py                  # register(harness): the pixel-rule tool and the intent

tests/
├── structural_figures.py      # drawn test figures for each illusion
├── test_structural.py         # plugin loading, rules and pipelines on drawn figures
└── test_structural_benchmark.py   # 396 images; skipped without the image directory
```

## Design Decisions

1. **Tool access.** A pipeline is `measure_<illusion>(image, tools) -> Measurement`. It calls
   `tools["colour_mask"](image, "dark")` and the others by name. The arithmetic between tool
   calls is unchanged.
2. **Measurement.** A small dataclass: value_a, value_b, quantity, found. `found` is False
   when a step does not get the expected shapes; the intent then returns value `None`.
3. **Decision.** The intent calls `tools["decide"](quantity, TOLERANCES[key])`, so the trace
   ends with `decide` and holds the quantity and the tolerance.
4. **Pixel rules as a tool.** The plugin registers `pixel_rules.classify_image` as
   `illusion_pixel_rules`. It returns the illusion key. The trace then shows the choice.
5. **Plugin order.** `measurement_plugin` must be loaded before `intent_harness_structural.plugin`;
   the registry already fails early otherwise.
6. **Check data.** The check lists the image files in the six VLMBias folders and derives the
   illusion from the folder and the gold answer from `diff0` in the file name. A second
   script, `compare_recorded.py`, reads the recorded `14-..19-*-colour.parquet` and compares
   answer and quantity per item; the item id is `<Instance>_<NNN>_notitle_px<size>`. It is a
   separate script because reading parquet needs pandas, which the SDK does not depend on.

## Complexity Tracking

None.
