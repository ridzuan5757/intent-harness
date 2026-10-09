"""The frozen tolerance of each illusion.

Each tolerance is 1.5 times the largest absolute quantity measured on that illusion's original
images. It was frozen before any edited image was measured. The values are copied from the
`tolerance` column of the experiment's result files (experiment workspace `results/`):

| Illusion            | Source file                               |
|---------------------|-------------------------------------------|
| muller_lyer         | 14-muller-lyer-colour.parquet             |
| ponzo               | 15-ponzo-colour.parquet                   |
| vertical_horizontal | 16-vertical-horizontal-colour.parquet     |
| ebbinghaus          | 17-ebbinghaus-colour.parquet              |
| poggendorff         | 18-poggendorff-colour.parquet             |
| zollner             | 19-zollner-colour.parquet                 |

Ebbinghaus and Zöllner originals measure exactly zero, so their tolerance is 0. That holds
for figures drawn by the VLMBias generator only.

Ponzo: two 384 px originals have a short bar that touches the converging lines, which sets
the tolerance above the smallest edit (0.15). 12 of 36 edited images are answered "Yes". This
is a recorded limitation; the answer stays binary.
"""

TOLERANCE_RULE = "1.5 x the largest absolute quantity on the originals, frozen before edited images"

TOLERANCES = {
    "muller_lyer": 0.1848341232227488,
    "ponzo": 0.1764705882352941,
    "vertical_horizontal": 0.015544041450777202,
    "ebbinghaus": 0.0,
    "poggendorff": 0.03041416428900707,
    "zollner": 0.0,
}
