# services/llm/adapters/openai_compat.py
import json
from typing import Optional, Dict, Any, List
from arlo.services.llm.base import LLMProvider, LLMResponse

class OpenAICompatAdapter(LLMProvider):
    """Covers: OpenAI, Groq, Together, Fireworks, local vLLM — any OpenAI-compatible API."""

    def __init__(self, api_key: str, model: str, base_url: Optional[str] = None):
        try:
            from openai import AsyncOpenAI
            self.client = AsyncOpenAI(api_key=api_key, base_url=base_url)
            self.model_name = model
        except ImportError:
            self.client = None
            self.model_name = model

    async def chat(self, system: str, user: str, max_tokens: int = 1024) -> LLMResponse:
        if not self.client:
            raise RuntimeError("OpenAICompatAdapter requires openai package.")
        resp = await self.client.chat.completions.create(
            model=self.model_name, max_tokens=max_tokens,
            messages=[{"role": "system", "content": system},
                      {"role": "user", "content": user}]
        )
        text = resp.choices[0].message.content
        return LLMResponse(text=text, parsed=None, provider="openai_compat",
                           model=self.model_name,
                           input_tokens=resp.usage.prompt_tokens if hasattr(resp.usage, 'prompt_tokens') else None,
                           output_tokens=resp.usage.completion_tokens if hasattr(resp.usage, 'completion_tokens') else None)

    async def chat_json(self, system: str, user: str, schema: Optional[Dict[str, Any]] = None) -> LLMResponse:
        if not self.client:
            raise RuntimeError("OpenAICompatAdapter requires openai package.")
        resp = await self.client.chat.completions.create(
            model=self.model_name,
            response_format={"type": "json_object"},
            messages=[{"role": "system", "content": system + "\nReturn ONLY valid JSON."},
                      {"role": "user", "content": user}]
        )
        text = resp.choices[0].message.content
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError:
            parsed = None
        return LLMResponse(text=text, parsed=parsed, provider="openai_compat",
                           model=self.model_name,
                           input_tokens=resp.usage.prompt_tokens if hasattr(resp.usage, 'prompt_tokens') else None,
                           output_tokens=resp.usage.completion_tokens if hasattr(resp.usage, 'completion_tokens') else None)

    async def chat_tools(self, system: str, user: str, tools: List[Dict[str, Any]]) -> LLMResponse:
        if not self.client:
            raise RuntimeError("OpenAICompatAdapter requires openai package.")
        resp = await self.client.chat.completions.create(
            model=self.model_name, tools=tools, tool_choice="auto",
            messages=[{"role": "system", "content": system},
                      {"role": "user", "content": user}]
        )
        call = resp.choices[0].message.tool_calls[0] if resp.choices[0].message.tool_calls else None
        if call:
            parsed = {"name": call.function.name, "arguments": json.loads(call.function.arguments)}
        else:
            parsed = {"raw": resp.choices[0].message.content}
        return LLMResponse(text=str(parsed), parsed=parsed, provider="openai_compat",
                           model=self.model_name,
                           input_tokens=resp.usage.prompt_tokens if hasattr(resp.usage, 'prompt_tokens') else None,
                           output_tokens=resp.usage.completion_tokens if hasattr(resp.usage, 'completion_tokens') else None)
