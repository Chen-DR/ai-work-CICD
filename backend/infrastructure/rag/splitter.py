from typing import Generator


CHUNK_SIZE = 800
CHUNK_OVERLAP = 150


def split_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> Generator[str, None, None]:
    """Split text into overlapping chunks by character count."""
    if not text:
        return
    start = 0
    while start < len(text):
        end = start + chunk_size
        yield text[start:end]
        start += chunk_size - overlap
        if start >= len(text):
            break
