import os
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
from apps.common.response import success, error
from .models import Artifact
from .serializers import ArtifactSerializer
from .services import ArtifactService


class ArtifactViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Artifact.objects.all()
    serializer_class = ArtifactSerializer
    permission_classes = [IsAuthenticated]
    service = ArtifactService()

    def get_queryset(self):
        qs = super().get_queryset()
        project_id = self.request.query_params.get("project_id")
        job_type = self.request.query_params.get("job_type")
        artifact_type = self.request.query_params.get("artifact_type")
        if project_id:
            qs = qs.filter(project_id=project_id)
        if job_type:
            qs = qs.filter(job_type=job_type)
        if artifact_type:
            qs = qs.filter(artifact_type=artifact_type)
        return qs

    @action(detail=True, methods=["get"])
    def download(self, request, pk=None):
        artifact = self.get_object()
        response = self.service.get_download_response(artifact)
        if response is None:
            return error(40401, "File not found on disk", status=404)
        return response

    def destroy(self, request, *args, **kwargs):
        artifact = self.get_object()
        self.service.delete_artifact_file(artifact)
        return super().destroy(request, *args, **kwargs)
