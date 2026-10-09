# Reproduction result, 2026-10-09

Run on the laptop through the SDK path: `Harness` with `intent_harness_tools.measurement_plugin`,
`intent_harness_structural.plugin` and a fixed classifier that always chooses `structural`.
Images: the 396 VLMBias illusion images (`benchmark-main/vlms-are-biased-notitle`), 198
originals and 198 edited. 12 s for all 396 images.

## Illusion names (pixel rules)

396 of 396 named correctly. The rules hash equals the hash frozen in the experiment
(`2da696c4…0c53`).

## Accuracy per illusion

| Illusion | Originals | Edited | Recorded |
|---|---|---|---|
| Müller-Lyer | 36 / 36 | 36 / 36 | same |
| Ponzo | 36 / 36 | 24 / 36 | same |
| Vertical-Horizontal | 18 / 18 | 18 / 18 | same |
| Ebbinghaus | 36 / 36 | 36 / 36 | same |
| Poggendorff | 36 / 36 | 36 / 36 | same |
| Zöllner | 36 / 36 | 36 / 36 | same |

Ponzo's 12 misses are all the smallest edit (0.15). This is a recorded limitation; the
answer stays binary.

## Item by item (`compare_recorded.py`)

| Measure | Value |
|---|---|
| Items compared | 396 of 396 (same item ids in both) |
| Same answer | 396 |
| Same gold answer | 396 |
| Same quantity, within 1e-9 | 396 |
| Largest quantity gap | 4.4e-16 |

## Notebook 13 section 10 (first original of each illusion, |quantity|)

| Illusion | 384 px | 768 px | 1152 px |
|---|---|---|---|
| Müller-Lyer | 0.0583 | 0.0302 | 0.0203 |
| Ponzo | 0.0000 | 0.0000 | 0.0000 |
| Vertical-Horizontal | 0.0104 | 0.0000 | 0.0000 |
| Ebbinghaus | 0.0000 | 0.0000 | 0.0000 |
| Poggendorff | 0.0012 | 0.0004 | 0.0002 |
| Zöllner | 0.0000 | 0.0000 | 0.0000 |

All equal to the notebook values at 4 decimals.

## Leakage check

The scores are near perfect, so the check is: no step reads a benchmark label. The pixel rules
read pixels only and were frozen before scoring; the tolerances were frozen on originals before
any edited image was measured; the gold answer comes from the file name only in the check
script, never in the intent.
