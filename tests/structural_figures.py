"""Drawn test figures for the structural intent, one per illusion.

Each function returns a PIL image with a known answer: `edit=0` draws the two compared parts
equal (answer "Yes"); a non-zero `edit` changes one part (answer "No"). The shapes follow the
class descriptions, so the pixel rules name the illusion.
"""

from PIL import ImageDraw

from intent_harness_tools import SUPERSAMPLE, draw_discs, draw_segments, segment_at_angle

SIZE = 768


def muller_lyer(edit=0.0):
    """Upper shaft with outward fins (arrow tails), lower shaft with inward fins (arrow heads)."""
    left, right = 220, 540
    lower_right = right + (right - left) * edit
    segments = [((left, 250), (right, 250)), ((left, 520), (lower_right, 520))]
    segments += [((left, 250), (left - 28, 222)), ((left, 250), (left - 28, 278))]
    segments += [((right, 250), (right + 28, 222)), ((right, 250), (right + 28, 278))]
    segments += [((left, 520), (left + 28, 492)), ((left, 520), (left + 28, 548))]
    segments += [((lower_right, 520), (lower_right - 28, 492)), ((lower_right, 520), (lower_right - 28, 548))]
    return draw_segments(SIZE, segments)


def ponzo(edit=0.0):
    """Two converging lines from the bottom corners; two short bars, the upper one changed."""
    segments = [((40, 760), (330, 10)), ((728, 760), (438, 10))]
    bar = 140
    top_extra = bar * edit
    segments += [((384 - bar / 2, 220), (384 + bar / 2 + top_extra, 220)),
                 ((384 - bar / 2, 560), (384 + bar / 2, 560))]
    return draw_segments(SIZE, segments)


def vertical_horizontal(edit=0.0):
    """An inverted T; the vertical segment changed."""
    length = 300
    segments = [((234, 600), (534, 600)), ((384, 600), (384, 600 - length * (1 + edit)))]
    return draw_segments(SIZE, segments)


def ebbinghaus(edit=0.0):
    """Two red discs; the right disc changed."""
    return draw_discs(SIZE, [((220, 384), 96), ((548, 384), 96 * (1 + edit))])


def poggendorff(offset=0):
    """A grey rectangle and two diagonal pieces of one 30-degree line; `offset` shifts the right piece in px."""
    image = draw_segments(SIZE, [((384, 60), (384, 708))], width=120, colour=(128, 128, 128))
    canvas = image.resize((SIZE * SUPERSAMPLE, SIZE * SUPERSAMPLE))
    left = segment_at_angle((200, 520), 200, 30)
    right_centre = (568, 520 - (368 * 0.5773502691896257) + offset)
    right = segment_at_angle(right_centre, 200, 30)
    draw = ImageDraw.Draw(canvas)
    for (x0, y0), (x1, y1) in (left, right):
        draw.line([(x0 * SUPERSAMPLE, y0 * SUPERSAMPLE), (x1 * SUPERSAMPLE, y1 * SUPERSAMPLE)],
                  fill=(0, 0, 0), width=7 * SUPERSAMPLE)
    return canvas.resize((SIZE, SIZE))


def zollner(tilt_deg=0.0):
    """Two long horizontal lines with slanted strokes; `tilt_deg` tilts them toward each other."""
    segments = []
    for y, sign, lean in ((250, 1, 1), (520, -1, -1)):
        line = segment_at_angle((384, y), 600, sign * tilt_deg / 2.0)
        segments.append(line)
        for x in range(124, 660, 50):
            segments.append(((x - lean * 20, y - 30), (x + lean * 20, y + 30)))
    return draw_segments(SIZE, segments)
