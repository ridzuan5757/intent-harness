"""Drawing helpers: test shapes with a known answer.

Shapes are drawn at SUPERSAMPLE times the target size and shrunk, so the edges are soft like
the edges of the benchmark figures.
"""

import math

from PIL import Image, ImageDraw

SUPERSAMPLE = 4


def _canvas(size):
    return Image.new("RGB", (size * SUPERSAMPLE, size * SUPERSAMPLE), "white")


def _shrink(image, size):
    return image.resize((size, size), Image.LANCZOS)


def draw_segments(size, segments, width=7, colour=(0, 0, 0)):
    """Straight strokes with flat ends. segments: list of ((x0, y0), (x1, y1)) in target pixels."""
    image = _canvas(size)
    draw = ImageDraw.Draw(image)
    for (x0, y0), (x1, y1) in segments:
        draw.line([(x0 * SUPERSAMPLE, y0 * SUPERSAMPLE), (x1 * SUPERSAMPLE, y1 * SUPERSAMPLE)],
                  fill=colour, width=width * SUPERSAMPLE)
    return _shrink(image, size)


def draw_discs(size, discs, colour=(255, 0, 0)):
    """Filled discs. discs: list of ((x, y), diameter) in target pixels."""
    image = _canvas(size)
    draw = ImageDraw.Draw(image)
    for (x, y), diameter in discs:
        radius = diameter * SUPERSAMPLE / 2.0
        centre_x = x * SUPERSAMPLE
        centre_y = y * SUPERSAMPLE
        draw.ellipse([centre_x - radius, centre_y - radius, centre_x + radius, centre_y + radius], fill=colour)
    return _shrink(image, size)


def segment_at_angle(centre, length, angle_deg):
    """((x0, y0), (x1, y1)) of a segment through `centre` at `angle_deg` (rising to the right)."""
    x, y = centre
    dx = math.cos(math.radians(angle_deg)) * length / 2.0
    dy = -math.sin(math.radians(angle_deg)) * length / 2.0
    return ((x - dx, y - dy), (x + dx, y + dy))
