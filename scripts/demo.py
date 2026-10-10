"""Helpers for the demo notebooks (01 to 05): the demo harness, and a trace as a table."""

import numpy as np
import pandas as pd
from PIL import Image

import runs

ENV_DEMO = runs.ROOT / ".env.demo"
DEMO_MODEL = "Qwen/Qwen2.5-7B-Instruct"


def demo_harness():
    """The harness that .env.demo describes: tools, then intents, then the classifier."""
    from intent_harness import Harness

    return Harness.from_env(ENV_DEMO)


def short(value, width=60):
    """A short text for one trace input or output: arrays and images by their shape."""
    if isinstance(value, Image.Image):
        return f"image {value.size[0]}x{value.size[1]}"
    if isinstance(value, np.ndarray):
        return f"array {value.shape}"
    if isinstance(value, (list, tuple)) and len(value) > 4:
        return f"{type(value).__name__} of {len(value)}"
    if isinstance(value, float):
        return f"{value:.4f}"
    text = repr(value)
    if len(text) > width:
        text = text[: width - 3] + "..."
    return text


def trace_table(answer):
    """One row per tool call in the answer's trace."""
    rows = []
    for number, step in enumerate(answer.trace, start=1):
        inputs = []
        for name, value in step.inputs.items():
            inputs.append(f"{name}={short(value, 40)}")
        rows.append({
            "step": number,
            "tool": step.tool,
            "inputs": ", ".join(inputs),
            "output": short(step.output),
            "ok": step.ok,
        })
    return pd.DataFrame(rows)


def answer_summary(answer):
    """The classifier's choice and the intent's answer, as one row."""
    return {
        "intent": answer.intent,
        "confidence": round(answer.confidence, 3),
        "probabilities": {key: round(value, 3) for key, value in answer.probabilities.items()},
        "pipeline": answer.pipeline,
        "value": answer.value,
        "tool calls": len(answer.trace),
    }
