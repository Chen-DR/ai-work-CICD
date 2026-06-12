import os
import shutil
from pathlib import Path
from django.conf import settings


class LocalStorage:
    """Local filesystem storage adapter."""

    def __init__(self, base_path: str = ""):
        self.base = Path(settings.DATA_ROOT) / base_path
        self.base.mkdir(parents=True, exist_ok=True)

    def write(self, relative_path: str, content: bytes) -> str:
        full = self.base / relative_path
        full.parent.mkdir(parents=True, exist_ok=True)
        full.write_bytes(content)
        return str(full)

    def read(self, relative_path: str) -> bytes:
        full = self.base / relative_path
        return full.read_bytes()

    def delete(self, relative_path: str) -> bool:
        full = self.base / relative_path
        if full.exists():
            full.unlink()
            return True
        return False

    def exists(self, relative_path: str) -> bool:
        return (self.base / relative_path).exists()

    def size(self, relative_path: str) -> int:
        return (self.base / relative_path).stat().st_size
