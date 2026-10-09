import pytest

from intent_harness import FunctionTool, RegistrationError
from intent_harness.registry import Registry

from tests.fakes import AddTwiceIntent, EchoIntent, FixedClassifier, add


class NoRun:
    key = "x"
    description = "d"
    required_tools = ()


class NoDescription:
    key = "x"
    required_tools = ()

    def run(self, image, question, tools):
        return None


@pytest.mark.parametrize("part, missing", [(NoRun(), "run"), (NoDescription(), "description")])
def test_intent_missing_attribute_is_named(part, missing):
    registry = Registry()
    with pytest.raises(RegistrationError, match=f"'{missing}'"):
        registry.add_intent(part)


def test_intent_with_missing_tool_fails_and_names_it():
    registry = Registry()
    with pytest.raises(RegistrationError, match="add"):
        registry.add_intent(AddTwiceIntent())


def test_required_tools_as_string_is_rejected():
    class StringTools(EchoIntent):
        required_tools = "add"

    registry = Registry()
    with pytest.raises(RegistrationError, match="list of names"):
        registry.add_intent(StringTools())


def test_duplicate_tool_and_intent_names_fail():
    registry = Registry()
    registry.add_tool(add, name="add")
    with pytest.raises(RegistrationError, match="already registered"):
        registry.add_tool(add, name="add")
    registry.add_intent(EchoIntent())
    with pytest.raises(RegistrationError, match="already registered"):
        registry.add_intent(EchoIntent())


def test_plain_function_is_wrapped_and_found_by_name():
    registry = Registry()
    tool = registry.add_tool(add, name="add")
    assert isinstance(tool, FunctionTool)
    assert registry.tool("add") is tool
    assert registry.tool("add")(2, 2) == 4


def test_plain_function_without_name_is_rejected():
    registry = Registry()
    with pytest.raises(RegistrationError, match="Not a tool"):
        registry.add_tool(add)


def test_tools_for_gives_only_declared_tools():
    registry = Registry()
    registry.add_tool(add, name="add")
    registry.add_tool(max, name="max")
    intent = registry.add_intent(AddTwiceIntent())
    assert sorted(registry.tools_for(intent)) == ["add"]


def test_classifier_checks():
    registry = Registry()
    with pytest.raises(RegistrationError, match="classify"):
        registry.set_classifier(object())
    registry.set_classifier(FixedClassifier("echo"))
    with pytest.raises(RegistrationError, match="already registered"):
        registry.set_classifier(FixedClassifier("echo"))


def test_intent_infos_keep_order():
    registry = Registry()
    registry.add_tool(add, name="add")
    registry.add_intent(EchoIntent())
    registry.add_intent(AddTwiceIntent())
    assert [info.key for info in registry.intent_infos()] == ["echo", "sum"]
