"""Knowledge base search module."""

from typing import Optional
from .models import KnowledgeChunk, KnowledgeDocument
from infrastructure.rag.retriever import rank_chunks_by_keyword


def search_chunks(project_id: int, query: str, top_k: int = 5) -> list[dict]:
    """Search knowledge chunks across documents in a project.

    Args:
        project_id: Project to search within
        query: Natural language query string
        top_k: Maximum number of results to return

    Returns:
        List of dicts with document_id, document_title, chunk_id, content, metadata
    """
    chunks = KnowledgeChunk.objects.filter(project_id=project_id).values(
        "id", "content", "metadata", "document_id"
    )

    # Build document title lookup
    doc_titles = {
        d.id: d.title
        for d in KnowledgeDocument.objects.filter(project_id=project_id).only("id", "title")
    }

    # Enrich chunks with document title
    enriched = []
    for c in chunks:
        c["document_title"] = doc_titles.get(c["document_id"], "Unknown")
        enriched.append(c)

    # Rank by keyword relevance
    results = rank_chunks_by_keyword(enriched, query, top_k)

    return [
        {
            "document_id": r["document_id"],
            "document_title": r.get("document_title", ""),
            "chunk_id": r["id"],
            "content": r["content"],
            "metadata": r.get("metadata", {}),
        }
        for r in results
    ]
