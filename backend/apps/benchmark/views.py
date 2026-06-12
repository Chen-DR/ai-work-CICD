import os
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from django.conf import settings
from django.utils import timezone
from apps.common.response import success, error
from apps.audit.services import client_ip, log_action
from .models import BenchmarkScript, BenchmarkJob
from .serializers import BenchmarkScriptSerializer, BenchmarkJobSerializer, CreateBenchmarkJobSerializer
from .services import BenchmarkService


class BenchmarkScriptViewSet(viewsets.ModelViewSet):
    queryset = BenchmarkScript.objects.all()
    serializer_class = BenchmarkScriptSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        qs = super().get_queryset()
        project_id = self.request.query_params.get("project_id")
        if project_id:
            qs = qs.filter(project_id=project_id)
        return qs

    def create(self, request, *args, **kwargs):
        file = request.FILES.get("file")
        if not file:
            return error(40001, "No file provided")

        project_id = request.data.get("project_id")
        name = request.data.get("name")
        script_type = request.data.get("script_type")

        if not all([project_id, name, script_type]):
            return error(40001, "Missing required fields: project_id, name, script_type")

        svc = BenchmarkService()
        script = svc.save_script(
            project_id=int(project_id),
            name=name,
            script_type=script_type,
            file=file,
            description=request.data.get("description", ""),
            user=request.user,
        )
        log_action(
            request.user,
            "benchmark.script.upload",
            "benchmark_script",
            script.id,
            project_id=script.project_id,
            ip_address=client_ip(request),
            detail={"file_name": script.file_name, "script_type": script.script_type},
        )
        return success(BenchmarkScriptSerializer(script).data, status=201)


class BenchmarkJobViewSet(viewsets.ModelViewSet):
    queryset = BenchmarkJob.objects.all()
    serializer_class = BenchmarkJobSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        project_id = self.request.query_params.get("project_id")
        if project_id:
            qs = qs.filter(project_id=project_id)
        return qs

    def create(self, request, *args, **kwargs):
        ser = CreateBenchmarkJobSerializer(data=request.data)
        if not ser.is_valid():
            return error(40001, "Invalid parameters", ser.errors)

        svc = BenchmarkService()
        job = svc.create_job(
            project_id=ser.validated_data["project_id"],
            script_id=ser.validated_data["script_id"],
            server_id=ser.validated_data["server_id"],
            workdir=ser.validated_data["workdir"],
            params=ser.validated_data["params"],
            user=request.user,
        )
        log_action(
            request.user,
            "benchmark.job.create",
            "benchmark_job",
            job.id,
            project_id=job.project_id,
            ip_address=client_ip(request),
            detail={"server_id": job.server_id, "workdir": job.workdir, "params": job.params},
        )
        return success(BenchmarkJobSerializer(job).data, status=201)

    @action(detail=True, methods=["get"])
    def logs(self, request, pk=None):
        job = self.get_object()
        if not job.log_path:
            return success("")
        try:
            tail = int(request.query_params.get("tail", settings.JOB_LOG_TAIL_LINES))
            path = os.path.join(settings.DATA_ROOT, job.log_path)
            with open(path, "r") as f:
                lines = f.readlines()
            return success("".join(lines[-tail:]))
        except (FileNotFoundError, IOError):
            return success("")

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        job = self.get_object()
        if job.status in ("PENDING", "RUNNING"):
            job.status = "CANCELLED"
            job.finished_at = timezone.now()
            job.save(update_fields=["status", "finished_at"])
            from celery.task.control import revoke
            if job.celery_task_id:
                revoke(job.celery_task_id, terminate=True)
            return success({"status": "CANCELLED"})
        return error(40001, "Job cannot be cancelled in current state")
