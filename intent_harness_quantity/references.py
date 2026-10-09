"""Reference crops for the chess and xiangqi piece counters.

The piece counters compare each square or intersection with grey crops cut from the unedited
VLMBias boards at their known starting positions. The rules are those of the experiment
(grounded-count-harness, harness/counting.py, `board_references`), unchanged.

The crops are shipped in `board_references.npz` next to this file, so a user does not need the
benchmark images. `build_board_references` rebuilds them from the two unedited boards; the check
`specs/006-quantity-subtopics/checks/build_references.py` shows that the shipped file equals the
experiment's crops.
"""

import os

import numpy as np
from PIL import Image

REFERENCE_SIDE = 32
CHESS_SQUARE_COLOURS = [np.array([255, 206, 158]), np.array([209, 139, 71])]
CHESS_BACK_RANK = ["Rook", "Knight", "Bishop", "Queen", "King", "Bishop", "Knight", "Rook"]
XIANGQI_BACK_RANK = ["Chariot", "Knight", "Elephant", "Advisor", "General", "Advisor", "Elephant",
                     "Knight", "Chariot"]

SHIPPED_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "board_references.npz")


# ---------------------------------------------------------------- crops (shared with the counters)

def grey_patch(values):
    """A REFERENCE_SIDE x REFERENCE_SIDE grey patch of a 2-D value array (clipped to 0-255)."""
    return np.asarray(Image.fromarray(np.clip(values, 0, 255).astype(np.uint8)).resize(
        (REFERENCE_SIDE, REFERENCE_SIDE), Image.BILINEAR)).astype(float)


def chess_squares(rgb):
    """The 64 squares of a board that fills the image, inset by 1/16 of a square."""
    side = rgb.shape[0] // 8
    inset = side // 16
    squares = []
    for row in range(8):
        for column in range(8):
            squares.append((row, column, rgb[row * side + inset:(row + 1) * side - inset,
                                             column * side + inset:(column + 1) * side - inset]))
    return squares


def chess_feature(square):
    """A square -> grey patch with square-coloured pixels set to 128, and the share of piece pixels."""
    values = square.astype(int)
    distances = []
    for colour in CHESS_SQUARE_COLOURS:
        distances.append(np.abs(values - colour).sum(axis=2))
    piece = np.min(np.stack(distances), axis=0) > 60
    brightness = 0.299 * values[:, :, 0] + 0.587 * values[:, :, 1] + 0.114 * values[:, :, 2]
    return grey_patch(np.where(piece, brightness, 128.0)), float(piece.mean())


def xiangqi_rings(rgb):
    """Piece borders of an unedited xiangqi board: hollow, roughly square rings of near-black or
    strong-red pixels; concentric rings of one piece count once. Boxes (top, bottom, left, right)."""
    from scipy import ndimage

    ring = (rgb.max(axis=2) < 60) | ((rgb[:, :, 0] > 150) & (rgb[:, :, 1] < 90) & (rgb[:, :, 2] < 90))
    labels, count = ndimage.label(ring, structure=np.ones((3, 3)))
    width = rgb.shape[1]
    rings = []
    for found, label in zip(ndimage.find_objects(labels), range(1, count + 1)):
        height_box = found[0].stop - found[0].start
        width_box = found[1].stop - found[1].start
        if height_box < 0.04 * width or width_box < 0.04 * width or height_box > 0.2 * width:
            continue
        if not (0.75 <= height_box / width_box <= 1.33):
            continue
        if (labels[found] == label).mean() > 0.5:
            continue
        rings.append((found[0].start, found[0].stop, found[1].start, found[1].stop))
    rings.sort(key=lambda box: -(box[1] - box[0]) * (box[3] - box[2]))
    pieces = []
    for box in rings:
        centre_row = (box[0] + box[1]) / 2.0
        centre_col = (box[2] + box[3]) / 2.0
        inside = False
        for kept in pieces:
            if kept[0] <= centre_row <= kept[1] and kept[2] <= centre_col <= kept[3]:
                inside = True
        if not inside:
            pieces.append(box)
    return pieces


def xiangqi_crop(rgb, centre_row, centre_col, size):
    """The grey patch of a size x size crop around one intersection."""
    top = int(round(max(0.0, centre_row - size / 2.0)))
    left = int(round(max(0.0, centre_col - size / 2.0)))
    crop = rgb[top:int(round(centre_row + size / 2.0)), left:int(round(centre_col + size / 2.0))].astype(int)
    brightness = 0.299 * crop[:, :, 0] + 0.587 * crop[:, :, 1] + 0.114 * crop[:, :, 2]
    return grey_patch(brightness)


