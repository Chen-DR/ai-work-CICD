"""Artifact business logic."""

import os
from django.conf import settings
from django.http import FileResponse
from .models import Artifact


class ArtifactService:
    """Handles artifact file operations."""

    def get_download_response(self, artifact: Artifact):
        """Return a file download response for an artifact."""
        full_path = os.path.join(settings.DATA_ROOT, artifact.storage_path)
        if not os.path.exists(full_path):
            return None
        return FileResponse(
            open(full_path, "rb"),
            as_attachment=True,
            filename=artifact.file_name,
        )

    def delete_artifact_file(self, artifact: Artifact) -> bool:
        """Delete the physical file associated with an artifact."""
        full_path = os.path.join(settings.DATA_ROOT, artifact.storage_path)
        if os.path.exists(full_path):
            os.remove(full_path)
            return True
        return False
