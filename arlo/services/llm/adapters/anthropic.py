# services/llm/adapters/anthropic.py
import json
from typing import Optional, Dict, Any, List
from arlo.services.llm.base import LLMProvider, LLMResponse

class AnthropicAdapter(LLMProvider):
    """Covers: claude-sonnet-4-5, claude-haiku-4-5, claude-opus-4, etc."""

    def __init__(self, api_key: str, model: str = "claude-sonnet-4-5"):
        try:
            import anthropic
            self.client = anthropic.Anthropic(api_key=api_key)
            self.model_name = model
        except ImportError:
            self.client = None
            self.model_name = model

    async def chat(self, system: str, user: str, max_tokens: int = 1024) -> LLMResponse:
        if not self.client:
            raise RuntimeError("AnthropicAdapter requires anthropic package.")
        msg = self.client.messages.create(
            model=self.model_name, max_tokens=max_tokens,
            system=system,
            messages=[{"role": "user", "content": user}]
        )
        text = msg.content[0].text
        return LLMResponse(text=text, parsed=None, provider="anthropic",
                           model=self.model_name,
                           input_tokens=msg.usage.input_tokens,
                           output_tokens=msg.usage.output_tokens)

    async def chat_json(self, system: str, user: str, schema: Optional[Dict[str, Any]] = None) -> LLMResponse:
        resp = await self.chat(
            system + "\nReturn ONLY valid JSON. No prose, no markdown fences.", user
        )
        try:
            parsed = json.loads(resp.text)
            return LLMResponse(**{**vars(resp), "parsed": parsed})
        except json.JSONDecodeError:
            resp2 = await self.chat(
                system + "\nReturn ONLY valid JSON. Previous response was invalid.", user
            )
            try:
                parsed = json.loads(resp2.text)
            except json.JSONDecodeError:
                parsed = None
            return LLMResponse(**{**vars(resp2), "parsed": parsed})

    async def chat_tools(self, system: str, user: str, tools: List[Dict[str, Any]]) -> LLMResponse:
        if not self.client:
            raise RuntimeError("AnthropicAdapter requires anthropic package.")
        msg = self.client.messages.create(
            model=self.model_name, max_tokens=1024,
            system=system, tools=tools,
            messages=[{"role": "user", "content": user}]
        )
        tool_use = next((b for b in msg.content if b.type == "tool_use"), None)
        if tool_use:
            parsed = {"name": tool_use.name, "arguments": tool_use.input}
        else:
            parsed = {"raw": msg.content[0].text}
        return LLMResponse(text=str(parsed), parsed=parsed, provider="anthropic",
                           model=self.model_name,
                           input_tokens=msg.usage.input_tokens,
                           output_tokens=msg.usage.output_tokens)
