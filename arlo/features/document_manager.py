"""
Document Manager feature. Manages file upload, parsing, and vector store indexing.
"""

from datetime import datetime
import os
from pathlib import Path
from typing import List, Optional
from arlo.core.database import get_db_connection
from arlo.core.config import UPLOAD_DIR
from arlo.core.models import Document, DocumentCreate


class DocumentManager:
    def __init__(self, doc_processor, rag_service):
        self.doc_processor = doc_processor
        self.rag_service = rag_service

    def upload_and_index_document(self, project_id: int, filename: str, file_content: bytes, doc_type: str) -> Document:
        """
        Saves a document to disk, parses text, chunks it,
        inserts metadata into SQLite, and indexes chunk embeddings in ChromaDB.
        """
        project_upload_dir = Path(UPLOAD_DIR) / str(project_id)
        project_upload_dir.mkdir(parents=True, exist_ok=True)
        
        filepath = project_upload_dir / filename
        with open(filepath, "wb") as f:
            f.write(file_content)

        filesize_bytes = len(file_content)
        now = datetime.utcnow().isoformat()

        # Parse text content
        text = self.doc_processor.extract_text(str(filepath))
        chunks = self.doc_processor.chunk_text(text)
        chunk_count = len(chunks)

        # 1. Insert file metadata in SQLite
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO documents (project_id, filename, filepath, filesize_bytes, doc_type, chunk_count, is_deleted, uploaded_at)
                VALUES (?, ?, ?, ?, ?, ?, 0, ?);
                """,
                (project_id, filename, str(filepath), filesize_bytes, doc_type, chunk_count, now)
            )
            document_id = cursor.lastrowid
            conn.commit()

        # 2. Add chunk embeddings to vector database (ChromaDB)
        metadatas = [
            {"project_id": project_id, "document_id": document_id, "filename": filename, "chunk_index": idx}
            for idx in range(len(chunks))
        ]
        self.rag_service.add_kb_chunks(
            project_id=project_id,
            document_id=document_id,
            chunks=chunks,
            metadatas=metadatas
        )

        return Document(
            id=document_id,
            project_id=project_id,
            filename=filename,
            filepath=str(filepath),
            filesize_bytes=filesize_bytes,
            doc_type=doc_type,
            chunk_count=chunk_count,
            is_deleted=False,
            uploaded_at=datetime.fromisoformat(now)
        )

    def delete_document(self, project_id: int, document_id: int) -> None:
        """
        Performs hard-delete from disk and ChromaDB.
        Updates SQLite metadata with a tombstone (is_deleted = 1).
        """
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT filepath FROM documents WHERE id = ?;", (document_id,))
            row = cursor.fetchone()
            if not row:
                raise ValueError(f"Document with ID {document_id} not found.")
            
            filepath = row[0]
            
            # Remove file from disk
            if os.path.exists(filepath):
                try:
                    os.remove(filepath)
                except OSError as e:
                    print(f"Error deleting file from disk: {e}")

            # Delete from ChromaDB
            self.rag_service.delete_document_chunks(project_id, document_id)

            # Set tombstone flag in SQLite
            cursor.execute("UPDATE documents SET is_deleted = 1 WHERE id = ?;", (document_id,))
            conn.commit()


    def list_project_documents(self, project_id: int) -> List[Document]:
        """Lists active (non-deleted) documents for a project."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM documents WHERE project_id = ? AND is_deleted = 0 ORDER BY uploaded_at DESC;",
                (project_id,)
            )
            rows = cursor.fetchall()
            return [
                Document(
                    id=row["id"],
                    project_id=row["project_id"],
                    filename=row["filename"],
                    filepath=row["filepath"],
                    filesize_bytes=row["filesize_bytes"],
                    doc_type=row["doc_type"],
                    chunk_count=row["chunk_count"],
                    is_deleted=bool(row["is_deleted"]),
                    uploaded_at=datetime.fromisoformat(row["uploaded_at"])
                )
                for row in rows
            ]
