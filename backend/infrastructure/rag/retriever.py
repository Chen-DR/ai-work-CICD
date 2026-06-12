from typing import Optional
from .keyword_search import extract_keywords


def rank_chunks_by_keyword(chunks: list[dict], query: str, top_k: int = 5) -> list[dict]:
    """Simple keyword-based chunk ranking."""
    keywords = extract_keywords(query)

    scored = []
    for chunk in chunks:
        content = chunk.get("content", "").lower()
        score = sum(1 for kw in keywords if kw.lower() in content)
        scored.append((chunk, score))

    scored.sort(key=lambda x: x[1], reverse=True)
    return [item[0] for item in scored[:top_k] if item[1] > 0]
