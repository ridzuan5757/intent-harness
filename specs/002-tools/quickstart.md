# Quickstart: Measurement Tools

## Set up
```bash
uv venv --python 3.12 .venv
uv pip install --python .venv/bin/python -r requirements.txt
```

## Validate
```bash
.venv/bin/python -m pytest tests -q
```
Expected: every test passes; the drawn-shape module reports 116 passed checks
(`tests/test_drawn_shapes.py`), and the largest-error test matches notebook 13.

## Use
```python
from intent_harness_tools import draw_segments, colour_mask, find_runs

image = draw_segments(384, [((115.2, 192), (268.8, 192))])
segments = find_runs(colour_mask(image, "dark"), "rows", 30)
segments[0]["length"]   # about 153.6
```
