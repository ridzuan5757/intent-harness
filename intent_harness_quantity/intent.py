"""The quantity intent. It holds counting pipelines by name and runs one of them."""

from intent_harness.types import Result

DESCRIPTION = (
    "The question asks how many of something the image shows: a number of legs, pieces, "
    "squares, stars, stripes or other countable parts."
)


class QuantityIntent:
    """Questions that ask for a count.

    `pipelines` is a list of counting pipelines. Each has `name`, `required_tools` and
    `count(image, question, tools)`. `selector(image, question, names)` returns the name of the
    pipeline to run. With one pipeline the selector is not needed.
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
        """The tools of all pipelines, each name once, in the order the pipelines give them."""
        names = []
        for pipeline in self.pipelines.values():
            for name in pipeline.required_tools:
                if name not in names:
                    names.append(name)
        return tuple(names)

    def choose(self, image, question):
        """The name of the pipeline to run."""
        names = list(self.pipelines)
        if self.selector is None:
            if len(names) == 1:
                return names[0]
            raise RuntimeError(
                f"The quantity intent has {len(names)} pipelines ({names}) and no selector."
            )
        name = self.selector(image, question, names)
        if name not in self.pipelines:
            raise RuntimeError(f"The selector chose '{name}', which is not one of {names}.")
        return name

    def run(self, image, question, tools):
        name = self.choose(image, question)
        count = self.pipelines[name].count(image, question, tools)
        return Result(value=count, pipeline=name)
