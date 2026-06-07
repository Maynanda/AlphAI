# services/llm/provider.py
from arlo.core.config import settings
from arlo.services.llm.base import LLMProvider

_instance: LLMProvider | None = None

def get_provider() -> LLMProvider:
    """
    Returns the active LLM provider singleton.
    Initialized at startup via FastAPI lifespan.
    Routers receive this via Depends(get_provider).
    """
    global _instance
    if _instance:
        return _instance

    p = settings.llm_provider

    if p == "local_hf":
        from arlo.services.llm.adapters.local_hf import LocalHFAdapter
        _instance = LocalHFAdapter(model_path=settings.llm_model_path)

    elif p == "gemini":
        from arlo.services.llm.adapters.gemini import GeminiAdapter
        _instance = GeminiAdapter(
            api_key=settings.gemini_api_key,
            model=settings.llm_model_name
        )

    elif p == "anthropic":
        from arlo.services.llm.adapters.anthropic import AnthropicAdapter
        _instance = AnthropicAdapter(
            api_key=settings.anthropic_api_key,
            model=settings.llm_model_name
        )

    elif p == "openai_compat":
        from arlo.services.llm.adapters.openai_compat import OpenAICompatAdapter
        _instance = OpenAICompatAdapter(
            api_key=settings.openai_api_key,
            model=settings.llm_model_name,
            base_url=settings.llm_base_url
        )

    else:
        raise ValueError(f"Unknown llm_provider: {p}")

    return _instance
