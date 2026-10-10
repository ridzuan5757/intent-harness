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

## Demo notebooks

`notebooks/01-demo-*.ipynb` to `05-demo-*.ipynb` show the harness at work on a few images each,
before the result notebooks:

| Notebook | What it shows |
|---|---|
| 01 mount the harness | loading tools, intents and the classifier; one counting and one illusion question from input to answer, with the trace |
| 02 intent classifier | the prompt the model reads; the choice, probabilities and confidence with two and with ten intents |
| 03 structural | one original and one edited image of each illusion; the trace of one image; the Ponzo miss |
| 04 quantity legs | three animal pairs with the animal box and the leg regions drawn |
| 05 quantity sub-topics | one image of each of the twelve counting sub-topics; the trace of one image |

They load the harness from `.env.demo`: the parts of `.env.paper`, with the classifier model
`Qwen/Qwen2.5-7B-Instruct` (the best model of the sweep that fits on a 32 GB laptop next to
SAM 3). They need `INTENT_HARNESS_DATA_DIR` (see below) and the three models in the local
HuggingFace cache: `Qwen/Qwen2.5-7B-Instruct`, `facebook/sam3` and
`IDEA-Research/grounding-dino-tiny`.

## Reproduce the paper

`.env.paper` lists what the paper loads: the measurement, counting, GroundingDINO and SAM 3
tools; the quantity and structural intents; and the option-scoring classifier with
`Qwen/Qwen3-4B`. The models load from the local HuggingFace cache only (no download).

1. Install the extras:

   ```bash
   uv pip install --python .venv/bin/python -e '.[models,notebooks,test]'
   ```

2. Set the data folder. Use the environment, or a `.env` file at the repository root (git
   ignores it):

   | Variable | Value |
   |---|---|
   | `INTENT_HARNESS_DATA_DIR` | the VLMBias data folder: it holds `benchmark-main/`, `benchmark-original/`, `train-animals/` and their `.parquet` tables |
   | `INTENT_HARNESS_RESULTS_DIR` | where the runs write (default: `results/`) |
   | `INTENT_HARNESS_RECORDED_DIR` | optional: earlier result files, for an item-by-item comparison in the notebooks |

3. Run the scripts. Each one continues after a stop, and writes its result file and a `.done`
   marker only when every item is done. `--limit N` makes a separate smoke run.

   | Script | Set | Result |
   |---|---|---|
   | `scripts/run_classifier.py --models all` | 388 intent prompts, 24 models | `results/01-classifier-<model>.parquet` |
   | `scripts/run_structural.py` | 396 illusion images | `results/02-structural.parquet` |
   | `scripts/run_legs.py` | 2,196 animal images (1,098 pairs) | `results/03-legs.parquet` |
   | `scripts/run_counting.py` | 795 counting items | `results/04-counting.parquet` |
   | `scripts/run_end_to_end.py` | 2,784 VLMBias prompts | `results/05-end-to-end.parquet` |

   Run them from the repository root with `PYTHONPATH=.`.

4. Open the result notebooks, `notebooks/06-results-*.ipynb` to `10-results-*.ipynb`. Each reads its
   result files only.

The item lists (prompts, image paths and gold answers) are in `data/`. The images are not in
this repository.
