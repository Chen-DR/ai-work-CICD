import os
import uuid
from pathlib import Path
from django.conf import settings


def generate_storage_path(base_dir: str, original_filename: str) -> tuple[str, str]:
    """Generate a safe storage path and return (relative_path, safe_filename)."""
    ext = os.path.splitext(original_filename)[1].lower()
    safe_name = f"{uuid.uuid4().hex}{ext}"
    relative = os.path.join(base_dir, safe_name)
    return relative, safe_name


def ensure_dir(path: str) -> str:
    """Ensure directory exists and return the path."""
    p = Path(settings.DATA_ROOT) / path
    p.parent.mkdir(parents=True, exist_ok=True)
    return str(p)
