"""The structural intent on the 396 VLMBias illusion images.

Skipped unless INTENT_HARNESS_VLMBIAS_DIR points to the `benchmark-main` folder of the VLMBias
dataset. The recorded numbers are from the experiment workspace (notebooks 11 and 14 to 19).
"""

import os
from pathlib import Path

import pytest
from PIL import Image

from intent_harness import Choice, Harness
from intent_harness_structural import PAPER_KEYS
from intent_harness_structural.illusions import folder_to_key

BENCHMARK_DIR = os.environ.get("INTENT_HARNESS_VLMBIAS_DIR")

pytestmark = pytest.mark.skipif(not BENCHMARK_DIR, reason="INTENT_HARNESS_VLMBIAS_DIR is not set")

# Correct answers (originals correct, originals total, edited correct, edited total).
RECORDED_ACCURACY = {
    "muller_lyer": (36, 36, 36, 36),
    "ponzo": (36, 36, 24, 36),
    "vertical_horizontal": (18, 18, 18, 18),
    "ebbinghaus": (36, 36, 36, 36),
    "poggendorff": (36, 36, 36, 36),
    "zollner": (36, 36, 36, 36),
}


class StructuralOnly:
    def classify(self, question, intents):
        return Choice(key="structural", probabilities={"structural": 1.0}, confidence=1.0)


@pytest.fixture(scope="module")
def answered():
    harness = Harness()
    harness.load_tools("intent_harness_tools.measurement_plugin")
    harness.load_intents("intent_harness_structural.plugin")
    harness.register_classifier(StructuralOnly())
    root = Path(BENCHMARK_DIR) / "vlms-are-biased-notitle"
    rows = []
    for folder, key in folder_to_key().items():
        for path in sorted((root / folder / "images").glob("*.png")):
            original = "_diff0_" in path.name
            answer = harness.answer(Image.open(path), "")
            rows.append({"illusion": key, "original": original, "named": answer.pipeline,
                         "correct": answer.value == ("Yes" if original else "No")})
    return rows


def test_396_images(answered):
    assert len(answered) == 396
    assert sum(row["original"] for row in answered) == 198


def test_pixel_rules_name_all_396_images(answered):
    assert sum(row["named"] == row["illusion"] for row in answered) == 396


def test_accuracy_per_illusion_equals_the_recorded_accuracy(answered):
    accuracy = {}
    for key in PAPER_KEYS:
        originals = [row for row in answered if row["illusion"] == key and row["original"]]
        edited = [row for row in answered if row["illusion"] == key and not row["original"]]
        accuracy[key] = (sum(row["correct"] for row in originals), len(originals),
                         sum(row["correct"] for row in edited), len(edited))
    assert accuracy == RECORDED_ACCURACY
