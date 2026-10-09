import pytest

from intent_harness import Harness, LoadError, RegistrationError
from intent_harness.loading import parse_list

from tests.plugins import fake_classifier

TOOLS = "tests.plugins.fake_tools"
INTENTS = "tests.plugins.fake_intents"
CLASSIFIER = "tests.plugins.fake_classifier"


def test_load_in_code_from_module_paths():
    harness = Harness().load_tools(TOOLS).load_intents(INTENTS).load_classifier(CLASSIFIER, model="m")
    assert sorted(harness.registry.tools) == ["add"]
    assert sorted(harness.registry.intents) == ["echo", "sum"]
    assert fake_classifier.RECEIVED == {"model": "m"}
    assert harness.answer(1, "q").value == 4


def test_from_env_loads_in_order_and_passes_model(tmp_path):
    env = tmp_path / ".env"
    env.write_text(
        f"INTENT_HARNESS_TOOLS={TOOLS}\n"
        f"INTENT_HARNESS_INTENTS={INTENTS}\n"
        f"INTENT_HARNESS_CLASSIFIER={CLASSIFIER}\n"
        "INTENT_HARNESS_CLASSIFIER_MODEL=small-model\n"
    )
    harness = Harness.from_env(env)
    assert fake_classifier.RECEIVED == {"model": "small-model"}
    answer = harness.answer(5, "q")
    assert (answer.intent, answer.value) == ("sum", 8)


def test_from_env_intents_before_tools_fails(tmp_path):
    env = tmp_path / ".env"
    env.write_text(f"INTENT_HARNESS_INTENTS={INTENTS}\n")
    with pytest.raises(RegistrationError, match="not registered"):
        Harness.from_env(env)


def test_from_env_does_not_change_process_environment(tmp_path, monkeypatch):
    monkeypatch.delenv("INTENT_HARNESS_TOOLS", raising=False)
    env = tmp_path / ".env"
    env.write_text(f"INTENT_HARNESS_TOOLS={TOOLS}\n")
    Harness.from_env(env)
    import os
    assert "INTENT_HARNESS_TOOLS" not in os.environ


def test_missing_env_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        Harness.from_env(tmp_path / "absent.env")


def test_module_that_does_not_import_is_named():
    with pytest.raises(LoadError, match="tests.plugins.absent"):
        Harness().load_tools("tests.plugins.absent")


def test_module_without_register_is_named():
    with pytest.raises(LoadError, match="no_register"):
        Harness().load_tools("tests.plugins.no_register")


def test_parse_list_skips_empty_items():
    assert parse_list("a,,b, ,c") == ["a", "b", "c"]
    assert parse_list("") == []
    assert parse_list(None) == []
