"""Shared helpers for the paper runs: paths, a resumable writer and the result reader.

A run writes one JSON line per item to `<name>.jsonl` while it goes. A second start skips the
items already in that file. When every item is done, the run writes `<name>.parquet` and the
marker `<name>.done` (the item count and the end time). A notebook reads a result only when its
marker exists and its item count matches.

A smoke run (`--limit N`) writes `<name>-smoke-N.*`, never the full-run files.

Paths come from the environment (or a git-ignored `.env` at the repository root):

- INTENT_HARNESS_DATA_DIR      the VLMBias data folder (holds benchmark-main/, benchmark-original/,
                               train-animals/ and their .parquet tables)
- INTENT_HARNESS_RESULTS_DIR   where result files go (default: results/ in the repository)
- INTENT_HARNESS_RECORDED_DIR  optional: the experiment's result files, for the comparison
"""

import json
import os
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_LISTS = ROOT / "data"

ENV_DATA = "INTENT_HARNESS_DATA_DIR"
ENV_RESULTS = "INTENT_HARNESS_RESULTS_DIR"
ENV_RECORDED = "INTENT_HARNESS_RECORDED_DIR"


def _load_dotenv():
    """Read the repository's .env file into the environment, if it exists. Values already set
    in the environment win."""
    path = ROOT / ".env"
    if path.is_file():
        from dotenv import load_dotenv

        load_dotenv(path, override=False)


_load_dotenv()


def data_dir() -> Path:
    value = os.environ.get(ENV_DATA)
    if not value:
        raise RuntimeError(f"Set {ENV_DATA} to the VLMBias data folder.")
    return Path(value)


def results_dir() -> Path:
    value = os.environ.get(ENV_RESULTS)
    path = Path(value) if value else ROOT / "results"
    path.mkdir(parents=True, exist_ok=True)
    return path


def recorded_dir() -> Path | None:
    value = os.environ.get(ENV_RECORDED)
    return Path(value) if value else None


def run_name(name: str, limit: int = 0) -> str:
    """The file stem of a run. A smoke run gets its own stem."""
    if limit:
        return f"{name}-smoke-{limit}"
    return name


class Run:
    """A resumable run over items with unique ids."""

    def __init__(self, name: str, total: int, folder: Path | None = None) -> None:
        self.folder = folder or results_dir()
        self.name = name
        self.total = total
        self.progress = self.folder / f"{name}.jsonl"
        self.result = self.folder / f"{name}.parquet"
        self.marker = self.folder / f"{name}.done"
        self.rows: dict[str, dict] = {}
        if self.progress.exists():
            with open(self.progress) as handle:
                for line in handle:
                    line = line.strip()
                    if line:
                        row = json.loads(line)
                        self.rows[row["item_id"]] = row
        self._handle = None
        self._started = time.time()
        self._added = 0

    def done(self, item_id: str) -> bool:
        return item_id in self.rows

    def add(self, row: dict) -> None:
        if self._handle is None:
            self._handle = open(self.progress, "a")
        self._handle.write(json.dumps(row) + "\n")
        self._handle.flush()
        self.rows[row["item_id"]] = row
        self._added += 1
        if self._added % 100 == 0:
            rate = (time.time() - self._started) / self._added
            left = self.total - len(self.rows)
            print(f"{self.name}: {len(self.rows)} of {self.total} | {rate:.2f} s per item | "
                  f"about {rate * left / 60:.0f} min left", flush=True)

    def finish(self, order: list[str]) -> bool:
        """Write the result file and the marker when every item is done. Returns True then."""
        if self._handle is not None:
            self._handle.close()
            self._handle = None
        missing = [item_id for item_id in order if item_id not in self.rows]
        if missing:
            print(f"{self.name}: {len(missing)} items not done; no result file written.", flush=True)
            return False
        import pandas as pd

        rows = [self.rows[item_id] for item_id in order]
        pd.DataFrame(rows).to_parquet(self.result, index=False)
        self.marker.write_text(json.dumps({"items": len(rows), "finished": time.strftime(
            "%Y-%m-%dT%H:%M:%SZ", time.gmtime())}) + "\n")
        print(f"{self.name}: done | {len(rows)} items | {self.result.name}", flush=True)
        return True


def read_result(name: str, folder: Path | None = None):
    """The result of a complete run as a DataFrame. Refuses a run without its marker, or a
    marker whose item count does not match the file."""
    import pandas as pd

    folder = folder or results_dir()
    marker = folder / f"{name}.done"
    result = folder / f"{name}.parquet"
    if not marker.exists() or not result.exists():
        raise FileNotFoundError(f"The run '{name}' is not complete (no {marker.name}).")
    table = pd.read_parquet(result)
    expected = json.loads(marker.read_text())["items"]
    if len(table) != expected:
        raise ValueError(f"The run '{name}' has {len(table)} rows; its marker says {expected}.")
    return table


def load_items(name: str):
    """An item list from data/ as a DataFrame."""
    import pandas as pd

    return pd.read_parquet(DATA_LISTS / f"{name}.parquet")


ENV_PAPER = ROOT / ".env.paper"


class FixedClassifier:
    """Chooses one intent for every question. The set runs use it, so that a table measures the
    intent's pipelines only; notebook 05 uses the real classifier."""

    def __init__(self, key: str) -> None:
        self.key = key

    def classify(self, question, intents):
        from intent_harness.types import Choice

        probabilities = {}
        for info in intents:
            probabilities[info.key] = 1.0 if info.key == self.key else 0.0
        return Choice(key=self.key, probabilities=probabilities, confidence=1.0)


def paper_harness(fixed_intent: str | None = None):
    """The harness that .env.paper describes. With `fixed_intent`, the tools and intents of
    .env.paper are loaded and a fixed classifier takes the place of the classifier."""
    from intent_harness import Harness
    from intent_harness import loading

    if fixed_intent is None:
        return Harness.from_env(ENV_PAPER)
    values = loading.read_env(ENV_PAPER)
    harness = Harness()
    harness.load_tools(*loading.parse_list(values.get(loading.ENV_TOOLS)))
    harness.load_intents(*loading.parse_list(values.get(loading.ENV_INTENTS)))
    harness.register_classifier(FixedClassifier(fixed_intent))
    return harness


def step_value(answer, tool: str, field: str):
    """An input of the first trace step of `tool`, or None."""
    for step in answer.trace:
        if step.tool == tool:
            return step.inputs.get(field)
    return None
