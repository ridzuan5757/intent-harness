"""The structural intent and the measurement tools plugin, on drawn figures."""

import subprocess
import sys

import pytest
from PIL import Image

from intent_harness import Choice, Harness, RegistrationError
from intent_harness_structural import (MEASUREMENT_TOOLS, PAPER_KEYS, PIPELINES, PIXEL_RULE_TOOL,
                                       TOLERANCES, StructuralIntent, rules_hash)
from intent_harness_structural.illusions import ILLUSIONS, check_descriptions
from intent_harness_tools.measurement_plugin import TOOL_NAMES

from tests import structural_figures as figures

# The hash of the pixel rules frozen in the experiment workspace on 2026-10-04.
FROZEN_RULES_HASH = "2da696c4843f98c5858538433905815d5ee5fc00f38202121563ba1ecc040c53"


class StructuralOnly:
    def classify(self, question, intents):
        return Choice(key="structural", probabilities={"structural": 1.0}, confidence=1.0)


def build():
    harness = Harness()
    harness.load_tools("intent_harness_tools.measurement_plugin")
    harness.load_intents("intent_harness_structural.plugin")
    harness.register_classifier(StructuralOnly())
    return harness


FIGURES = {
    "muller_lyer": (figures.muller_lyer, 0.0, 0.3),
    "ponzo": (figures.ponzo, 0.0, 0.25),
    "vertical_horizontal": (figures.vertical_horizontal, 0.0, 0.3),
    "ebbinghaus": (figures.ebbinghaus, 0.0, 0.3),
    "poggendorff": (figures.poggendorff, 0, 40),
    "zollner": (figures.zollner, 0.0, 3.0),
}


# ---------------------------------------------------------------- tools plugin (User Story 3)

def test_measurement_plugin_registers_eight_tools_by_function_name():
    harness = Harness()
    harness.load_tools("intent_harness_tools.measurement_plugin")
    assert sorted(harness.registry.tools) == sorted(TOOL_NAMES)
    assert sorted(TOOL_NAMES) == sorted(["colour_mask", "group_shapes", "find_runs", "direction_filter",
                                         "equivalent_diameter", "fit_line", "point_line_distance", "decide"])


def test_structural_intent_before_tools_fails_and_names_missing_tools():
    harness = Harness()
    with pytest.raises(RegistrationError) as error:
        harness.register_intent(StructuralIntent())
    assert "colour_mask" in str(error.value)


def test_intent_declares_every_tool_it_uses():
    assert set(StructuralIntent.required_tools) == set(MEASUREMENT_TOOLS) | {PIXEL_RULE_TOOL}
    assert set(MEASUREMENT_TOOLS) == set(TOOL_NAMES)


# ---------------------------------------------------------------- moved code is unchanged

def test_pixel_rules_hash_equals_the_frozen_experiment_hash():
    assert rules_hash() == FROZEN_RULES_HASH


def test_descriptions_hold_no_outcome_word():
    assert check_descriptions() == []
    assert [illusion["key"] for illusion in ILLUSIONS][:6] == PAPER_KEYS


def test_tolerances_cover_the_six_illusions():
    assert sorted(TOLERANCES) == sorted(PAPER_KEYS) == sorted(PIPELINES)


def test_structural_package_does_not_import_the_tools_package():
    code = (
        "import sys\n"
        "import intent_harness_structural\n"
        "print(','.join(n for n in sys.modules if n.startswith('intent_harness_tools')))\n"
    )
    result = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, check=True)
    assert result.stdout.strip() == ""


# ---------------------------------------------------------------- answers on drawn figures (US1, US2)

@pytest.mark.parametrize("key", PAPER_KEYS)
def test_pixel_rules_name_each_drawn_figure(key):
    draw, equal, changed = FIGURES[key]
    harness = build()
    assert harness.answer(draw(equal), "").pipeline == key
    assert harness.answer(draw(changed), "").pipeline == key


@pytest.mark.parametrize("key", PAPER_KEYS)
def test_equal_parts_answer_yes_and_changed_parts_answer_no(key):
    draw, equal, changed = FIGURES[key]
    harness = build()
    assert harness.answer(draw(equal), "Are the two parts equal?").value == "Yes"
    assert harness.answer(draw(changed), "Are the two parts equal?").value == "No"


def test_trace_starts_with_the_rules_and_ends_with_decide():
    answer = build().answer(figures.ebbinghaus(0.3), "Are the two red circles equal in size?")
    tools = [step.tool for step in answer.trace]
    assert tools == [PIXEL_RULE_TOOL, "colour_mask", "group_shapes", "equivalent_diameter",
                     "equivalent_diameter", "decide"]
    assert answer.trace[0].output == "ebbinghaus"
    assert answer.trace[-1].inputs["tolerance"] == TOLERANCES["ebbinghaus"]
    assert answer.intent == "structural"
    assert answer.pipeline == "ebbinghaus"


def test_blank_image_gives_pipeline_none_and_value_none():
    answer = build().answer(Image.new("RGB", (256, 256), "white"), "")
    assert answer.pipeline == "none"
    assert answer.value is None
    assert [step.tool for step in answer.trace] == [PIXEL_RULE_TOOL]


def test_shapes_not_found_gives_value_none():
    # Three red discs: the Ebbinghaus pipeline expects exactly two.
    from intent_harness_tools import draw_discs
    image = draw_discs(768, [((150, 384), 90), ((384, 384), 90), ((620, 384), 90)])
    answer = build().answer(image, "")
    assert answer.pipeline == "ebbinghaus"
    assert answer.value is None
    assert answer.trace[-1].tool == "group_shapes"
