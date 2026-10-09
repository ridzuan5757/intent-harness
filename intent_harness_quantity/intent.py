"""The quantity intent. It holds counting pipelines by name and runs one of them."""

from intent_harness.types import Result

NO_COUNTER = "none"

DESCRIPTION = (
    "The question asks how many of something the image shows: a number of legs, pieces, "
    "squares, stars, stripes or other countable parts."
)


class QuantityIntent:
    """Questions that ask for a count.

    `pipelines` is a list of counting pipelines. Each has `name`, `required_tools` and
    `count(image, question, tools)`. The selector chooses the pipeline to run. It is either:

    - the name of a registered tool, called as `tool(image, question)`, so the choice is a trace
      step; or
    - a function `selector(image, question, names)`.

    A selector that returns None means no counter fits the question: the answer has the pipeline
    "none" and the value None. With one pipeline the selector is not needed.
    """

    key = "quantity"
    description = DESCRIPTION

    def __init__(self, pipelines, selector=None):
        if not pipelines:
            raise ValueError("The quantity intent needs at least one counting pipeline.")
        self.pipelines = {}
        for pipeline in pipelines:
            if pipeline.name in self.pipelines:
                raise ValueError(f"Two counting pipelines are named '{pipeline.name}'.")
            self.pipelines[pipeline.name] = pipeline
        self.selector = selector

    @property
    def required_tools(self):
        """The selector tool (when it is a name) and the tools of all pipelines, each name once."""
        names = []
        if isinstance(self.selector, str):
            names.append(self.selector)
        for pipeline in self.pipelines.values():
            for name in pipeline.required_tools:
                if name not in names:
                    names.append(name)
        return tuple(names)

    def choose(self, image, question, tools=None):
        """The name of the pipeline to run, or None when the selector finds no counter."""
        names = list(self.pipelines)
        if self.selector is None:
            if len(names) == 1:
                return names[0]
            raise RuntimeError(
                f"The quantity intent has {len(names)} pipelines ({names}) and no selector."
            )
        if isinstance(self.selector, str):
            if tools is None:
                raise RuntimeError(f"The selector tool '{self.selector}' needs the tools mapping.")
            name = tools[self.selector](image, question)
        else:
            name = self.selector(image, question, names)
        if name is None:
            return None
        if name not in self.pipelines:
            raise RuntimeError(f"The selector chose '{name}', which is not one of {names}.")
        return name

    def run(self, image, question, tools):
        name = self.choose(image, question, tools)
        if name is None:
            return Result(value=None, pipeline=NO_COUNTER)
        count = self.pipelines[name].count(image, question, tools)
        return Result(value=count, pipeline=name)
