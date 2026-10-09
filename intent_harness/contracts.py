"""The three contracts that loaded parts must follow.

The core checks parts against these contracts. It does not import any concrete part.
"""

from collections.abc import Mapping, Sequence
from typing import Any, Protocol, runtime_checkable

from intent_harness.types import Choice, IntentInfo, Result


@runtime_checkable
class Tool(Protocol):
    """A named callable that does one job."""

    name: str

    def __call__(self, *args: Any, **kwargs: Any) -> Any: ...


@runtime_checkable
class Intent(Protocol):
    """A pipeline for one kind of question.

    `required_tools` names the tools that `run` uses. `run` gets only those tools.
    """

    key: str
    description: str
    required_tools: Sequence[str]

    def run(self, image: Any, question: str, tools: Mapping[str, Tool]) -> Result: ...


@runtime_checkable
class IntentClassifier(Protocol):
    """Chooses one of the loaded intents for a question."""

    def classify(self, question: str, intents: Sequence[IntentInfo]) -> Choice: ...
