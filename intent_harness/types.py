"""Data types that the core passes between its parts."""

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class IntentInfo:
    """What a classifier reads about one loaded intent."""

    key: str
    description: str


@dataclass(frozen=True)
class Choice:
    """The result of an intent classifier.

    `probabilities` has one entry for each loaded intent key. `confidence` is from 0 to 1.
    """

    key: str
    probabilities: dict[str, float] = field(default_factory=dict)
    confidence: float = 1.0


@dataclass(frozen=True)
class Step:
    """One tool call in the trace of an answer."""

    tool: str
    inputs: dict[str, Any]
    output: Any = None
    ok: bool = True
    error: str | None = None


@dataclass(frozen=True)
class Result:
    """What an intent returns from `run`.

    `pipeline` names the sub-pipeline that ran. When it is None, the answer uses the intent key.
    """

    value: Any
    pipeline: str | None = None


@dataclass(frozen=True)
class Answer:
    """The result of `Harness.answer` for one question."""

    intent: str
    pipeline: str
    value: Any
    confidence: float
    probabilities: dict[str, float]
    trace: tuple[Step, ...]
