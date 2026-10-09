# intent-harness

## Set up

Python 3.12 and [uv](https://docs.astral.sh/uv/) are required.

```bash
uv venv --python 3.12 .venv
uv pip install --python .venv/bin/python -r requirements.txt
.venv/bin/python -m pytest
```

Every package the code uses is pinned in `requirements.txt`. Add a package there in the same
change that starts to use it.

## Use

The core holds no tools, intents or classifier. Load them at runtime, in code or from a
`.env` file. A plugin module has one function, `register(harness, **options)`, that adds its
parts.

```python
from intent_harness import Harness

harness = Harness()
harness.load_tools("my_package.tools")
harness.load_intents("my_package.intents")
harness.load_classifier("my_package.classifier", model="qwen3-4b")

answer = harness.answer(image, "How many legs does this animal have?")
answer.intent      # the intent that the classifier chose
answer.pipeline    # the pipeline that ran inside that intent
answer.value       # the result, for example a count or "Yes"
answer.trace       # one step for each tool call: tool, inputs, output
answer.confidence  # the classifier's confidence in the intent
```

The same set of parts can be listed in a `.env` file:

```
INTENT_HARNESS_TOOLS=my_package.tools
INTENT_HARNESS_INTENTS=my_package.intents
INTENT_HARNESS_CLASSIFIER=my_package.classifier
INTENT_HARNESS_CLASSIFIER_MODEL=qwen3-4b
```

```python
harness = Harness.from_env(".env")
```

Tools load first, then intents, then the classifier. An intent names the tools it needs; if
one is not loaded, loading the intent fails.
