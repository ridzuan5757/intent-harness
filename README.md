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
