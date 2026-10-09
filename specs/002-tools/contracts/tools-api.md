# Contract: public functions of `intent_harness_tools`

Every function is importable from the package root. None imports another package of this
repository.

| Function | Arguments | Returns |
|---|---|---|
| `colour_mask(image, colour)` | PIL image; `"dark"`, `"red"` or `"grey"` | Mask; ValueError for another colour |
| `group_shapes(mask, min_pixels=20)` | Mask; int | list of Shape, largest first |
| `find_runs(mask, axis, min_length)` | Mask; `"rows"` or `"columns"`; int | list of Segment by position; ValueError for another axis |
| `direction_filter(mask, axis, length)` | Mask; `"rows"` or `"columns"`; int | Mask with only strokes that hold a straight `length`-pixel line along `axis` |
| `equivalent_diameter(shape)` | Shape | float, the diameter of a disc with the same area |
| `fit_line(shape)` | Shape | Line |
| `point_line_distance(point, line)` | (row, col); Line | float, signed; positive below the line in the image |
| `decide(quantity, tolerance)` | float; float | `"Yes"` or `"No"` |
| `draw_segments(size, segments, width=7, colour=(0, 0, 0))` | int; list of ((x0, y0), (x1, y1)); int; RGB | PIL RGB image of `size` x `size` |
| `draw_discs(size, discs, colour=(255, 0, 0))` | int; list of ((x, y), diameter); RGB | PIL RGB image |
| `segment_at_angle(centre, length, angle_deg)` | (x, y); float; float | ((x0, y0), (x1, y1)) |

Constants: `COLOUR_RULES` (the three colour thresholds in words), `SUPERSAMPLE = 4`.
