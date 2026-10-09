"""The quantity intent and its legs pipeline, with fake localizers in place of the models."""

import numpy as np
import pytest

from intent_harness import Harness, RegistrationError, Result
from intent_harness_quantity import LegsPipeline, QuantityIntent
from intent_harness_tools.sam3 import keep_smaller_regions, mask_to_box, remove_duplicate_regions
from tests.fakes import FixedClassifier

SIZE = 256


def rectangle(row0, col0, row1, col1):
    mask = np.zeros((SIZE, SIZE), dtype=bool)
    mask[row0:row1, col0:col1] = True
    return mask


def region(mask, score):
    return {"box": mask_to_box(mask), "score": score, "mask": mask}


class FakeImage:
    """Stands in for an image: carries the regions the fake segmenter returns."""

    def __init__(self, regions, animal=(0.0, 0.0, 1.0, 1.0)):
        self.regions = regions
        self.animal = list(animal)


def fake_best_box(image, query):
    return image.animal


def fake_segment_concept(image, concept, min_score=0.01):
    return [r for r in image.regions if r["score"] >= min_score]


def leg_harness():
    harness = Harness()
    harness.register_tool(fake_best_box, name="best_box")
    harness.register_tool(fake_segment_concept, name="segment_concept")
    harness.register_tool(keep_smaller_regions, name="keep_smaller_regions")
    harness.register_tool(remove_duplicate_regions, name="remove_duplicate_regions")
    harness.load_intents("intent_harness_quantity.plugin")
    harness.register_classifier(FixedClassifier("quantity"))
    return harness


def four_legs_and_noise():
    legs = [
        region(rectangle(150, 20, 250, 40), 0.95),
        region(rectangle(150, 70, 250, 90), 0.9),
        region(rectangle(150, 130, 250, 150), 0.85),
        region(rectangle(150, 190, 250, 210), 0.8),
    ]
    duplicate = region(rectangle(152, 20, 250, 40), 0.7)      # same leg as the first
    inside = region(rectangle(160, 72, 200, 88), 0.6)          # nested in the second
    low = region(rectangle(10, 10, 40, 40), 0.3)               # below the threshold
    body = region(rectangle(0, 0, 240, 256), 0.99)             # too big for the size rule
    return legs + [duplicate, inside, low, body]


def test_harness_counts_legs_with_trace_in_order():
    answer = leg_harness().answer(FakeImage(four_legs_and_noise()), "How many legs does it have?")
    assert answer.intent == "quantity"
    assert answer.pipeline == "legs"
    assert answer.value == 4
    assert [step.tool for step in answer.trace] == [
        "best_box", "segment_concept", "keep_smaller_regions", "remove_duplicate_regions"]
    assert answer.trace[0].inputs["query"] == "animal"
    assert answer.trace[1].inputs["concept"] == "leg"


def test_added_leg_gives_one_more():
    regions = four_legs_and_noise() + [region(rectangle(150, 230, 250, 250), 0.75)]
    assert leg_harness().answer(FakeImage(regions), "How many legs?").value == 5


def test_no_region_counts_zero():
    assert leg_harness().answer(FakeImage([]), "How many legs?").value == 0


def test_size_rule_uses_the_animal_box():
    small_animal = (0.5, 0.5, 0.7, 0.7)                       # half its area is 0.02: a leg of 0.03 is too big
    regions = [region(rectangle(150, 20, 250, 40), 0.95)]
    assert leg_harness().answer(FakeImage(regions, small_animal), "How many legs?").value == 0


def test_plugin_needs_the_tools_first():
    harness = Harness()
    with pytest.raises(RegistrationError):
        harness.load_intents("intent_harness_quantity.plugin")


class FakePipeline:
    def __init__(self, name, tools, value):
        self.name = name
        self.required_tools = tools
        self.value = value

    def count(self, image, question, tools):
        return self.value


def test_one_pipeline_runs_without_selector():
    intent = QuantityIntent([FakePipeline("legs", ("a",), 4)])
    assert intent.run(None, "q", {}) == Result(value=4, pipeline="legs")


def test_selector_chooses_among_pipelines():
    seen = []

    def selector(image, question, names):
        seen.append(names)
        return "stars"

    intent = QuantityIntent(
        [FakePipeline("legs", ("a", "b"), 4), FakePipeline("stars", ("b", "c"), 50)], selector)
    assert intent.required_tools == ("a", "b", "c")
    assert intent.run(None, "How many stars?", {}) == Result(value=50, pipeline="stars")
    assert seen == [["legs", "stars"]]


def test_two_pipelines_without_selector_raise():
    intent = QuantityIntent([FakePipeline("legs", (), 4), FakePipeline("stars", (), 50)])
    with pytest.raises(RuntimeError, match="legs"):
        intent.run(None, "q", {})


def test_selector_with_unknown_name_raises():
    intent = QuantityIntent([FakePipeline("legs", (), 4)], lambda image, question, names: "dice")
    with pytest.raises(RuntimeError, match="dice"):
        intent.run(None, "q", {})


def test_duplicate_pipeline_names_raise():
    with pytest.raises(ValueError):
        QuantityIntent([FakePipeline("legs", (), 4), FakePipeline("legs", (), 5)])


def test_legs_pipeline_constants_match_the_experiment():
    pipeline = LegsPipeline()
    assert pipeline.name == "legs"
    from intent_harness_quantity import legs

    assert (legs.MIN_SCORE, legs.SIZE_RULE, legs.MAX_REGIONS, legs.THRESHOLD, legs.NESTED) == (
        0.01, 0.5, 150, 0.48, True)


def test_tool_plugins_register_names():
    harness = Harness()
    harness.load_tools("intent_harness_tools.grounding_dino_plugin", "intent_harness_tools.sam3_plugin")
    assert sorted(harness.registry.tools) == [
        "best_box", "keep_smaller_regions", "remove_duplicate_regions", "segment_concept"]
    harness.load_intents("intent_harness_quantity.plugin")
    assert list(harness.registry.intents) == ["quantity"]
