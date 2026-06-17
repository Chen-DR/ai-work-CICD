import json
import os
import time

from celery import current_app
from django.conf import settings
from django.http import StreamingHttpResponse
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated

from apps.audit.services import client_ip, log_action
from apps.common.response import error, success
from apps.servers.models import Server
from infrastructure.ssh.guards import validate_server_workdir
from .models import ScriptExecutionTask, ScriptFile, ScriptParamPreset
from .serializers import (
    ScriptExecuteSerializer,
    ScriptExecutionTaskSerializer,
    ScriptFileSerializer,
    ScriptParamPresetSerializer,
    ScriptUpdateSerializer,
)
from .services import ScriptService
from .validators import validate_server_run_as


def sync_celery_terminal_state(task: ScriptExecutionTask) -> ScriptExecutionTask:
    if task.status not in ("PENDING", "RUNNING") or not task.celery_task_id:
        return task

    result = current_app.AsyncResult(task.celery_task_id)
    if result.state == "FAILURE":
        task.status = "FAILED"
        task.error_message = str(result.result) or "Celery task failed"
        task.finished_at = timezone.now()
        task.save(update_fields=["status", "error_message", "finished_at"])
    elif result.state == "REVOKED":
        task.status = "CANCELLED"
        task.error_message = "任务已被撤销"
        task.finished_at = timezone.now()
        task.save(update_fields=["status", "error_message", "finished_at"])
    return task


