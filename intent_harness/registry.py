"""Holds the loaded tools, intents and classifier, and checks each one when it is added."""

from collections.abc import Callable, Mapping
from types import MappingProxyType
from typing import Any

from intent_harness.contracts import Intent, IntentClassifier, Tool
from intent_harness.tool_wrapper import FunctionTool
from intent_harness.types import IntentInfo


class RegistrationError(ValueError):
    """A part does not follow its contract, or a name is wrong."""


def _missing(part: Any, attributes: tuple[str, ...]) -> str | None:
    for attribute in attributes:
        if not hasattr(part, attribute):
            return attribute
    return None


class Registry:
    """The parts loaded into one harness."""

    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}
        self._intents: dict[str, Intent] = {}
        self._classifier: IntentClassifier | None = None

    # ---- tools

    def add_tool(self, tool: Tool | Callable[..., Any], name: str | None = None) -> Tool:
        """Add a tool. A plain function needs `name` and is wrapped as a `FunctionTool`."""
        if name is not None:
            tool = FunctionTool(name, tool)
        missing = _missing(tool, ("name",))
        if missing is not None or not callable(tool):
            raise RegistrationError(
                f"Not a tool: {tool!r}. Give a plain function with a name, "
                "or an object with 'name' that can be called."
            )
        if tool.name in self._tools:
            raise RegistrationError(f"A tool named '{tool.name}' is already registered.")
        self._tools[tool.name] = tool
        return tool

    def tool(self, name: str) -> Tool:
        if name not in self._tools:
            raise KeyError(f"No tool named '{name}'. Registered: {sorted(self._tools)}")
        return self._tools[name]

    @property
    def tools(self) -> Mapping[str, Tool]:
        return MappingProxyType(self._tools)

    def tools_for(self, intent: Intent) -> Mapping[str, Tool]:
        """A read-only mapping with only the tools that `intent` declared."""
        return MappingProxyType({name: self._tools[name] for name in intent.required_tools})

    # ---- intents

    def add_intent(self, intent: Intent) -> Intent:
        """Add an intent. All the tools it names must already be registered."""
        missing = _missing(intent, ("key", "description", "required_tools", "run"))
        if missing is not None:
            raise RegistrationError(f"Not an intent: {intent!r} has no '{missing}'.")
        if not callable(intent.run):
            raise RegistrationError(f"Intent '{intent.key}': 'run' cannot be called.")
        if isinstance(intent.required_tools, str):
            raise RegistrationError(
                f"Intent '{intent.key}': 'required_tools' must be a list of names, not a string."
            )
        if intent.key in self._intents:
            raise RegistrationError(f"An intent with key '{intent.key}' is already registered.")
        absent = [name for name in intent.required_tools if name not in self._tools]
        if absent:
            raise RegistrationError(
                f"Intent '{intent.key}' needs tools that are not registered: {absent}. "
                "Load the tools before the intents."
            )
        self._intents[intent.key] = intent
        return intent

    def intent(self, key: str) -> Intent:
        if key not in self._intents:
            raise KeyError(f"No intent with key '{key}'. Registered: {sorted(self._intents)}")
        return self._intents[key]

    @property
    def intents(self) -> Mapping[str, Intent]:
        return MappingProxyType(self._intents)

    def intent_infos(self) -> list[IntentInfo]:
        """Key and description of each loaded intent, in the order they were added."""
        return [IntentInfo(key=i.key, description=i.description) for i in self._intents.values()]

    # ---- classifier

    def set_classifier(self, classifier: IntentClassifier) -> IntentClassifier:
        """Set the intent classifier. A harness has one; setting it again is an error."""
        if not callable(getattr(classifier, "classify", None)):
            raise RegistrationError(f"Not an intent classifier: {classifier!r} has no 'classify'.")
        if self._classifier is not None:
            raise RegistrationError("An intent classifier is already registered.")
        self._classifier = classifier
        return classifier

    @property
    def classifier(self) -> IntentClassifier | None:
        return self._classifier
