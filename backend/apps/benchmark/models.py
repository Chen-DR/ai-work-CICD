from django.db import models
from django.contrib.auth.models import User


class BenchmarkScript(models.Model):
    SCRIPT_TYPE_CHOICES = [
        ("cpu", "CPU"),
        ("disk", "Disk"),
        ("gpu", "GPU"),
        ("mixed", "Mixed"),
        ("custom", "Custom"),
    ]

    project = models.ForeignKey("projects.Project", on_delete=models.CASCADE, related_name="benchmark_scripts")
    name = models.CharField(max_length=256)
    script_type = models.CharField(max_length=32, choices=SCRIPT_TYPE_CHOICES)
    version = models.CharField(max_length=64, default="v1")
    file_name = models.CharField(max_length=256)
    storage_path = models.CharField(max_length=512)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.script_type})"


class BenchmarkJob(models.Model):
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

    project = models.ForeignKey("projects.Project", on_delete=models.CASCADE, related_name="benchmark_jobs")
    script = models.ForeignKey(BenchmarkScript, on_delete=models.CASCADE)
    server = models.ForeignKey("servers.Server", on_delete=models.CASCADE)
    workdir = models.CharField(max_length=512)
    params = models.JSONField(default=dict)
    status = models.CharField(max_length=32, choices=STATUS_CHOICES, default="PENDING")
    celery_task_id = models.CharField(max_length=128, blank=True)
    log_path = models.CharField(max_length=512, blank=True)
    report_path = models.CharField(max_length=512, blank=True)
    remote_report_path = models.CharField(max_length=512, blank=True)
    error_message = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Benchmark {self.id} - {self.script.name}"