class ScriptFileViewSet(viewsets.ModelViewSet):
    queryset = ScriptFile.objects.all()
    serializer_class = ScriptFileSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    service = ScriptService()

    def get_queryset(self):
        qs = super().get_queryset()
        project_id = self.request.query_params.get("project_id")
        if project_id:
            qs = qs.filter(project_id=project_id)
        return qs

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["include_content"] = self.action == "retrieve"
        return context

    def create(self, request, *args, **kwargs):
        return self._upload_script(request)

    @action(detail=False, methods=["post"])
    def upload(self, request):
        return self._upload_script(request)

    def _upload_script(self, request):
        file = request.FILES.get("file")
        project_id = request.data.get("project_id")
        if not file or not project_id:
            return error(40001, "缺少脚本文件或项目 ID")
        try:
            script = self.service.save_script(
                project_id=int(project_id),
                name=request.data.get("name") or os.path.splitext(file.name)[0],
                file=file,
                description=request.data.get("description", ""),
                user=request.user,
            )
        except ValueError as exc:
            return error(40001, str(exc), status=400)

        log_action(
            request.user,
            "script.upload",
            "script",
            script.id,
            project_id=script.project_id,
            ip_address=client_ip(request),
            detail={"file_name": script.file_name, "language": script.language},
        )
        return success(ScriptFileSerializer(script).data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        script = self.get_object()
        serializer = ScriptUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return error(40001, "请求参数不正确", serializer.errors, status=400)

        data = serializer.validated_data
        if "name" in data:
            script.name = data["name"]
        if "description" in data:
            script.description = data["description"]
        if "content" in data:
            self.service.update_script_content(script, data["content"])
        script.save()
        log_action(
            request.user,
            "script.update",
            "script",
            script.id,
            project_id=script.project_id,
            ip_address=client_ip(request),
            detail={"name": script.name},
        )
        return success(ScriptFileSerializer(script, context={"include_content": True}).data)

    def destroy(self, request, *args, **kwargs):
        script = self.get_object()
        log_action(
            request.user,
            "script.delete",
            "script",
            script.id,
            project_id=script.project_id,
            ip_address=client_ip(request),
            detail={"file_name": script.file_name},
        )
        self.service.delete_script_file(script)
        self.perform_destroy(script)
        return success(None)

    @action(detail=True, methods=["post"])
    def execute(self, request, pk=None):
        script = self.get_object()
        serializer = ScriptExecuteSerializer(data=request.data)
        if not serializer.is_valid():
            return error(40001, "请求参数不正确", serializer.errors, status=400)

        try:
            server = Server.objects.get(id=serializer.validated_data["server_id"], project=script.project)
            cwd = validate_server_workdir(server, serializer.validated_data["cwd"], {"script", "general"})
            run_as = validate_server_run_as(server, serializer.validated_data.get("run_as", ""))
        except Server.DoesNotExist:
            return error(40401, "服务器不存在或不属于当前项目", status=404)
        except PermissionError as exc:
            return error(60002, str(exc), status=400)
        except ValueError as exc:
            return error(40001, str(exc), status=400)

        task = self.service.create_task(
            script=script,
            server=server,
            cwd=cwd,
            args=serializer.validated_data.get("args", ""),
            timeout=serializer.validated_data.get("timeout", settings.SCRIPT_DEFAULT_TIMEOUT),
            run_as=run_as,
            user=request.user,
        )
        log_action(
            request.user,
            "script.execute",
            "script_task",
            task.task_id,
            project_id=task.project_id,
            ip_address=client_ip(request),
            detail={
                "script_id": script.id,
                "server_id": server.id,
                "cwd": task.cwd,
                "timeout": task.timeout,
                "run_as": task.run_as,
            },
        )
        return success(ScriptExecutionTaskSerializer(task).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["get", "post"])
    def presets(self, request, pk=None):
        script = self.get_object()
        if request.method == "GET":
            presets = script.param_presets.all()
            return success(ScriptParamPresetSerializer(presets, many=True).data)

        serializer = ScriptParamPresetSerializer(data=request.data)
        if not serializer.is_valid():
            return error(40001, "请求参数不正确", serializer.errors, status=400)
        if script.param_presets.filter(name=serializer.validated_data["name"]).exists():
            return error(40001, "同名参数预设已存在", status=400)

        preset = serializer.save(script=script, created_by=request.user)
        log_action(
            request.user,
            "script.preset.create",
            "script_param_preset",
            preset.id,
            project_id=script.project_id,
            ip_address=client_ip(request),
            detail={"script_id": script.id, "name": preset.name},
        )
        return success(ScriptParamPresetSerializer(preset).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["put", "delete"], url_path=r"presets/(?P<preset_id>[^/.]+)")
    def preset_detail(self, request, pk=None, preset_id=None):
        script = self.get_object()
        try:
            preset = script.param_presets.get(id=preset_id)
        except ScriptParamPreset.DoesNotExist:
            return error(40401, "参数预设不存在", status=404)

        if request.method == "DELETE":
            detail = {"script_id": script.id, "name": preset.name}
            preset.delete()
            log_action(
                request.user,
                "script.preset.delete",
                "script_param_preset",
                preset_id,
                project_id=script.project_id,
                ip_address=client_ip(request),
                detail=detail,
            )
            return success(None)

        serializer = ScriptParamPresetSerializer(preset, data=request.data, partial=True)
        if not serializer.is_valid():
            return error(40001, "请求参数不正确", serializer.errors, status=400)
        name = serializer.validated_data.get("name")
        if name and script.param_presets.exclude(id=preset.id).filter(name=name).exists():
            return error(40001, "同名参数预设已存在", status=400)

        preset = serializer.save()
        log_action(
            request.user,
            "script.preset.update",
            "script_param_preset",
            preset.id,
            project_id=script.project_id,
            ip_address=client_ip(request),
            detail={"script_id": script.id, "name": preset.name},
        )
        return success(ScriptParamPresetSerializer(preset).data)

    @action(detail=True, methods=["post"], url_path=r"presets/(?P<preset_id>[^/.]+)/use")
    def use_preset(self, request, pk=None, preset_id=None):
        script = self.get_object()
        try:
            preset = script.param_presets.get(id=preset_id)
        except ScriptParamPreset.DoesNotExist:
            return error(40401, "参数预设不存在", status=404)

        preset.last_used_at = timezone.now()
        preset.save(update_fields=["last_used_at", "updated_at"])
        return success(ScriptParamPresetSerializer(preset).data)

    @action(detail=True, methods=["get"])
    def recent_cwds(self, request, pk=None):
        script = self.get_object()
        qs = script.tasks.exclude(cwd="").order_by("-created_at").values_list("cwd", flat=True)
        recent = []
        for cwd in qs:
            if cwd not in recent:
                recent.append(cwd)
            if len(recent) >= 3:
                break
        return success(recent)


class ScriptExecutionTaskViewSet(viewsets.ModelViewSet):
    queryset = ScriptExecutionTask.objects.select_related("script").all()
    serializer_class = ScriptExecutionTaskSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "task_id"
    http_method_names = ["get", "delete", "head", "options"]

    def retrieve(self, request, *args, **kwargs):
        task = sync_celery_terminal_state(self.get_object())
        return success(self.get_serializer(task).data)

    def get_queryset(self):
        qs = super().get_queryset()
        project_id = self.request.query_params.get("project_id")
        script_id = self.request.query_params.get("script_id")
        if project_id:
            qs = qs.filter(project_id=project_id)
        if script_id:
            qs = qs.filter(script_id=script_id)
        return qs

    def destroy(self, request, *args, **kwargs):
        task = self.get_object()
        if task.status not in ("PENDING", "RUNNING"):
            return error(40001, "任务当前状态不能终止", status=400)
        task.status = "CANCELLED"
        task.finished_at = timezone.now()
        task.save(update_fields=["status", "finished_at"])
        if task.celery_task_id:
            current_app.control.revoke(task.celery_task_id)
        return success({"status": "CANCELLED"})

    @action(detail=True, methods=["delete"])
    def terminate(self, request, task_id=None):
        return self.destroy(request, task_id=task_id)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def stream_task_logs(request, task_id):
    try:
        task = ScriptExecutionTask.objects.get(task_id=task_id)
    except ScriptExecutionTask.DoesNotExist:
        return error(40401, "任务不存在", status=404)

    def event_stream():
        nonlocal task
        offset = 0
        idle_count = 0
        while True:
            task.refresh_from_db(fields=["status", "log_path"])
            previous_status = task.status
            task = sync_celery_terminal_state(task)
            if previous_status != task.status and task.status in ("FAILED", "CANCELLED"):
                if task.error_message:
                    yield f"data: {json.dumps({'type': 'stderr', 'line': task.error_message, 'ts': ''}, ensure_ascii=False)}\n\n"
                yield f"data: {json.dumps({'type': 'exit', 'code': -1, 'ts': ''}, ensure_ascii=False)}\n\n"
                break
            if task.log_path:
                path = os.path.join(settings.DATA_ROOT, task.log_path)
                if os.path.exists(path):
                    with open(path, "r", encoding="utf-8", errors="replace") as f:
                        f.seek(offset)
                        chunk = f.read()
                        offset = f.tell()
                    if chunk:
                        idle_count = 0
                        for line in chunk.splitlines():
                            try:
                                payload = json.loads(line)
                            except json.JSONDecodeError:
                                payload = {"type": "stdout", "line": line, "ts": ""}
                            yield f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"
                    else:
                        idle_count += 1
            if task.status in ("SUCCESS", "FAILED", "CANCELLED", "TIMEOUT") and idle_count > 1:
                break
            time.sleep(1)

    response = StreamingHttpResponse(event_stream(), content_type="text/event-stream")
    response["Cache-Control"] = "no-cache"
    response["X-Accel-Buffering"] = "no"
    return response
