"""Colour masks: the pixels of one colour class."""

import numpy as np

# The colour thresholds of the illusion figures.
COLOUR_RULES = {
    "dark": "R, G and B all below 100",
    "red": "R above 180, G and B below 90",
    "grey": "R within 12 of 128, and the three channels within 4 of each other",
}


def colour_mask(image, colour):
    """(H, W) bool: the pixels of one colour class."""
    rgb = np.asarray(image.convert("RGB")).astype(np.int16)     # (H, W, 3)
    red = rgb[:, :, 0]
    green = rgb[:, :, 1]
    blue = rgb[:, :, 2]
    if colour == "dark":
        return (red < 100) & (green < 100) & (blue < 100)
    if colour == "red":
        return (red > 180) & (green < 90) & (blue < 90)
    if colour == "grey":
        return ((np.abs(red - 128) < 12) & (np.abs(red - green) < 4) & (np.abs(green - blue) < 4))
    raise ValueError(f"unknown colour '{colour}'; known: {sorted(COLOUR_RULES)}")
