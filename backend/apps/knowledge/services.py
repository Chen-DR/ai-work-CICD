import os
import uuid
from .models import KnowledgeDocument, KnowledgeChunk
from .parsers import is_allowed_file, parse_document
from .search import search_chunks
from infrastructure.storage.local_storage import LocalStorage


class KnowledgeService:
    def __init__(self):
        self.storage = LocalStorage("uploads/knowledge")

    def is_allowed_file(self, filename: str) -> bool:
        return is_allowed_file(filename)

    def save_document(self, project_id: int, user_id: int, file) -> KnowledgeDocument:
        content = file.read()

        # Generate safe path
        ext = os.path.splitext(file.name)[1].lower()
        safe_name = f"{uuid.uuid4().hex}{ext}"
        relative_path = safe_name
        self.storage.write(relative_path, content)

        # Create document record
        doc = KnowledgeDocument.objects.create(
            project_id=project_id,
            title=os.path.splitext(file.name)[0],
            file_name=file.name,
            file_type=ext.lstrip("."),
            storage_path=relative_path,
            status="UPLOADED",
            created_by_id=user_id,
        )

        return doc

    def _parse_document(self, doc: KnowledgeDocument, text: str):
        doc.status = "PARSING"
        doc.error_message = ""
        doc.save(update_fields=["status", "error_message"])
        KnowledgeChunk.objects.filter(document=doc).delete()
        chunks = parse_document(text)
        for i, chunk_content in enumerate(chunks):
            KnowledgeChunk.objects.create(
                document=doc,
                project_id=doc.project_id,
                chunk_index=i,
                content=chunk_content,
                metadata={"file_name": doc.file_name, "chunk_index": i},
            )
        doc.status = "READY"
        doc.save(update_fields=["status"])

    def search(self, project_id: int, query: str, top_k: int = 5) -> list[dict]:
        return search_chunks(project_id, query, top_k)
