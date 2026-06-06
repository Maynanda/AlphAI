"""
RAG service module using ChromaDB for local vector storage.
"""

import logging
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings
from arlo.core.config import CHROMA_DB_PATH

logger = logging.getLogger(__name__)

class RAGService:
    def __init__(self, embedding_service):
        self.embedding_service = embedding_service
        self.client = None

    def initialize(self) -> None:
        """Initializes the Chroma persistent client."""
        try:
            logger.info(f"Initializing ChromaDB client at: {CHROMA_DB_PATH}")
            self.client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
            logger.info("ChromaDB initialized.")
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")
            raise

    def _get_kb_collection_name(self, project_id: int) -> str:
        return f"project_{project_id}_kb"

    def _get_fragments_collection_name(self, project_id: int) -> str:
        return f"project_{project_id}_fragments"

    def add_kb_chunks(self, project_id: int, document_id: int, chunks: List[str], metadatas: List[Dict[str, Any]]) -> None:
        """
        Adds text chunks to the project knowledge base vector collection.
        """
        if self.client is None:
            self.initialize()

        collection_name = self._get_kb_collection_name(project_id)
        collection = self.client.get_or_create_collection(name=collection_name)

        embeddings = self.embedding_service.embed_documents(chunks)
        ids = [f"doc_{document_id}_chunk_{i}" for i in range(len(chunks))]

        collection.add(
            documents=chunks,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )
        logger.info(f"Added {len(chunks)} chunks to KB collection: {collection_name}")

    def add_fragment_chunks(self, project_id: int, fragment_id: int, chunks: List[str]) -> None:
        """
        Adds communication fragment chunks to the fragments vector collection.
        """
        if self.client is None:
            self.initialize()

        collection_name = self._get_fragments_collection_name(project_id)
        collection = self.client.get_or_create_collection(name=collection_name)

        embeddings = self.embedding_service.embed_documents(chunks)
        ids = [f"frag_{fragment_id}_chunk_{i}" for i in range(len(chunks))]
        metadatas = [{"fragment_id": fragment_id} for _ in chunks]

        collection.add(
            documents=chunks,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )
        logger.info(f"Added {len(chunks)} chunks to fragments collection: {collection_name}")

    def query_context(self, project_id: int, query: str, top_k: int = 5, collections: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Queries KB and/or fragments collections for top_k similar chunks.
        """
        if self.client is None:
            self.initialize()

        results = []
        query_embedding = self.embedding_service.embed_query(query)
        target_collections = collections or ["kb", "fragments"]

        for col_type in target_collections:
            name = (
                self._get_kb_collection_name(project_id)
                if col_type == "kb"
                else self._get_fragments_collection_name(project_id)
            )
            try:
                collection = self.client.get_collection(name=name)
                res = collection.query(
                    query_embeddings=[query_embedding],
                    n_results=top_k
                )
                
                # Format results
                if res and "documents" in res and res["documents"]:
                    docs = res["documents"][0]
                    metas = res["metadatas"][0] if "metadatas" in res and res["metadatas"] else [{}] * len(docs)
                    dists = res["distances"][0] if "distances" in res and res["distances"] else [0.0] * len(docs)
                    ids = res["ids"][0] if "ids" in res and res["ids"] else [""] * len(docs)

                    for d, m, dist, idx in zip(docs, metas, dists, ids):
                        results.append({
                            "content": d,
                            "metadata": m,
                            "distance": dist,
                            "id": idx,
                            "source": col_type
                        })
            except Exception as e:
                # Collection might not exist yet if no files uploaded
                logger.warning(f"Collection {name} not queryable (might not exist): {e}")

        # Sort by distance (smaller distance = higher similarity)
        results.sort(key=lambda x: x["distance"])
        return results[:top_k]

    def delete_document_chunks(self, project_id: int, document_id: int) -> None:
        """Deletes all chunks associated with a specific document."""
        if self.client is None:
            self.initialize()

        collection_name = self._get_kb_collection_name(project_id)
        try:
            collection = self.client.get_collection(name=collection_name)
            # Use where clause to match metadata
            collection.delete(where={"document_id": document_id})
            logger.info(f"Deleted chunks for document {document_id} from {collection_name}")
        except Exception as e:
            logger.error(f"Error deleting document {document_id} chunks: {e}")

    def delete_project_collections(self, project_id: int) -> None:
        """Deletes both collections associated with a project."""
        if self.client is None:
            self.initialize()

        for name in [self._get_kb_collection_name(project_id), self._get_fragments_collection_name(project_id)]:
            try:
                self.client.delete_collection(name=name)
                logger.info(f"Deleted collection: {name}")
            except Exception as e:
                logger.warning(f"Could not delete collection {name}: {e}")
