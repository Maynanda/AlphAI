# services/llm/adapters/gemini.py
import google.generativeai as genai
import json
from arlo.services.llm.base import LLMProvider, LLMResponse

class GeminiAdapter(LLMProvider):
    """Covers: gemini-2.0-flash, gemini-1.5-pro, gemini-2.5-pro, etc."""

    def __init__(self, api_key: str, model: str = "gemini-3.1-flash"):
        genai.configure(api_key=api_key)
        self.model_name = model
        self.client = genai.GenerativeModel(model)

    async def chat(self, system: str, user: str, max_tokens: int = 1024) -> LLMResponse:
        response = self.client.generate_content(
            f"{system}\n\n{user}",
            generation_config=genai.GenerationConfig(max_output_tokens=max_tokens)
        )
        return LLMResponse(text=response.text, parsed=None, provider="gemini",
                           model=self.model_name,
                           input_tokens=response.usage_metadata.prompt_token_count if hasattr(response, 'usage_metadata') else None,
                           output_tokens=response.usage_metadata.candidates_token_count if hasattr(response, 'usage_metadata') else None)

    async def chat_json(self, system: str, user: str, schema: dict | None = None) -> LLMResponse:
        config = genai.GenerationConfig(
            response_mime_type="application/json",
            response_schema=schema  # Gemini native structured output
        )
        response = self.client.generate_content(f"{system}\n\n{user}", generation_config=config)
        parsed = json.loads(response.text)
        return LLMResponse(text=response.text, parsed=parsed, provider="gemini",
                           model=self.model_name,
                           input_tokens=response.usage_metadata.prompt_token_count if hasattr(response, 'usage_metadata') else None,
                           output_tokens=response.usage_metadata.candidates_token_count if hasattr(response, 'usage_metadata') else None)

    async def chat_tools(self, system: str, user: str, tools: list[dict]) -> LLMResponse:
        fn_decls = [genai.protos.FunctionDeclaration(**t) for t in tools]
        tool_config = genai.Tool(function_declarations=fn_decls)
        response = self.client.generate_content(f"{system}\n\n{user}", tools=[tool_config])
        call = response.candidates[0].content.parts[0].function_call
        parsed = {"name": call.name, "arguments": dict(call.args)}
        return LLMResponse(text=str(parsed), parsed=parsed, provider="gemini",
                           model=self.model_name, input_tokens=None, output_tokens=None)
