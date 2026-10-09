import pytest

from intent_harness import Harness

from tests.fakes import (AddTwiceIntent, EchoIntent, FailingIntent, FixedClassifier, PeekIntent,
                         PlainValueIntent, add, fail)


def build(key, *intents):
    harness = Harness()
    harness.register_tool(add, name="add")
    harness.register_tool(fail, name="fail")
    harness.register_tool(max, name="max")
    for intent in intents:
        harness.register_intent(intent)
    harness.register_classifier(FixedClassifier(key, confidence=0.75))
    return harness


def test_classifier_choice_routes_to_second_intent():
    harness = build("sum", EchoIntent(), AddTwiceIntent())
    answer = harness.answer(10, "What is the total?")
    assert answer.intent == "sum"
    assert answer.pipeline == "add-twice"
    assert answer.value == 13
    assert answer.confidence == 0.75
    assert answer.probabilities == {"echo": 0.0, "sum": 1.0}


def test_classifier_receives_loaded_intents_only():
    harness = build("echo", EchoIntent(), AddTwiceIntent())
    harness.answer(None, "q")
    question, infos = harness.registry.classifier.seen[0]
    assert question == "q"
    assert [(info.key, info.description) for info in infos] == [
        ("echo", EchoIntent.description), ("sum", AddTwiceIntent.description)]


def test_trace_has_two_steps_in_call_order():
    harness = build("sum", AddTwiceIntent())
    trace = harness.answer(10, "q").trace
    assert [(step.tool, step.inputs, step.output) for step in trace] == [
        ("add", {"a": 10, "b": 1}, 11),
        ("add", {"a": 11, "b": 2}, 13),
    ]


def test_pipeline_defaults_to_intent_key():
    harness = build("echo", EchoIntent())
    answer = harness.answer(None, "hello")
    assert answer.pipeline == "echo"
    assert answer.value == "hello"
    assert answer.trace == ()


def test_intent_gets_only_declared_tools():
    harness = build("peek", PeekIntent())
    assert harness.answer(None, "q").value == ["add"]


def test_no_classifier_or_no_intent_raises():
    empty = Harness()
    empty.register_classifier(FixedClassifier("echo"))
    with pytest.raises(RuntimeError, match="No intent"):
        empty.answer(None, "q")
    no_classifier = Harness()
    no_classifier.register_intent(EchoIntent())
    with pytest.raises(RuntimeError, match="No intent classifier"):
        no_classifier.answer(None, "q")


def test_unknown_key_from_classifier_raises():
    harness = build("missing", EchoIntent())
    with pytest.raises(RuntimeError, match="not a loaded intent"):
        harness.answer(None, "q")


def test_tool_error_is_raised_to_the_caller():
    harness = build("broken", FailingIntent())
    with pytest.raises(ValueError, match="cannot use 5"):
        harness.answer(5, "q")


def test_intent_must_return_result():
    harness = build("plain", PlainValueIntent())
    with pytest.raises(TypeError, match="not Result"):
        harness.answer(None, "q")


def test_trace_is_separate_per_answer():
    harness = build("sum", AddTwiceIntent())
    first = harness.answer(1, "q")
    second = harness.answer(2, "q")
    assert len(first.trace) == 2 and len(second.trace) == 2
    assert second.trace[0].inputs["a"] == 2
