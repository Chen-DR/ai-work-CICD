from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
from django.utils import timezone
from apps.common.constants import ACTIVE_STATUSES
from apps.common.response import success, error
from apps.audit.services import client_ip, log_action
from .models import ApptainerDefinition, ApptainerBuildJob
from .serializers import (
    ApptainerDefinitionSerializer, ApptainerBuildJobSerializer,
    GenerateDefinitionSerializer, CreateBuildJobSerializer,
)
from .services import ApptainerService
from . import tasks


class ApptainerDefinitionViewSet(viewsets.ModelViewSet):
    queryset = ApptainerDefinition.objects.all()
    serializer_class = ApptainerDefinitionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        project_id = self.request.query_params.get("project_id")
        if project_id:
            qs = qs.filter(project_id=project_id)
        return qs

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return error(40001, "请求参数不正确", serializer.errors, status=400)
        self.perform_create(serializer)
        return success(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if not serializer.is_valid():
            return error(40001, "请求参数不正确", serializer.errors, status=400)
        self.perform_update(serializer)
        return success(serializer.data)

    def perform_create(self, serializer):
        definition = serializer.save(created_by=self.request.user)
        ApptainerService().persist_definition_file(definition)
        log_action(
            self.request.user,
            "apptainer.definition.create",
            "apptainer_definition",
            definition.id,
            project_id=definition.project_id,
            ip_address=client_ip(self.request),
            detail={"name": definition.name, "storage_path": definition.storage_path},
        )

    def perform_update(self, serializer):
        definition = serializer.save()
        ApptainerService().persist_definition_file(definition)
        log_action(
            self.request.user,
            "apptainer.definition.update",
            "apptainer_definition",
            definition.id,
            project_id=definition.project_id,
            ip_address=client_ip(self.request),
            detail={"name": definition.name, "storage_path": definition.storage_path},
        )


class ApptainerBuildJobViewSet(viewsets.ModelViewSet):
    queryset = ApptainerBuildJob.objects.all()
    serializer_class = ApptainerBuildJobSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        project_id = self.request.query_params.get("project_id")
        if project_id:
            qs = qs.filter(project_id=project_id)
        return qs

    def create(self, request, *args, **kwargs):
        ser = CreateBuildJobSerializer(data=request.data)
        if not ser.is_valid():
            return error(40001, "Invalid parameters", ser.errors)

        job = ApptainerBuildJob.objects.create(
            project_id=ser.validated_data["project_id"],
            definition_id=ser.validated_data["definition_id"],
            server_id=ser.validated_data["server_id"],
            workdir=ser.validated_data["workdir"],
            output_name=ser.validated_data["output_name"],
            created_by=request.user,
        )
        log_action(
            request.user,
            "apptainer.build_job.create",
            "apptainer_build_job",
            job.id,
            project_id=job.project_id,
            ip_address=client_ip(request),
            detail={"server_id": job.server_id, "workdir": job.workdir, "output_name": job.output_name},
        )

        # Submit Celery task
        task = tasks.run_apptainer_build_task.delay(job.id)
        job.celery_task_id = task.id
        job.save(update_fields=["celery_task_id"])

        return success(ApptainerBuildJobSerializer(job).data, status=201)

    def destroy(self, request, *args, **kwargs):
        job = self.get_object()
        if job.status in ACTIVE_STATUSES:
            return error(40001, "运行中的构建任务不能删除，请先取消任务", status=400)

        log_action(
            request.user,
            "apptainer.build_job.delete",
            "apptainer_build_job",
            job.id,
            project_id=job.project_id,
            ip_address=client_ip(request),
            detail={
                "status": job.status,
                "server_id": job.server_id,
                "workdir": job.workdir,
                "output_name": job.output_name,
            },
        )
        self.perform_destroy(job)
        return success(None)

    @action(detail=True, methods=["get"])
    def logs(self, request, pk=None):
        job = self.get_object()
        if not job.log_path:
            return success("")
        try:
            import os
            tail = int(request.query_params.get("tail", settings.JOB_LOG_TAIL_LINES))
            from apps.common.storage import ensure_dir
            path = os.path.join(settings.DATA_ROOT, job.log_path)
            with open(path, "r") as f:
                lines = f.readlines()
            content = "".join(lines[-tail:])
            return success(content)
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


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def generate(request):
    ser = GenerateDefinitionSerializer(data=request.data)
    if not ser.is_valid():
        return error(40001, "Invalid parameters", ser.errors)

    svc = ApptainerService()
    try:
        definition = svc.generate_definition(**ser.validated_data, created_by=request.user)
        log_action(
            request.user,
            "apptainer.definition.generate",
            "apptainer_definition",
            definition.id,
            project_id=definition.project_id,
            ip_address=client_ip(request),
            detail={"name": definition.name, "use_knowledge": ser.validated_data.get("use_knowledge")},
        )
        return success(ApptainerDefinitionSerializer(definition).data)
    except ValueError as e:
        return error(40001, f"生成内容未通过 Definition 校验：{str(e)}", status=400)
    except Exception as e:
        return error(70001, f"Definition 生成失败：{str(e)}", status=500)
