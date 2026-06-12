"""Document parsers for knowledge base."""

import re
from infrastructure.rag.splitter import split_text, CHUNK_SIZE, CHUNK_OVERLAP


ALLOWED_EXTENSIONS = {".txt", ".md", ".log", ".sh", ".def", ".json", ".yaml", ".yml"}


def is_allowed_file(filename: str) -> bool:
    """Check if the file extension is allowed for knowledge base upload."""
    import os
    ext = os.path.splitext(filename)[1].lower()
    return ext in ALLOWED_EXTENSIONS


def clean_text(text: str) -> str:
    """Clean and normalize text content."""
    # Remove excessive whitespace
    text = re.sub(r"\s+", " ", text).strip()
    # Remove null bytes
    text = text.replace("\x00", "")
    return text


def parse_document(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    """Parse document text into chunks.

    Args:
        text: Raw document text
        chunk_size: Maximum characters per chunk
        overlap: Character overlap between chunks

    Returns:
        List of text chunks
    """
    cleaned = clean_text(text)
    return list(split_text(cleaned, chunk_size, overlap))
