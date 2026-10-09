"""A causal language model from the local cache that scores option texts.

`option_log_probabilities(prompt, options)` gives, for each option text, the log-probability
that the model writes exactly that text at the start of its reply: the sum over the option's
tokens, with teacher forcing. Nothing is generated. torch and transformers are imported only
when a model is loaded (install the `models` extra).
"""

import gc
from collections.abc import Sequence


class LanguageModel:
    """A text-only causal language model, loaded from local files only (no download)."""

    def __init__(self, model: str, device: str = "mps", dtype: str = "bfloat16") -> None:
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer

        self.torch = torch
        self.name = model
        self.device = torch.device(device)
        self.tokenizer = AutoTokenizer.from_pretrained(model, local_files_only=True)
        self.model = AutoModelForCausalLM.from_pretrained(
            model, dtype=getattr(torch, dtype), local_files_only=True
        )
        self.model = self.model.to(self.device)
        self.model.eval()
        if self.tokenizer.pad_token_id is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

    def _prompt_ids(self, prompt: str):
        """The prompt as one user message through the chat template, thinking turned off."""
        messages = [{"role": "user", "content": prompt}]
        text = self.tokenizer.apply_chat_template(
            messages, add_generation_prompt=True, tokenize=False, enable_thinking=False
        )
        encoded = self.tokenizer(text, return_tensors="pt", add_special_tokens=False)
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
        log_probs = self.torch.log_softmax(logits.float(), dim=-1)           # (n_options, L, vocab)

        result = {}
        for row_index, option in enumerate(options):
            total = 0.0
            for step, token_id in enumerate(option_ids[option]):
                position = prompt_len + step - 1          # the logits that predict this token
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