# ---------------------------------------------------------------- build, save, load

def build_board_references(chess_image, xiangqi_image, cluster):
    """The reference crops from the unedited chess and xiangqi boards (PIL images).

    `cluster(values, gap)` is the counting tool of the same name. Returns
    {"chess": {"references": [...]}, "xiangqi": {"references": [...], "columns", "rows", "size"}},
    where each reference is {"kind", "feature"} and the xiangqi grid is in fractions of the width.
    """
    chess = []
    for row, column, square in chess_squares(np.asarray(chess_image.convert("RGB"))):
        if row in (0, 7):
            kind = CHESS_BACK_RANK[column]
        elif row in (1, 6):
            kind = "Pawn"
        else:
            continue
        feature, share = chess_feature(square)
        chess.append({"kind": kind, "feature": feature})

    rgb = np.asarray(xiangqi_image.convert("RGB"))
    width = rgb.shape[1]
    pieces = xiangqi_rings(rgb)
    sizes = []
    column_centres = []
    row_centres = []
    for top, bottom, left, right in pieces:
        sizes.append(bottom - top)
        column_centres.append((left + right) / 2.0)
        row_centres.append((top + bottom) / 2.0)
    size = float(np.median(sizes))
    columns = cluster(column_centres, 0.5 * size)
    occupied_rows = cluster(row_centres, 0.5 * size)
    slope, intercept = np.polyfit([0, 2, 3, 6, 7, 9], occupied_rows, 1)
    rows = []
    for index in range(10):
        rows.append(intercept + slope * index)
    layout = {}
    for column in range(9):
        layout[(0, column)] = XIANGQI_BACK_RANK[column]
        layout[(9, column)] = XIANGQI_BACK_RANK[column]
    for column in (1, 7):
        layout[(2, column)] = "Cannon"
        layout[(7, column)] = "Cannon"
    for column in (0, 2, 4, 6, 8):
        layout[(3, column)] = "Soldier"
        layout[(6, column)] = "Soldier"
    xiangqi = []
    for row_index in range(10):
        for column_index in range(9):
            xiangqi.append({"kind": layout.get((row_index, column_index), "empty"),
                            "feature": xiangqi_crop(rgb, rows[row_index], columns[column_index], size)})
    return {
        "chess": {"references": chess},
        "xiangqi": {"references": xiangqi, "columns": [value / width for value in columns],
                    "rows": [value / width for value in rows], "size": size / width},
    }


def save_board_references(references, path=SHIPPED_FILE):
    """Write the references as uint8 crops (lossless: every crop is a resized uint8 image)."""
    arrays = {}
    for board in ("chess", "xiangqi"):
        features = []
        kinds = []
        for reference in references[board]["references"]:
            feature = reference["feature"]
            if not np.array_equal(feature, np.round(feature)) or feature.min() < 0 or feature.max() > 255:
                raise ValueError("A reference crop is not a uint8 image; it cannot be saved losslessly.")
            features.append(feature.astype(np.uint8))
            kinds.append(reference["kind"])
        arrays[f"{board}_features"] = np.stack(features)
        arrays[f"{board}_kinds"] = np.array(kinds)
    arrays["xiangqi_columns"] = np.array(references["xiangqi"]["columns"], dtype=float)
    arrays["xiangqi_rows"] = np.array(references["xiangqi"]["rows"], dtype=float)
    arrays["xiangqi_size"] = np.array(references["xiangqi"]["size"], dtype=float)
    np.savez_compressed(path, **arrays)


_loaded = {}


def load_board_references(path=SHIPPED_FILE):
    """The references in the same form as `build_board_references` returns them."""
    if path not in _loaded:
        with np.load(path, allow_pickle=False) as data:
            references = {}
            for board in ("chess", "xiangqi"):
                items = []
                for feature, kind in zip(data[f"{board}_features"], data[f"{board}_kinds"]):
                    items.append({"kind": str(kind), "feature": feature.astype(float)})
                references[board] = {"references": items}
            references["xiangqi"]["columns"] = [float(value) for value in data["xiangqi_columns"]]
            references["xiangqi"]["rows"] = [float(value) for value in data["xiangqi_rows"]]
            references["xiangqi"]["size"] = float(data["xiangqi_size"])
        _loaded[path] = references
    return _loaded[path]
