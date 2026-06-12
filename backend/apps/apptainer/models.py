from django.db import models
from django.contrib.auth.models import User


class ApptainerDefinition(models.Model):
    project = models.ForeignKey("projects.Project", on_delete=models.CASCADE, related_name="apptainer_defs")
    conversation = models.ForeignKey("chat.Conversation", on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=256)
    version = models.CharField(max_length=64, default="v1")
    content = models.TextField()
    storage_path = models.CharField(max_length=512, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.version})"


class ApptainerBuildJob(models.Model):
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("VALIDATING", "Validating"),
        ("UPLOADING", "Uploading"),
        ("RUNNING", "Running"),
        ("COLLECTING", "Collecting"),
        ("SUCCESS", "Success"),
        ("FAILED", "Failed"),
        ("CANCELLED", "Cancelled"),
        ("TIMEOUT", "Timeout"),
    ]

    project = models.ForeignKey("projects.Project", on_delete=models.CASCADE, related_name="build_jobs")
    definition = models.ForeignKey(ApptainerDefinition, on_delete=models.CASCADE)
    server = models.ForeignKey("servers.Server", on_delete=models.CASCADE)
    workdir = models.CharField(max_length=512)
    output_name = models.CharField(max_length=256)
    status = models.CharField(max_length=32, choices=STATUS_CHOICES, default="PENDING")
    celery_task_id = models.CharField(max_length=128, blank=True)
    log_path = models.CharField(max_length=512, blank=True)
    remote_output_path = models.CharField(max_length=512, blank=True)
    error_message = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Build {self.id} - {self.output_name}"
