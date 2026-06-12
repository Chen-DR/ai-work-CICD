from django.db import models
from django.contrib.auth.models import User


class KnowledgeDocument(models.Model):
    STATUS_CHOICES = [
        ("UPLOADED", "Uploaded"),
        ("PARSING", "Parsing"),
        ("READY", "Ready"),
        ("FAILED", "Failed"),
    ]

    project = models.ForeignKey("projects.Project", on_delete=models.CASCADE, related_name="knowledge_docs")
    title = models.CharField(max_length=256, blank=True)
    file_name = models.CharField(max_length=256)
    file_type = models.CharField(max_length=32)
    storage_path = models.CharField(max_length=512)
    status = models.CharField(max_length=32, choices=STATUS_CHOICES, default="UPLOADED")
    error_message = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.file_name


class KnowledgeChunk(models.Model):
    document = models.ForeignKey(KnowledgeDocument, on_delete=models.CASCADE, related_name="chunks")
    project = models.ForeignKey("projects.Project", on_delete=models.CASCADE)
    chunk_index = models.IntegerField()
    content = models.TextField()
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["chunk_index"]

    def __str__(self):
        return f"{self.document.file_name} chunk {self.chunk_index}"
