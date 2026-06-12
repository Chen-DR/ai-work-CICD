import hashlib
import os
from django.conf import settings
from .models import Artifact


def file_checksum(storage_path: str) -> str:
    full_path = os.path.join(settings.DATA_ROOT, storage_path)
    if not os.path.isfile(full_path):
        return ""
    digest = hashlib.sha256()
    with open(full_path, "rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def file_size(storage_path: str) -> int:
    full_path = os.path.join(settings.DATA_ROOT, storage_path)
    if not os.path.isfile(full_path):
        return 0
    return os.path.getsize(full_path)


def create_artifact(
    *,
    project_id: int,
    job_type: str,
    job_id: int,
    artifact_type: str,
    file_name: str,
    storage_path: str,
    local_file: bool = True,
) -> Artifact:
    size = file_size(storage_path) if local_file else 0
    checksum = file_checksum(storage_path) if local_file else ""
    return Artifact.objects.create(
        project_id=project_id,
        job_type=job_type,
        job_id=job_id,
        artifact_type=artifact_type,
        file_name=file_name,
        storage_path=storage_path,
        file_size=size,
        checksum=checksum,
    )
