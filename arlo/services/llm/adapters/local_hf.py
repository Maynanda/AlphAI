# services/llm/adapters/local_hf.py
import json
import re
from typing import Optional, Dict, Any, List
from arlo.services.llm.base import LLMProvider, LLMResponse

class LocalHFAdapter(LLMProvider):
    """Covers: Qwen3, Qwen2.5, Mistral, Llama 3, Phi-3, and any HF-compatible model."""

    def __init__(self, model_path: str, device_map: str = "auto"):
        self.model_name = model_path
        # We wrap in try-except because transformers might fail to import if not installed
        try:
            import torch
            from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
            self.tokenizer = AutoTokenizer.from_pretrained(model_path)
            self.model = AutoModelForCausalLM.from_pretrained(
                model_path, torch_dtype=torch.float16, device_map=device_map
            )
            self.pipe = pipeline("text-generation", model=self.model, tokenizer=self.tokenizer)
        except ImportError:
            self.tokenizer = None
            self.model = None
            self.pipe = None

    async def chat(self, system: str, user: str, max_tokens: int = 1024) -> LLMResponse:
        if not self.pipe:
            raise RuntimeError("LocalHFAdapter requires transformers and torch to be installed.")
        messages = [{"role": "system", "content": system}, {"role": "user", "content": user}]
        prompt = self.tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
        out = self.pipe(prompt, max_new_tokens=max_tokens, do_sample=False)
        text = out[0]["generated_text"][len(prompt):]
        return LLMResponse(text=text.strip(), parsed=None,
                           provider="local_hf", model=self.model_name,
                           input_tokens=None, output_tokens=None)

    async def chat_json(self, system: str, user: str, schema: Optional[Dict[str, Any]] = None) -> LLMResponse:
        json_instruction = "\nReturn ONLY valid JSON. No prose, no markdown fences."
        resp = await self.chat(system + json_instruction, user)
        try:
            parsed = json.loads(resp.text)
            return LLMResponse(**{**vars(resp), "parsed": parsed})
        except json.JSONDecodeError:
            resp2 = await self.chat(
                system + json_instruction + "\nPrevious output was not valid JSON. Try again.", user
            )
            try:
                parsed = json.loads(resp2.text)
            except json.JSONDecodeError:
                parsed = None
            return LLMResponse(**{**vars(resp2), "parsed": parsed})

    async def chat_tools(self, system: str, user: str, tools: List[Dict[str, Any]]) -> LLMResponse:
        if not self.pipe:
            raise RuntimeError("LocalHFAdapter requires transformers and torch.")
        messages = [{"role": "system", "content": system}, {"role": "user", "content": user}]
        prompt = self.tokenizer.apply_chat_template(
            messages, tools=tools, tokenize=False, add_generation_prompt=True
        )
        out = self.pipe(prompt, max_new_tokens=512, do_sample=False)
        text = out[0]["generated_text"][len(prompt):]
        match = re.search(r'<tool_call>(.*?)</tool_call>', text, re.DOTALL)
        parsed = json.loads(match.group(1)) if match else {"raw": text}
        return LLMResponse(text=text, parsed=parsed,
                           provider="local_hf", model=self.model_name,
                           input_tokens=None, output_tokens=None)
