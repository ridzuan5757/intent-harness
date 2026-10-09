"""The counting pipelines on a small sample of VLMBias counting images.

Skipped unless INTENT_HARNESS_VLMBIAS_DIR points to the `benchmark-main` folder of the VLMBias
dataset. Image paths below are relative to its parent folder. The recorded counts are those of
the experiment workspace (results/23 to 26-*.parquet); the sample has 2 items per pixel
sub-topic, with one item the experiment counted wrong where the sub-topic has one. The full sets
run in the paper notebooks.
"""

import os
from pathlib import Path

import pytest
from PIL import Image

from intent_harness import Choice, Harness

BENCHMARK_DIR = os.environ.get("INTENT_HARNESS_VLMBIAS_DIR")

pytestmark = pytest.mark.skipif(not BENCHMARK_DIR, reason="INTENT_HARNESS_VLMBIAS_DIR is not set")

MAIN = "benchmark-main/vlms-are-biased-notitle"
ORIGINAL = "benchmark-original/original_images/images"

# (image path, question, recorded count, counter). The comment says whether the recorded count
# is the right count.
SAMPLE = [
    (f"{MAIN}/chess_grid/images/chess_grid_01_row_remove_first_row_notitle_px1152.png",
     "How many rows are there on this board?", 7, "chess_grid"),                    # right
    (f"{MAIN}/chess_grid/images/chess_grid_01_row_remove_first_row_notitle_px384.png",
     "How many rows are there on this board?", 7, "chess_grid"),                    # right
    (f"{MAIN}/sudoku_grid/images/sudoku_grid_01_row_add_first_row_notitle_px1152.png",
     "How many rows are there on this puzzle?", 10, "sudoku_grid"),                 # right
    (f"{MAIN}/sudoku_grid/images/sudoku_grid_01_row_add_first_row_notitle_px384.png",
     "How many rows are there on this puzzle?", 10, "sudoku_grid"),                 # right
    (f"{MAIN}/xiangqi_grid/images/xiangqi_grid_01_row_remove_row_before_river_notitle_px1152.png",
     "How many horizontal lines are there on this board?", 9, "xiangqi_grid"),      # right
    (f"{MAIN}/xiangqi_grid/images/xiangqi_grid_01_row_remove_row_before_river_notitle_px384.png",
     "How many horizontal lines are there on this board?", 9, "xiangqi_grid"),      # right
    (f"{MAIN}/go_grid/images/go_grid_01_remove_row_px1152.png",
     "How many horizontal lines are there on this board?", 18, "go_grid"),          # right
    (f"{MAIN}/go_grid/images/go_grid_01_remove_row_px384.png",
     "How many horizontal lines are there on this board?", 18, "go_grid"),          # right
    (f"{ORIGINAL}/chess_pieces_notitle_px1152.png",
     "How many chess pieces are there on this board?", 32, "chess_pieces"),         # right
    (f"{MAIN}/chess_pieces/images/chess_pieces_001_remove_whiteknight_at_g1_notitle_px1152.png",
     "How many chess pieces are there on this board?", 31, "chess_pieces"),         # right
    (f"{ORIGINAL}/xiangqi_pieces_notitle_px1152.png",
     "How many xiangqi pieces are there on this board?", 32, "xiangqi_pieces"),     # right
    (f"{MAIN}/xiangqi_pieces/images/xiangqi_pieces_001_remove_black_knight_at_b1_notitle_px1152.png",
     "How many xiangqi pieces are there on this board?", 31, "xiangqi_pieces"),     # right
    (f"{MAIN}/flag_stars/images/Flag of Burundi-stars=4_384.png",
     "How many stars are there in this flag?", 2, "flag_stars"),                    # wrong
    (f"{MAIN}/flag_stars/images/Flag of Australia-stars=5_1152.png",
     "How many stars are there in this flag?", 5, "flag_stars"),                    # right
    (f"{MAIN}/flag_stripes/images/Flag of Cuba-stripes=4_1152.png",
     "How many stripes are there in this flag?", 4, "flag_stripes"),                # right
    (f"{MAIN}/flag_stripes/images/Flag of Cuba-stripes=4_384.png",
     "How many stripes are there in this flag?", 4, "flag_stripes"),                # right
    (f"{MAIN}/dice/images/dice_002_replace_E5_notitle_px1152.png",
     "How many circles are there in cell E5?", 3, "dice"),                          # wrong
    (f"{MAIN}/dice/images/dice_001_remove_C3_notitle_px1152.png",
     "How many circles are there in cell C3?", 2, "dice"),                          # right
    (f"{MAIN}/tally/images/tally_003_add_D4_notitle_px1152.png",
     "How many lines are there in cell D4?", 1, "tally"),                           # wrong
    (f"{MAIN}/tally/images/tally_001_add_C3_notitle_px1152.png",
     "How many lines are there in cell C3?", 4, "tally"),                           # right
]


class QuantityOnly:
    def classify(self, question, intents):
        return Choice(key="quantity", probabilities={"quantity": 1.0}, confidence=1.0)


@pytest.fixture(scope="module")
def harness():
    h = Harness()
    h.load_tools("intent_harness_tools.counting_plugin",
                 "intent_harness_tools.grounding_dino_plugin",
                 "intent_harness_tools.sam3_plugin")
    h.load_intents("intent_harness_quantity.plugin")
    h.register_classifier(QuantityOnly())
    return h


@pytest.mark.parametrize("path, question, recorded, counter", SAMPLE)
def test_count_equals_the_recorded_count(harness, path, question, recorded, counter):
    image = Image.open(Path(BENCHMARK_DIR).parent / path).convert("RGB")
    answer = harness.answer(image, question)
    assert answer.pipeline == counter
    assert answer.value == recorded
    assert answer.trace[0].tool == "select_counter"
