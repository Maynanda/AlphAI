"""
Document parsing and chunking service (Unstructured + PyMuPDF).
"""

import logging
from typing import List, Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)

class DocumentProcessor:
    def __init__(self, chunk_size: int = 512, overlap: int = 64):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def extract_text(self, filepath: str) -> str:
        """
        Extracts text from PDF, MD, TXT, DOCX using PyMuPDF or Unstructured.
        """
        path = Path(filepath)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {filepath}")

        ext = path.suffix.lower()
        if ext == ".pdf":
            return self._extract_pdf(path)
        elif ext in [".txt", ".md"]:
            return self._extract_text_file(path)
        elif ext in [".docx", ".doc"]:
            return self._extract_docx(path)
        else:
            raise ValueError(f"Unsupported file type: {ext}")

    def _extract_pdf(self, path: Path) -> str:
        """Extracts PDF text using PyMuPDF (fitz)."""
        try:
            import fitz  # PyMuPDF
            doc = fitz.open(path)
            text = ""
            for page in doc:
                text += page.get_text()
            return text
        except ImportError:
            logger.warning("PyMuPDF (fitz) not installed, falling back to basic parsing.")
            raise
        except Exception as e:
            logger.error(f"Error reading PDF {path}: {e}")
            raise

    def _extract_text_file(self, path: Path) -> str:
        """Extracts plain text files."""
        return path.read_text(encoding="utf-8", errors="ignore")

    def _extract_docx(self, path: Path) -> str:
        """Extracts text using unstructured library."""
        try:
            from unstructured.partition.docx import partition_docx
            elements = partition_docx(filename=str(path))
            return "\n\n".join([el.text for el in elements])
        except ImportError:
            logger.warning("unstructured library not installed or failed to partition docx.")
            raise
        except Exception as e:
            logger.error(f"Error reading DOCX {path}: {e}")
            raise

    def chunk_text(self, text: str) -> List[str]:
        """
        Splits text into chunks of specified token/word size with overlap.
        """
        words = text.split()
        chunks = []
        
        if len(words) <= self.chunk_size:
            return [text]

        step = self.chunk_size - self.overlap
        for i in range(0, len(words), step):
            chunk_words = words[i:i + self.chunk_size]
            chunks.append(" ".join(chunk_words))
            if i + self.chunk_size >= len(words):
                break
                
        return chunks
