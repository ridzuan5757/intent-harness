"""The run helpers of the paper scripts: resume, the completion marker, the refusal of an
incomplete run, smoke-run names, and the harness of .env.paper."""

import sys
from pathlib import Path

import pytest

pd = pytest.importorskip("pandas")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import runs  # noqa: E402


def test_a_smoke_run_has_its_own_name():
    assert runs.run_name("02-structural") == "02-structural"
    assert runs.run_name("02-structural", 5) == "02-structural-smoke-5"


def test_a_run_resumes_and_writes_the_marker_only_when_complete(tmp_path):
    run = runs.Run("demo", total=3, folder=tmp_path)
    run.add({"item_id": "a", "value": 1})
    run.add({"item_id": "b", "value": 2})
    assert run.finish(["a", "b", "c"]) is False
    assert not (tmp_path / "demo.done").exists()
    with pytest.raises(FileNotFoundError, match="not complete"):
        runs.read_result("demo", folder=tmp_path)

    again = runs.Run("demo", total=3, folder=tmp_path)
    assert again.done("a") and again.done("b") and not again.done("c")
    again.add({"item_id": "c", "value": 3})
    assert again.finish(["a", "b", "c"]) is True
    table = runs.read_result("demo", folder=tmp_path)
    assert list(table["item_id"]) == ["a", "b", "c"]
    assert list(table["value"]) == [1, 2, 3]


def test_a_marker_that_does_not_match_the_file_is_refused(tmp_path):
    run = runs.Run("demo", total=1, folder=tmp_path)
    run.add({"item_id": "a", "value": 1})
    run.finish(["a"])
    (tmp_path / "demo.done").write_text('{"items": 2}\n')
    with pytest.raises(ValueError, match="marker says 2"):
        runs.read_result("demo", folder=tmp_path)


def test_the_paper_harness_loads_the_tools_and_intents_of_env_paper():
    harness = runs.paper_harness(fixed_intent="structural")
    assert set(harness.registry.intents) == {"quantity", "structural"}
    assert "select_counter" in harness.registry.tools
    assert "illusion_pixel_rules" in harness.registry.tools


def test_the_fixed_classifier_chooses_its_intent():
    harness = runs.paper_harness(fixed_intent="quantity")
    choice = harness.registry.classifier.classify("any question", harness.registry.intent_infos())
    assert choice.key == "quantity"
    assert choice.probabilities["structural"] == 0.0
