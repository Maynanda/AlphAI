"""
FastAPI dependency injectors.
Singleton instances for LLM, EmbeddingService, and RAGService.
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Singletons — populated at startup lifespan
_llm_instance = None
_embedding_instance = None
_rag_instance = None
_doc_processor_instance = None
_doc_manager_instance = None


def get_llm():
    """Returns the global LLM instance (may be None if not loaded)."""
    return _llm_instance


def get_embedding():
    """Returns the global EmbeddingService instance."""
    return _embedding_instance


def get_rag():
    """Returns the global RAGService instance."""
    return _rag_instance


def get_doc_processor():
    """Returns the global DocumentProcessor instance."""
    return _doc_processor_instance


def get_doc_manager():
    """Returns the global DocumentManager instance."""
    return _doc_manager_instance


def initialize_services(model_path: str, embedding_name: str) -> dict:
    """
    Called once at app startup to load models and initialize services.
    Returns status dict.
    """
    global _llm_instance, _embedding_instance, _rag_instance, _doc_processor_instance, _doc_manager_instance
    status = {"llm_available": False, "rag_available": False, "embedding_available": False}

    # Initialize DocumentProcessor
    try:
        from arlo.services.document_processor import DocumentProcessor
        _doc_processor_instance = DocumentProcessor()
    except Exception as e:
        logger.warning(f"Failed to initialize DocumentProcessor: {e}")

    # Embedding (lightweight — always try)
    try:
        from arlo.services.embedding import EmbeddingService
        _embedding_instance = EmbeddingService(model_name=embedding_name)
        _embedding_instance.load()
        status["embedding_available"] = True
        logger.info("Embedding model loaded.")
    except Exception as e:
        logger.warning(f"Embedding model failed to load: {e}")

    # RAG (needs embedding)
    if _embedding_instance:
        try:
            from arlo.services.rag import RAGService
            _rag_instance = RAGService(embedding_service=_embedding_instance)
            _rag_instance.initialize()
            status["rag_available"] = True
            logger.info("RAG service initialized.")
        except Exception as e:
            logger.warning(f"RAG service failed to initialize: {e}")

    # Initialize DocumentManager if RAG and DocProcessor are available
    if _rag_instance and _doc_processor_instance:
        try:
            from arlo.features.document_manager import DocumentManager
            _doc_manager_instance = DocumentManager(_doc_processor_instance, _rag_instance)
            logger.info("DocumentManager initialized.")
        except Exception as e:
            logger.warning(f"Failed to initialize DocumentManager: {e}")

    # LLM (heavy local or lightweight Gemini API)
    from arlo.core.config import is_use_gemini_api, get_gemini_api_key
    if is_use_gemini_api():
        api_key = get_gemini_api_key()
        if api_key:
            try:
                from arlo.services.llm import GeminiLLM
                model_name = model_path if (model_path and "gemini" in model_path) else "gemini-1.5-flash"
                _llm_instance = GeminiLLM(api_key=api_key, model_name=model_name)
                success = _llm_instance.load_model()
                status["llm_available"] = success
                if success:
                    logger.info(f"Gemini API LLM initialized successfully with model: {model_name}")
                else:
                    _llm_instance = None
            except Exception as e:
                logger.warning(f"Failed to load Gemini API LLM: {e}")
                _llm_instance = None
        else:
            logger.warning("Gemini API is enabled but no API key was provided.")
            _llm_instance = None
    elif model_path and model_path.strip():
        try:
            from arlo.services.llm import LocalLLM
            _llm_instance = LocalLLM(model_path=model_path)
            success = _llm_instance.load_model()
            status["llm_available"] = success
            if success:
                logger.info("Local LLM loaded successfully.")
            else:
                _llm_instance = None
        except Exception as e:
            logger.warning(f"LLM failed to load: {e}")
            _llm_instance = None

    return status

