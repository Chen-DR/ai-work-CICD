import os
import uuid

from django.conf import settings

from .models import ScriptExecutionTask, ScriptFile
from .validators import script_language, validate_script_file


class ScriptService:
    def save_script(self, *, project_id: int, name: str, file, description: str = "", user=None) -> ScriptFile:
        validate_script_file(file)
        ext = os.path.splitext(file.name)[1].lower()
        safe_name = f"{uuid.uuid4().hex}{ext}"
        storage_path = os.path.join("uploads", "scripts", safe_name)
        full_path = os.path.join(settings.DATA_ROOT, storage_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)

        with open(full_path, "wb") as output:
            for chunk in file.chunks():
                output.write(chunk)

        return ScriptFile.objects.create(
            project_id=project_id,
            name=name or os.path.splitext(file.name)[0],
            file_name=file.name,
            storage_path=storage_path,
            description=description,
            language=script_language(file.name),
            created_by=user,
        )

    def script_full_path(self, script: ScriptFile) -> str:
        return os.path.join(settings.DATA_ROOT, script.storage_path)

    def read_script_content(self, script: ScriptFile) -> str:
        with open(self.script_full_path(script), "r", encoding="utf-8", errors="replace") as f:
            return f.read()

    def update_script_content(self, script: ScriptFile, content: str) -> None:
        with open(self.script_full_path(script), "w", encoding="utf-8") as f:
            f.write(content)

    def delete_script_file(self, script: ScriptFile) -> None:
        try:
            os.remove(self.script_full_path(script))
        except FileNotFoundError:
            pass

    def create_task(
        self,
        *,
        script: ScriptFile,
        server,
        cwd: str,
        args: str = "",
        timeout: int = 3600,
        run_as: str = "",
        user=None,
    ) -> ScriptExecutionTask:
        from . import tasks

        task = ScriptExecutionTask.objects.create(
            project=script.project,
            script=script,
            server=server,
            cwd=cwd,
            args=args or "",
            timeout=timeout,
            run_as=run_as or "",
            created_by=user,
        )
        celery_task = tasks.run_script_task.apply_async(args=[str(task.task_id)])
        task.celery_task_id = celery_task.id
        task.save(update_fields=["celery_task_id"])
        return task
