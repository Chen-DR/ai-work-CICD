from django.db import models


class Artifact(models.Model):
    ARTIFACT_TYPE_CHOICES = [
        ("knowledge_file", "Knowledge File"),
        ("apptainer_def", "Apptainer Definition"),
        ("build_log", "Build Log"),
        ("sif_path_record", "SIF Path Record"),
        ("benchmark_script", "Benchmark Script"),
        ("benchmark_log", "Benchmark Log"),
        ("benchmark_report", "Benchmark Report"),
        ("script_log", "Script Log"),
        ("script_output", "Script Output"),
    ]

    project = models.ForeignKey("projects.Project", on_delete=models.CASCADE, related_name="artifacts")
    job_type = models.CharField(max_length=64, blank=True)
    job_id = models.IntegerField(null=True, blank=True)
    artifact_type = models.CharField(max_length=64, choices=ARTIFACT_TYPE_CHOICES)
    file_name = models.CharField(max_length=256)
    storage_path = models.CharField(max_length=512)
    file_size = models.IntegerField(default=0)
    checksum = models.CharField(max_length=128, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.artifact_type}: {self.file_name}"
