# Implementation Plan: Option-Scoring Intent Classifier

**Branch**: `003-intent-classifier` | **Date**: 2026-10-09 | **Spec**: [spec.md](spec.md)

## Summary

Move the option-scoring classifier and the language-model scoring code from the experiment
workspace (`harness/classifiers.py`, `harness/adapter.py`) into a new package,
`intent_harness_classifiers`. The classifier takes its options from the intents the core
passes to `classify`, so it holds no label list. A plugin module, `option_scoring`, registers
it through `register(harness, model=..., **options)`.

## Technical Context

**Language/Version**: Python 3.12
**Primary Dependencies**: the core (`intent_harness`); torch and transformers from the
`models` extra, imported only when a real model loads
**Testing**: pytest with a fake language model on the laptop; a check script on the M3 for the
recorded number
**Target Platform**: macOS (MPS) for real models; any platform for the tests
**Constraints**: no download (`local_files_only=True`); no new package

## Constitution Check

| Principle | Check |
|---|---|
| I. Core knows nothing concrete | Pass: the new package imports only core types and contracts; the core is not changed. |
| II. Moved code keeps its numbers | Pass when SC-002 holds: same choice on 388 of 388 items, accuracy 0.714. |
| III. Public repository hygiene | Pass: grep before each commit; worktree and pull request. |
| IV. Environment | Pass: no new package; torch and transformers are already in the `models` extra. |
| V. Scope and simplicity | Pass: only option scoring moves; keyword, strict and image classifiers stay behind. |
| VI. Plain writing | Pass: ASD-STE100 docstrings. |

## Project Structure

```
intent_harness_classifiers/
  __init__.py            # exports OptionScoringClassifier, build_prompt, softmax, confidence
  scoring.py             # build_prompt, softmax, confidence_from_probabilities (pure functions)
  language_model.py      # LanguageModel: local causal LM, chat template, option_log_probabilities
  option_scoring.py      # OptionScoringClassifier and the plugin's register(harness, ...)
tests/
  test_option_scoring.py # fake language model: prompt, probabilities, plugin loading, routing
specs/003-intent-classifier/checks/
  reproduce_qwen3_4b.py  # M3 check against results/04-choice-qwen3-4b-full.parquet
```

## Design notes

- The source classifier kept a `Choice` question object with a fixed criteria dictionary. The
  SDK builds the same `criteria` from the `IntentInfo` list at each call, in the given order.
- Prompt text, softmax and confidence are copied unchanged, so the log scores and the choices
  must match the recorded file.
- `LanguageModel.option_log_probabilities` is copied from `ModelAdapter` (text-only path, one
  batched teacher-forced pass). The image path, `reply` and `candidate_probabilities` are not
  moved.
- `register` accepts `language_model=` (an object with `option_log_probabilities`) instead of
  `model=`, so tests and other back ends need no download.
