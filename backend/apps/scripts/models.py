import uuid

from django.contrib.auth.models import User
from django.db import models


class ScriptFile(models.Model):
    LANGUAGE_CHOICES = [
        ("shell", "Shell"),
        ("python", "Python"),
    ]

    project = models.ForeignKey("projects.Project", on_delete=models.CASCADE, related_name="managed_scripts")
    name = models.CharField(max_length=256)
    file_name = models.CharField(max_length=256)
    storage_path = models.CharField(max_length=512)
    description = models.TextField(blank=True)
    language = models.CharField(max_length=32, choices=LANGUAGE_CHOICES, default="shell")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return self.name


class ScriptParamPreset(models.Model):
    script = models.ForeignKey(ScriptFile, on_delete=models.CASCADE, related_name="param_presets")
    name = models.CharField(max_length=64)
    args = models.TextField()
    last_used_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-last_used_at", "-created_at"]
        indexes = [
            models.Index(fields=["script", "-last_used_at"], name="idx_script_preset_used"),
        ]
        unique_together = ("script", "name")

    def __str__(self):
        return f"{self.script.name}: {self.name}"


class ScriptExecutionTask(models.Model):
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("RUNNING", "Running"),
        ("SUCCESS", "Success"),
        ("FAILED", "Failed"),
        ("CANCELLED", "Cancelled"),
        ("TIMEOUT", "Timeout"),
    ]

    task_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey("projects.Project", on_delete=models.CASCADE, related_name="script_tasks")
    script = models.ForeignKey(ScriptFile, on_delete=models.CASCADE, related_name="tasks")
    server = models.ForeignKey(
        "servers.Server",
        on_delete=models.PROTECT,
        related_name="script_tasks",
        null=True,
        blank=True,
    )
    cwd = models.CharField(max_length=512)
    args = models.CharField(max_length=1024, blank=True)
    run_as = models.CharField(max_length=64, blank=True)
    timeout = models.PositiveIntegerField(default=3600)
    status = models.CharField(max_length=32, choices=STATUS_CHOICES, default="PENDING")
    celery_task_id = models.CharField(max_length=128, blank=True)
    log_path = models.CharField(max_length=512, blank=True)
    exit_code = models.IntegerField(null=True, blank=True)
    process_id = models.IntegerField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.script.name} {self.task_id}"
