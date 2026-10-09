"""Small fake parts for the core tests. They stand in for real tools, intents and classifiers."""

from intent_harness.types import Choice, Result


def add(a, b):
    return a + b


def fail(x):
    raise ValueError(f"cannot use {x}")


class FixedClassifier:
    """Always chooses `key`, and records what it was given."""

    def __init__(self, key, confidence=0.9):
        self.key = key
        self.confidence = confidence
        self.seen = []

    def classify(self, question, intents):
        self.seen.append((question, list(intents)))
        probabilities = {info.key: 0.0 for info in intents}
        probabilities[self.key] = 1.0
        return Choice(key=self.key, probabilities=probabilities, confidence=self.confidence)


class AddTwiceIntent:
    """Calls the `add` tool twice and returns the sum."""

    key = "sum"
    description = "Questions that ask for a total."
    required_tools = ("add",)

    def run(self, image, question, tools):
        first = tools["add"](image, 1)
        second = tools["add"](first, 2)
        return Result(value=second, pipeline="add-twice")


class EchoIntent:
    """Returns the question. Reports no pipeline name."""

    key = "echo"
    description = "Questions that are repeated back."
    required_tools = ()

    def run(self, image, question, tools):
        return Result(value=question)


class FailingIntent:
    key = "broken"
    description = "Calls a tool that fails."
    required_tools = ("fail",)

    def run(self, image, question, tools):
        tools["fail"](image)
        return Result(value=None)


class PeekIntent:
    """Returns the names of the tools it was given."""

    key = "peek"
    description = "Shows its tools."
    required_tools = ("add",)

    def run(self, image, question, tools):
        return Result(value=sorted(tools))


class PlainValueIntent:
    key = "plain"
    description = "Returns a plain value, not a Result."
    required_tools = ()

    def run(self, image, question, tools):
        return 3
