"""A language model from the local cache that scores option texts.

`option_log_probabilities(prompt, options)` gives, for each option text, the log-probability
that the model writes exactly that text at the start of its reply: the sum over the option's
tokens, with teacher forcing. Nothing is generated. torch and transformers are imported only
when a model is loaded (install the `models` extra).

Two kinds of model load:

- "lm": a text-only causal language model (AutoModelForCausalLM and its tokenizer).
- "vlm": a vision-language model (AutoModelForImageTextToText and its processor), used on text
  only: the prompt is one user message with one text part, and no image is given.

With kind="auto" the kind comes from the model's config: a config with a vision part is "vlm".
"""

import gc
from collections.abc import Sequence


KINDS = ("lm", "vlm")


def detect_kind(config) -> str:
    """"vlm" when the model config has a vision part, else "lm"."""
    if getattr(config, "vision_config", None) is not None:
        return "vlm"
    return "lm"


class LanguageModel:
    """A language model, loaded from local files only (no download), used on text only."""

    def __init__(self, model: str, device: str = "mps", dtype: str = "bfloat16",
                 kind: str = "auto") -> None:
        import torch
        from transformers import AutoConfig

        self.torch = torch
        self.name = model
        self.device = torch.device(device)
        if kind == "auto":
            kind = detect_kind(AutoConfig.from_pretrained(model, local_files_only=True))
        if kind not in KINDS:
            raise ValueError(f"kind must be 'auto' or one of {KINDS}, not '{kind}'.")
        self.kind = kind

        if kind == "lm":
            from transformers import AutoModelForCausalLM, AutoTokenizer

            self.processor = None
            self.tokenizer = AutoTokenizer.from_pretrained(model, local_files_only=True)
            self.model = AutoModelForCausalLM.from_pretrained(
                model, dtype=getattr(torch, dtype), local_files_only=True
            )
        else:
            from transformers import AutoModelForImageTextToText, AutoProcessor

            self.processor = AutoProcessor.from_pretrained(model, local_files_only=True)
            self.tokenizer = self.processor.tokenizer
            self.model = AutoModelForImageTextToText.from_pretrained(
                model, dtype=getattr(torch, dtype), local_files_only=True
            )
        self.model = self.model.to(self.device)
        self.model.eval()
        if self.tokenizer.pad_token_id is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

    def _prompt_ids(self, prompt: str):
        """The prompt as one user message through the chat template. A text-only model gets
        thinking turned off; a vision-language model gets one text part and no image."""
        if self.kind == "lm":
            messages = [{"role": "user", "content": prompt}]
            text = self.tokenizer.apply_chat_template(
                messages, add_generation_prompt=True, tokenize=False, enable_thinking=False
            )
            encoded = self.tokenizer(text, return_tensors="pt", add_special_tokens=False)
        else:
            messages = [{"role": "user", "content": [{"type": "text", "text": prompt}]}]
            text = self.processor.apply_chat_template(
                messages, add_generation_prompt=True, tokenize=False
            )
            encoded = self.processor(text=text, return_tensors="pt")
        return encoded["input_ids"][0]                                   # shape: (prompt_len,)

    def option_log_probabilities(self, prompt: str, options: Sequence[str]) -> dict[str, float]:
        """{option: log-probability of the option as the reply's first tokens}, from one
        batched forward pass."""
        prompt_ids = self._prompt_ids(prompt)
        prompt_len = int(prompt_ids.shape[0])

        option_ids = {}
        longest = 0
        for option in options:
            ids = self.tokenizer.encode(option, add_special_tokens=False)
            option_ids[option] = ids
            longest = max(longest, len(ids))

        pad_id = self.tokenizer.pad_token_id
        batch_input = []
        batch_mask = []
        for option in options:
            ids = option_ids[option]
            row = list(prompt_ids.tolist()) + ids + [pad_id] * (longest - len(ids))
            mask = [1] * (prompt_len + len(ids)) + [0] * (longest - len(ids))
            batch_input.append(row)
            batch_mask.append(mask)
        input_ids = self.torch.tensor(batch_input, device=self.device)        # (n_options, L)
        attention_mask = self.torch.tensor(batch_mask, device=self.device)   # (n_options, L)

        with self.torch.no_grad():
            logits = self.model(input_ids=input_ids, attention_mask=attention_mask).logits
        # Only the positions that predict the option tokens: the last prompt position and the
        # option positions. The full sequence in float32 does not fit next to a 7B model on 32 GB.
        start = prompt_len - 1
        log_probs = self.torch.log_softmax(logits[:, start:, :].float(), dim=-1)   # (n_options, longest + 1, vocab)

        result = {}
        for row_index, option in enumerate(options):
            total = 0.0
            for step, token_id in enumerate(option_ids[option]):
                position = step                           # the logits that predict this token, from `start`
                total += float(log_probs[row_index, position, token_id])
            result[option] = total
        return result

    def unload(self) -> None:
        """Free the model's memory."""
        del self.model
        self.model = None
        gc.collect()
        if self.device.type == "mps":
            self.torch.mps.empty_cache()
