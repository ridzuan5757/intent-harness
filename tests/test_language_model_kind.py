"""The model kind comes from the config: a config with a vision part loads as a vision-language
model used on text only. No model is loaded here."""

from types import SimpleNamespace

import pytest

from intent_harness_classifiers.language_model import KINDS, LanguageModel, detect_kind


def test_a_config_with_a_vision_part_is_a_vision_language_model():
    config = SimpleNamespace(vision_config=SimpleNamespace(hidden_size=8))
    assert detect_kind(config) == "vlm"


def test_a_config_without_a_vision_part_is_a_text_only_model():
    assert detect_kind(SimpleNamespace(hidden_size=8)) == "lm"
    assert detect_kind(SimpleNamespace(vision_config=None)) == "lm"


def test_the_two_kinds():
    assert KINDS == ("lm", "vlm")


def test_an_unknown_kind_is_refused_before_any_load():
    pytest.importorskip("torch")
    with pytest.raises(ValueError, match="kind must be"):
        LanguageModel("any-model", device="cpu", kind="audio")
