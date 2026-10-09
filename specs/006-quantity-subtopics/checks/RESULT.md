# Feature 006 checks: result (2026-10-09)

Small samples only (constitution, Principle II). The full sets run in the paper notebooks
(feature 007) on the M3.

## Board references (SC-003)

`build_references.py`: the crops that `build_board_references` makes from the two unedited boards
equal the experiment's `board_references()` exactly (32 chess crops, 90 xiangqi crops, the
xiangqi grid). The shipped `board_references.npz` (17.6 KB, uint8) also equals them exactly.

## Selector (SC-001)

`check_selector.py` on every counting prompt of `benchmark-main` and `benchmark-original`
(illusion and identification prompts left out): **2,155 of 2,155 prompts right** (1,159 images).

| Counter | Prompts right |
|---|---|
| legs | 637 / 637 |
| car_logos | 315 / 315 |
| flag_stars | 169 / 169 |
| dice | 168 / 168 |
| tally | 168 / 168 |
| shoe_logos | 146 / 146 |
| chess_pieces | 145 / 145 |
| xiangqi_pieces | 145 / 145 |
| flag_stripes | 90 / 90 |
| chess_grid | 49 / 49 |
| sudoku_grid | 49 / 49 |
| xiangqi_grid | 49 / 49 |
| go_grid | 25 / 25 |

## Counters through `Harness.answer` (SC-002)

`check_counters.py`, item by item against the recorded `count` of `results/23..27-*.parquet`.
The sample has up to 2 items the experiment counted wrong per sub-topic, then right items, to 5.

| Sub-topic | Where | Same count | Of them recorded wrong |
|---|---|---|---|
| chess_grid | laptop | 5 / 5 | 0 (the sub-topic has none) |
| sudoku_grid | laptop | 5 / 5 | 0 (none) |
| xiangqi_grid | laptop | 5 / 5 | 0 (none) |
| go_grid | laptop | 5 / 5 | 0 (none) |
| chess_pieces | laptop | 5 / 5 | 0 (none) |
| xiangqi_pieces | laptop | 5 / 5 | 0 (none) |
| flag_stars | laptop | 5 / 5 | 2 |
| flag_stripes | laptop | 5 / 5 | 0 (none) |
| dice | laptop | 5 / 5 | 2 |
| tally | laptop | 5 / 5 | 2 |
| car_logos | M3 (SAM 3) | 9 / 9 | 4 (all three targets: overlapping circles, prongs, star points) |
| shoe_logos | M3 (SAM 3) | 5 / 5 | 2 |

Total: **64 of 64** distinct items give the recorded count, 12 recorded errors included. The car
logo items come from two runs: the 5-item sample (all "overlapping circles") and 1 wrong and 1
right item per target; 2 items are in both runs and gave the same count both times.

Outputs: `~/Documents/workspace/intent-harness-runs/006/` (laptop) and its `m3/` folder.
