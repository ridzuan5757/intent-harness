"""Turn a plain function into a named tool that records trace steps.

Tools stay plain functions. The wrapper adds the name and records each call as a `Step`
while `Harness.answer` runs. Outside `answer`, a wrapped tool records nothing.
"""

from collections.abc import Callable
from contextvars import ContextVar
from typing import Any
import inspect

from intent_harness.types import Step

_current_trace: ContextVar[list[Step] | None] = ContextVar("intent_harness_trace", default=None)


def start_trace() -> object:
    """Start a new trace for the current context. Returns a token for `end_trace`."""
    return _current_trace.set([])


def end_trace(token: object) -> tuple[Step, ...]:
    """End the trace that `start_trace` started and return its steps."""
    steps = _current_trace.get() or []
    _current_trace.reset(token)
    return tuple(steps)


def _named_inputs(function: Callable[..., Any], args: tuple, kwargs: dict) -> dict[str, Any]:
    """The call inputs by parameter name, when the signature allows it."""
    try:
        bound = inspect.signature(function).bind(*args, **kwargs)
    except (TypeError, ValueError):
        named = {f"arg{index}": value for index, value in enumerate(args)}
        named.update(kwargs)
        return named
    return dict(bound.arguments)


class FunctionTool:
    """A plain function with a name. Each call records one step in the current trace."""

    def __init__(self, name: str, function: Callable[..., Any]):
        if not name:
            raise ValueError("A tool needs a name.")
        if not callable(function):
            raise TypeError(f"Tool '{name}': the function is not callable.")
        self.name = name
        self.function = function

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        steps = _current_trace.get()
        if steps is None:
            return self.function(*args, **kwargs)
        inputs = _named_inputs(self.function, args, kwargs)
        try:
            output = self.function(*args, **kwargs)
        except Exception as error:
            steps.append(Step(tool=self.name, inputs=inputs, ok=False, error=repr(error)))
            raise
        steps.append(Step(tool=self.name, inputs=inputs, output=output))
        return output

    def __repr__(self) -> str:
        return f"FunctionTool({self.name!r})"


def as_tool(name: str, function: Callable[..., Any]) -> FunctionTool:
    """Wrap `function` as a tool called `name`."""
    return FunctionTool(name, function)
