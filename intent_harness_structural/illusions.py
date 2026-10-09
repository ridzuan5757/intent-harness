"""The seven illusion classes.

Six classes are the optical illusions of the VLMBias benchmark. The seventh, `none`, is for a
figure that matches none of the six. Each description names only what is drawn: shapes, their
orientation, their position and their colour. It never states the outcome of a comparison.
The descriptions were written from the first original image of each class (768 px) on
2026-10-04. Moved unchanged from the experiment workspace (`harness/illusions.py`).
"""

import re

ILLUSIONS = [
    {
        "key": "muller_lyer",
        "name": "Müller-Lyer",
        "description": "Two horizontal line segments, one above the other. Each segment has a short "
                       "diagonal stroke at both ends. On one segment the strokes point outward, like "
                       "arrow tails; on the other segment they point inward, like arrow heads.",
        "vlmbias_sub_topic": "Müller-Lyer illusion",
        "vlmbias_folder": "mullerlyer",
    },
    {
        "key": "ponzo",
        "name": "Ponzo",
        "description": "Two long lines that start at the bottom corners and run toward the top, where "
                       "they come closer together. Between them lie two short horizontal segments, one "
                       "high and one low.",
        "vlmbias_sub_topic": "Ponzo illusion",
        "vlmbias_folder": "ponzo",
    },
    {
        "key": "vertical_horizontal",
        "name": "Vertical-Horizontal",
        "description": "One vertical line segment that stands on the middle of one horizontal line "
                       "segment, like an inverted letter T.",
        "vlmbias_sub_topic": "Vertical-Horizontal illusion",
        "vlmbias_folder": "verticalhorizontal",
    },
    {
        "key": "ebbinghaus",
        "name": "Ebbinghaus",
        "description": "Two red discs. One red disc is surrounded by a ring of small black discs; the "
                       "other red disc is surrounded by a ring of large black discs.",
        "vlmbias_sub_topic": "Ebbinghaus illusion",
        "vlmbias_folder": "ebbinghaus",
    },
    {
        "key": "poggendorff",
        "name": "Poggendorff",
        "description": "One tall grey rectangle. One diagonal line segment touches its left edge and "
                       "another diagonal line segment leaves its right edge.",
        "vlmbias_sub_topic": "Poggendorff illusion",
        "vlmbias_folder": "poggendorff",
    },
    {
        "key": "zollner",
        "name": "Zöllner",
        "description": "Two long horizontal lines, one above the other. Each line is crossed by many "
                       "short diagonal strokes. The strokes on the upper line lean one way and the "
                       "strokes on the lower line lean the other way.",
        "vlmbias_sub_topic": "Zöllner illusion",
        "vlmbias_folder": "zollner",
    },
    {
        "key": "none",
        "name": "None",
        "description": "A figure that matches none of the six descriptions above.",
        "vlmbias_sub_topic": None,
        "vlmbias_folder": None,
    },
]

ILLUSION_KEYS = [illusion["key"] for illusion in ILLUSIONS]

PAPER_KEYS = ILLUSION_KEYS[:6]

# Words that state the outcome of the comparison, or lean on the illusion's name. Checked as
# whole words (or the exact phrase), case-insensitively, in every description.
FORBIDDEN_WORDS = [
    "equal", "unequal", "same", "different", "longer", "shorter", "larger", "smaller", "bigger",
    "aligned", "misaligned", "parallel", "collinear", "straight line", "illusion", "appears",
    "looks", "seems",
]


def by_key(key):
    """The class with this key."""
    for illusion in ILLUSIONS:
        if illusion["key"] == key:
            return illusion
    raise KeyError(f"unknown illusion key '{key}'; known: {ILLUSION_KEYS}")


def folder_to_key():
    """The VLMBias image folder of each paper class -> the illusion key."""
    mapping = {}
    for illusion in ILLUSIONS:
        if illusion["vlmbias_folder"] is not None:
            mapping[illusion["vlmbias_folder"]] = illusion["key"]
    return mapping


def check_descriptions():
    """Every (key, forbidden word) pair found in a description. Empty when all are clean."""
    found = []
    for illusion in ILLUSIONS:
        lowered = illusion["description"].lower()
        for word in FORBIDDEN_WORDS:
            pattern = r"\b" + re.escape(word) + r"\b"
            if re.search(pattern, lowered) is not None:
                found.append((illusion["key"], word))
    return found
