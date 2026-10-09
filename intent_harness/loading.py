"""Load parts from module paths and from a .env file.

A plugin module exposes one function, `register(harness, **options)`, that adds its parts to
the harness.
"""

from importlib import import_module
from pathlib import Path
from typing import Any

from dotenv import dotenv_values

ENV_TOOLS = "INTENT_HARNESS_TOOLS"
ENV_INTENTS = "INTENT_HARNESS_INTENTS"
ENV_CLASSIFIER = "INTENT_HARNESS_CLASSIFIER"
ENV_CLASSIFIER_MODEL = "INTENT_HARNESS_CLASSIFIER_MODEL"


class LoadError(ImportError):
    """A plugin module cannot be loaded."""


def parse_list(text: str | None) -> list[str]:
    """Split a comma-separated list. Empty items are skipped."""
    if not text:
        return []
    return [item.strip() for item in text.split(",") if item.strip()]


def load_module(harness: Any, path: str, **options: Any) -> None:
    """Import the module at `path` and call its `register(harness, **options)`."""
    try:
        module = import_module(path)
    except ImportError as error:
        raise LoadError(f"Cannot import plugin module '{path}': {error}") from error
    register = getattr(module, "register", None)
    if not callable(register):
        raise LoadError(f"Plugin module '{path}' has no function 'register(harness, **options)'.")
    register(harness, **options)


def read_env(path: str | Path) -> dict[str, str | None]:
    """Read a .env file without changing the process environment."""
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(f"No .env file at '{path}'.")
    return dict(dotenv_values(path))
