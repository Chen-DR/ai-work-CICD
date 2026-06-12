"""Benchmark business logic."""

import os
import uuid
from django.conf import settings
from .models import BenchmarkScript, BenchmarkJob
from .serializers import BenchmarkScriptSerializer
from . import tasks


class BenchmarkService:
    """Handles benchmark script storage and job creation."""

    def save_script(
        self,
        project_id: int,
        name: str,
        script_type: str,
        file,
        description: str = "",
        user=None,
    ) -> BenchmarkScript:
        """Save an uploaded benchmark script."""
        ext = os.path.splitext(file.name)[1].lower()
        safe_name = f"{uuid.uuid4().hex}{ext}"
        storage_path = os.path.join("uploads", "benchmark", safe_name)
        full_path = os.path.join(settings.DATA_ROOT, storage_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)

        with open(full_path, "wb") as f:
            f.write(file.read())

        script = BenchmarkScript.objects.create(
            project_id=project_id,
            name=name,
            script_type=script_type,
            file_name=file.name,
            storage_path=storage_path,
            description=description,
            created_by=user,
        )
        return script

    def create_job(self, project_id: int, script_id: int, server_id: int, workdir: str, params: dict, user=None) -> BenchmarkJob:
        """Create a benchmark job and dispatch Celery task."""
        job = BenchmarkJob.objects.create(
            project_id=project_id,
            script_id=script_id,
            server_id=server_id,
            workdir=workdir,
            params=params,
            created_by=user,
        )
        task = tasks.run_benchmark_job_task.delay(job.id)
        job.celery_task_id = task.id
        job.save(update_fields=["celery_task_id"])
        return job
