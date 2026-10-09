import pytest

from intent_harness import FunctionTool, as_tool
from intent_harness.tool_wrapper import end_trace, start_trace

from tests.fakes import add, fail


def test_tool_outside_answer_records_nothing():
    tool = as_tool("add", add)
    assert tool(2, 3) == 5


def test_trace_records_calls_in_order_with_named_inputs():
    tool = as_tool("add", add)
    token = start_trace()
    tool(1, 2)
    tool(a=10, b=20)
    trace = end_trace(token)
    assert [step.output for step in trace] == [3, 30]
    assert trace[0].inputs == {"a": 1, "b": 2}
    assert trace[1].inputs == {"a": 10, "b": 20}
    assert all(step.tool == "add" for step in trace)


def test_failing_tool_records_step_and_raises():
    tool = as_tool("fail", fail)
    token = start_trace()
    with pytest.raises(ValueError):
        tool(7)
    trace = end_trace(token)
    assert len(trace) == 1
    assert trace[0].ok is False
    assert "cannot use 7" in trace[0].error


def test_tool_needs_name_and_callable():
    with pytest.raises(ValueError):
        FunctionTool("", add)
    with pytest.raises(TypeError):
        FunctionTool("x", 5)


def test_builtin_without_signature_still_records():
    tool = as_tool("maximum", max)
    token = start_trace()
    assert tool(1, 4) == 4
    trace = end_trace(token)
    assert trace[0].output == 4
