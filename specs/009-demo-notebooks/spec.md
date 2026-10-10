# Feature Specification: Demo Notebooks

**Feature Branch**: `009-demo-notebooks`
**Created**: 2026-10-10
**Status**: Done

## Summary

Five demo notebooks come before the result notebooks. They show how the harness is mounted
(tools, intents, classifier with a language model), what input goes in, what the intent
classifier gives back, which tools each intent calls, and the answer. The result notebooks of
feature 007 follow, renumbered 06 to 10.

## User Scenarios & Testing

### User Story 1 - See the harness mounted and one question answered (Priority: P1)

A reader opens notebook 01 and sees an empty harness filled with tools, then intents, then the
option-scoring classifier, in code and from `.env.demo`. Then one counting question and one
illusion question go through `Harness.answer`, with the classifier's choice, the trace and the
answer.

### User Story 2 - See the classifier and each intent on a few images (Priority: P1)

Notebook 02 shows the classifier's prompt and its choice with two and with ten intents.
Notebooks 03 to 05 show the structural intent, the legs counter and the twelve counting
sub-topics on a few images each, with the trace of one image.

## Requirements

- **FR-001**: The demos run on a laptop (32 GB) on a few images each, with the harness of
  `.env.demo`: the parts of `.env.paper`, classifier model `Qwen/Qwen2.5-7B-Instruct`.
- **FR-002**: Every answer in a demo goes through `Harness.answer` with the real classifier.
- **FR-003**: Each demo notebook has an opening cell (Question, Why, Approach, Prediction), then
  the demo sections, then "Reading the result" and "Conclusion".
- **FR-004**: The result notebooks are renamed `06-results-*` to `10-results-*`; their content
  stays the same apart from the numbers they use to refer to each other.
- **FR-005**: Each notebook is at or below 600 KB.

## Assumptions

- `Qwen/Qwen2.5-7B-Instruct` scored 0.747 on the ten-intent sweep (notebook 06). The best model,
  `qwen2.5-14b` (0.781, 29.5 GB), does not fit next to SAM 3 on 32 GB.
- `matplotlib` is added to the `notebooks` extra for the images in the demos.
