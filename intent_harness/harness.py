"""The harness: classify a question among the loaded intents, then run the chosen one."""

from pathlib import Path
from typing import Any, Callable

from intent_harness import loading
from intent_harness.contracts import Intent, IntentClassifier, Tool
from intent_harness.registry import Registry
from intent_harness.tool_wrapper import end_trace, start_trace
from intent_harness.types import Answer, Result


class Harness:
    """Holds the loaded parts and answers questions with them."""

    def __init__(self) -> None:
        self.registry = Registry()

    # ---- registration in code

    def register_tool(self, tool: Tool | Callable[..., Any], name: str | None = None) -> Tool:
        """Add a tool. For a plain function, give `name`."""
        return self.registry.add_tool(tool, name=name)

    def register_intent(self, intent: Intent) -> Intent:
        """Add an intent. Its tools must be registered first."""
        return self.registry.add_intent(intent)

    def register_classifier(self, classifier: IntentClassifier) -> IntentClassifier:
        """Set the intent classifier."""
        return self.registry.set_classifier(classifier)

    # ---- loading from module paths

    def load_tools(self, *paths: str) -> "Harness":
        for path in paths:
            loading.load_module(self, path)
        return self

    def load_intents(self, *paths: str) -> "Harness":
        for path in paths:
            loading.load_module(self, path)
        return self

    def load_classifier(self, path: str, **options: Any) -> "Harness":
        loading.load_module(self, path, **options)
        return self

    @classmethod
    def from_env(cls, path: str | Path = ".env") -> "Harness":
        """A harness loaded from a .env file: tools, then intents, then the classifier."""
        values = loading.read_env(path)
        harness = cls()
        harness.load_tools(*loading.parse_list(values.get(loading.ENV_TOOLS)))
        harness.load_intents(*loading.parse_list(values.get(loading.ENV_INTENTS)))
        classifier = values.get(loading.ENV_CLASSIFIER)
        if classifier:
            options = {}
            model = values.get(loading.ENV_CLASSIFIER_MODEL)
            if model:
                options["model"] = model
            harness.load_classifier(classifier.strip(), **options)
        return harness

    # ---- answering

    def answer(self, image: Any, question: str) -> Answer:
        """Classify `question`, run the chosen intent on `image`, and return the answer."""
        classifier = self.registry.classifier
        if classifier is None:
            raise RuntimeError("No intent classifier is loaded.")
        if not self.registry.intents:
            raise RuntimeError("No intent is loaded.")

        choice = classifier.classify(question, self.registry.intent_infos())
        if choice.key not in self.registry.intents:
            raise RuntimeError(
                f"The classifier chose '{choice.key}', which is not a loaded intent. "
                f"Loaded: {sorted(self.registry.intents)}"
            )
        intent = self.registry.intent(choice.key)

        token = start_trace()
        try:
            result = intent.run(image, question, self.registry.tools_for(intent))
        finally:
            trace = end_trace(token)
        if not isinstance(result, Result):
            raise TypeError(f"Intent '{intent.key}' returned {type(result).__name__}, not Result.")

        return Answer(
            intent=intent.key,
            pipeline=result.pipeline or intent.key,
            value=result.value,
            confidence=choice.confidence,
            probabilities=dict(choice.probabilities),
            trace=trace,
        )
