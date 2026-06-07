"""
FastAPI dependency injectors.
Singleton instances for Database, RAGService, and LLM Provider.
"""

from arlo.core.database import Database
from arlo.services.llm.provider import get_provider
from arlo.core.config import settings

_db: Database | None = None
_rag = None # Placeholder for RAGService until updated

async def get_db() -> Database:
    global _db
    if not _db:
        _db = Database(settings.db_path)
        await _db.connect()
    return _db

async def get_rag():
    global _rag
    if not _rag:
        try:
            from arlo.services.rag import RAGService
            _rag = RAGService(settings.chroma_path)
        except ImportError:
            _rag = None
    return _rag

# Fallbacks for legacy routers
def get_llm():
    return get_provider()

def get_embedding():
    return None

def get_doc_processor():
    return None

def get_doc_manager():
    return None

def initialize_services(model_path: str = "", embedding_name: str = "") -> dict:
    return {"llm_available": True, "rag_available": False, "embedding_available": False}


