# services/llm/base.py
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Dict, Any, List

@dataclass
class LLMResponse:
    text: str
    parsed: Optional[Dict[str, Any]]
    provider: str
    model: str
    input_tokens: Optional[int]
    output_tokens: Optional[int]

class LLMProvider(ABC):
    @abstractmethod
    async def chat(self, system: str, user: str, max_tokens: int = 1024) -> LLMResponse: ...

    @abstractmethod
    async def chat_json(self, system: str, user: str, schema: Optional[Dict[str, Any]] = None) -> LLMResponse: ...

    @abstractmethod
    async def chat_tools(self, system: str, user: str, tools: List[Dict[str, Any]]) -> LLMResponse: ...
