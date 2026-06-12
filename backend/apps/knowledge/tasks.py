import logging
from celery import shared_task
from .models import KnowledgeDocument
from .services import KnowledgeService

logger = logging.getLogger(__name__)


@shared_task
def parse_knowledge_document_task(document_id: int):
    try:
        doc = KnowledgeDocument.objects.get(id=document_id)
        svc = KnowledgeService()
        content = svc.storage.read(doc.storage_path).decode("utf-8", errors="ignore")
        svc._parse_document(doc, content)
        logger.info("Parsed document %d: %s", document_id, doc.file_name)
    except Exception as e:
        logger.error("Failed to parse document %d: %s", document_id, str(e))
        KnowledgeDocument.objects.filter(id=document_id).update(
            status="FAILED", error_message=str(e)
        )
