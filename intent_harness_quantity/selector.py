"""The counter selector: choose a counting pipeline from the question.

User decision 2026-10-09: text rules plus one image check. The rules were derived from every
counting prompt of VLMBias (`benchmark-main` and `benchmark-original`). They are applied in
order; the first match wins. Two questions are the same text for two sub-topics; one image check
splits them:

- "Knight pieces": chess or xiangqi pieces.
- "horizontal lines" / "vertical lines": a go board or a xiangqi board.

The image check is the aspect ratio: every VLMBias xiangqi image is 1.125 times as tall as it is
wide, and every chess and go image is square. A question that no rule matches gives None.
"""

import re

TALL_LIMIT = 1.06    # height / width above this: a xiangqi board

CHESS_ONLY_KINDS = ("King", "Queen", "Rook", "Bishop", "Pawn")
XIANGQI_ONLY_KINDS = ("General", "Advisor", "Elephant", "Horse", "Chariot", "Cannon", "Soldier")

# (rule number, description, test on the lower-case question, counter or image-check key)
SELECTOR_RULES = [
    (1, '"leg" or "legs"', lambda q: re.search(r"\blegs?\b", q), "legs"),
    (2, '"in cell X9" and "circles"', lambda q: re.search(r"\bin cell [a-z]\d+", q) and "circles" in q, "dice"),
    (3, '"in cell X9" and "lines"', lambda q: re.search(r"\bin cell [a-z]\d+", q) and "lines" in q, "tally"),
    (4, '"chess pieces" or a chess-only kind', lambda q: re.search(
        r"\b(chess|" + "|".join(kind.lower() for kind in CHESS_ONLY_KINDS) + r") pieces\b", q), "chess_pieces"),
    (5, '"xiangqi pieces" or a xiangqi-only kind', lambda q: re.search(
        r"\b(xiangqi|" + "|".join(kind.lower() for kind in XIANGQI_ONLY_KINDS) + r") pieces\b", q), "xiangqi_pieces"),
    (6, '"Knight pieces"', lambda q: re.search(r"\bknight pieces\b", q), "tall:xiangqi_pieces:chess_pieces"),
    (7, '"horizontal lines" or "vertical lines"', lambda q: re.search(r"\b(horizontal|vertical) lines\b", q),
     "tall:xiangqi_grid:go_grid"),
    (8, '"rows" or "columns", and "puzzle"', lambda q: re.search(r"\b(rows|columns)\b", q) and "puzzle" in q,
     "sudoku_grid"),
    (9, '"rows" or "columns", and "board"', lambda q: re.search(r"\b(rows|columns)\b", q) and "board" in q,
     "chess_grid"),
    (10, '"logo" and "car"', lambda q: "logo" in q and re.search(r"\bcar\b", q), "car_logos"),
    (11, '"logo" and "shoe"', lambda q: "logo" in q and re.search(r"\bshoe\b", q), "shoe_logos"),
    (12, '"flag" and "stars"', lambda q: "flag" in q and re.search(r"\bstars\b", q), "flag_stars"),
    (13, '"flag" and "stripes"', lambda q: "flag" in q and re.search(r"\bstripes\b", q), "flag_stripes"),
]


def is_tall(image):
    """True when the image is more than TALL_LIMIT times as tall as it is wide."""
    width, height = image.size
    return height > TALL_LIMIT * width


def select_counter(image, question):
    """The name of the counting pipeline for `question`, or None when no rule matches."""
    text = question.lower()
    for number, description, test, choice in SELECTOR_RULES:
        if not test(text):
            continue
        if choice.startswith("tall:"):
            prefix, if_tall, otherwise = choice.split(":")
            return if_tall if is_tall(image) else otherwise
        return choice
    return None
