# Data Model: Measurement Tools

All values are plain Python and numpy objects. No class is defined.

## Mask
- `numpy.ndarray`, dtype bool, shape (H, W). True where the pixel belongs to the colour class.
- Made by `colour_mask(image, colour)`; `colour` is one of `dark`, `red`, `grey`.

## Shape (dict)
| Key | Type | Meaning |
|---|---|---|
| `pixels` | int | number of pixels |
| `rows`, `cols` | ndarray of int | coordinates of the pixels |
| `bbox` | (row_min, col_min, row_max, col_max) | bounding box |
| `centroid` | (row, col) floats | mean position |

Made by `group_shapes(mask, min_pixels)`, largest first; 8-connected.

## Segment (dict)
| Key | Type | Meaning |
|---|---|---|
| `axis` | "rows" or "columns" | scan direction |
| `position` | float | mean line index |
| `first_line`, `last_line` | int | lines covered |
| `thickness` | int | number of lines covered |
| `start`, `end` | float | median run start and end (end exclusive) |
| `length` | float | median run length |

Made by `find_runs(mask, axis, min_length)`, sorted by position.

## Line (dict)
| Key | Type | Meaning |
|---|---|---|
| `centre` | (row, col) | mean of the pixels |
| `direction` | (dx, dy) unit vector | dx >= 0 |
| `angle_deg` | float | angle from the horizontal, positive when rising to the right |
| `end_a`, `end_b` | (row, col) | extreme pixels along the line; `end_a` is the left one |

Made by `fit_line(shape)`.

## Decision
- `"Yes"` when `abs(quantity) <= tolerance`, else `"No"`.
