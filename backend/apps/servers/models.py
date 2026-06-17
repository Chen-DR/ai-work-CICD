from django.db import models


class Server(models.Model):
    AUTH_PASSWORD = "password"
    AUTH_SSH_KEY = "ssh_key"

    STATUS_CHOICES = [
        ("ACTIVE", "Active"),
        ("DISABLED", "Disabled"),
        ("UNKNOWN", "Unknown"),
        ("FAILED", "Failed"),
    ]

    project = models.ForeignKey("projects.Project", on_delete=models.CASCADE, related_name="servers")
    name = models.CharField(max_length=128)
    host = models.CharField(max_length=128)
    port = models.IntegerField(default=22)
    username = models.CharField(max_length=128)
    auth_type = models.CharField(max_length=32, default=AUTH_PASSWORD)
    status = models.CharField(max_length=32, choices=STATUS_CHOICES, default="UNKNOWN")
    allow_script_root = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.host}:{self.port})"


class ServerCredential(models.Model):
    CREDENTIAL_PASSWORD = "password"
    CREDENTIAL_SSH_KEY = "ssh_key"

    server = models.ForeignKey(Server, on_delete=models.CASCADE, related_name="credentials")
    credential_type = models.CharField(max_length=32)
    secret = models.TextField(blank=True)
    secret_hint = models.CharField(max_length=128, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("server", "credential_type")

    def __str__(self):
        return f"{self.server.name} - {self.credential_type}"


class ServerAllowedDir(models.Model):
    PURPOSE_CHOICES = [
        ("build", "Build"),
        ("benchmark", "Benchmark"),
        ("script", "Script"),
        ("report", "Report"),
        ("general", "General"),
    ]

    server = models.ForeignKey(Server, on_delete=models.CASCADE, related_name="allowed_dirs")
    path = models.CharField(max_length=512)
    purpose = models.CharField(max_length=32, choices=PURPOSE_CHOICES, default="general")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.server.name}: {self.path}"


class ServerMetric(models.Model):
    """Collected server resource metrics."""

    server = models.ForeignKey(Server, on_delete=models.CASCADE, related_name="metrics")
    cpu_percent = models.FloatField(default=0)
    mem_percent = models.FloatField(default=0)
    mem_used_gb = models.FloatField(default=0)
    mem_total_gb = models.FloatField(default=0)
    gpu_percent = models.FloatField(default=0)
    gpu_mem_percent = models.FloatField(default=0)
    disk_percent = models.FloatField(default=0)
    disk_used_gb = models.FloatField(default=0)
    disk_total_gb = models.FloatField(default=0)
    collected_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-collected_at"]

    def __str__(self):
        return f"{self.server.name} @ {self.collected_at}"
