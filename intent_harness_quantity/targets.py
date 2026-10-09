"""Read what a counting question asks for: the target kind and its detail.

The rules are those of the experiment (grounded-count-harness, harness/datasets.py,
`COUNT_TARGET_RULES`), unchanged. They are applied in order; the first match wins.
"""

import re

CHESS_KINDS = ["King", "Queen", "Rook", "Bishop", "Knight", "Pawn"]
XIANGQI_KINDS = ["General", "Advisor", "Elephant", "Horse", "Knight", "Chariot", "Cannon", "Soldier"]

# (rule number, pattern, target kind)
COUNT_TARGET_RULES = [
    (1, r"in cell ([A-Z])(\d+)", "cell"),
    (2, r"\b(" + "|".join(CHESS_KINDS) + r") pieces\b", "kind"),
    (3, r"\b(" + "|".join(XIANGQI_KINDS) + r") pieces\b", "kind"),
    (4, r"\b(chess|xiangqi) pieces\b", "all pieces"),
    (5, r"\bhorizontal lines\b", "horizontal lines"),
    (6, r"\bvertical lines\b", "vertical lines"),
    (7, r"\brows\b", "rows"),
    (8, r"\bcolumns\b", "columns"),
    (9, r"\bpoints\b.*\bstar\b", "star points"),
    (10, r"\bstars\b", "stars"),
    (11, r"\bstripes in this flag|stripes are there in this flag", "stripes"),
    (12, r"\bprongs\b", "prongs"),
    (13, r"\boverlapping circles\b", "overlapping circles"),
    (14, r"\b(white|black) (stripes|stylized curves)\b", "shoe element"),
    (15, r"\bvisible (stripes|stylized curves)\b", "shoe element"),
]


def read_target(question):
    """(rule number, target kind, detail) for a counting question, or (0, None, None).

    The detail is the cell name for "cell" ("C3"), the piece kind for "kind" ("Knight"), the
    colour and element for rule 14 ("white stripes"), "any <element>" for rule 15, else "".
    """
    for number, pattern, kind in COUNT_TARGET_RULES:
        match = re.search(pattern, question)
        if match is None:
            continue
        if kind == "cell":
            return number, kind, f"{match.group(1)}{match.group(2)}"
        if kind == "kind":
            return number, kind, match.group(1)
        if kind == "shoe element" and number == 14:
            return number, kind, f"{match.group(1)} {match.group(2)}"
        if kind == "shoe element":
            return number, kind, f"any {match.group(1)}"
        return number, kind, ""
    return 0, None, None
