from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from apps.common.response import success, error
from apps.common.validators import validate_workdir
from apps.audit.services import client_ip, log_action
from .models import Server, ServerMetric, ServerAllowedDir
from .serializers import ServerSerializer, ServerCreateSerializer, ServerAllowedDirSerializer, ServerMetricSerializer
from .services import save_server_credentials, get_server_credentials
from .metrics import collect_server_metrics
from infrastructure.ssh.executor import SSHExecutor


class ServerViewSet(viewsets.ModelViewSet):
    queryset = Server.objects.all()
    serializer_class = ServerSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        project_id = self.request.query_params.get("project_id")
        if project_id:
            qs = qs.filter(project_id=project_id)
        return qs

    def create(self, request, *args, **kwargs):
        ser = ServerCreateSerializer(data=request.data)
        if not ser.is_valid():
            return error(40001, "Invalid parameters", ser.errors)

        server = Server.objects.create(
            project_id=ser.validated_data["project_id"],
            name=ser.validated_data["name"],
            host=ser.validated_data["host"],
            port=ser.validated_data["port"],
            username=ser.validated_data["username"],
            auth_type=ser.validated_data["auth_type"],
        )

        save_server_credentials(
            server,
            password=ser.validated_data.get("password", ""),
            ssh_key=ser.validated_data.get("ssh_key", ""),
        )
        log_action(
            request.user,
            "server.create",
            "server",
            server.id,
            project_id=server.project_id,
            ip_address=client_ip(request),
            detail=ser.validated_data,
        )

        from rest_framework.response import Response
        return Response({"code": 0, "message": "success", "data": ServerSerializer(server).data}, status=201)

    @action(detail=True, methods=["post"])
    def test(self, request, pk=None):
        server = self.get_object()
        creds = get_server_credentials(server)

        executor = SSHExecutor(
            host=server.host,
            port=server.port,
            username=server.username,
            password=creds.get("password", ""),
            pkey=creds.get("ssh_key", ""),
        )
        ok, msg = executor.test_connection()

        if ok:
            server.status = "ACTIVE"
        else:
            server.status = "FAILED"
        server.save(update_fields=["status"])
        log_action(
            request.user,
            "server.test",
            "server",
            server.id,
            project_id=server.project_id,
            ip_address=client_ip(request),
            detail={"success": ok, "message": msg},
        )

        return success({"success": ok, "message": msg})

    @action(detail=True, methods=["post"])
    def detect(self, request, pk=None):
        server = self.get_object()
        creds = get_server_credentials(server)

        executor = SSHExecutor(
            host=server.host,
            port=server.port,
            username=server.username,
            password=creds.get("password", ""),
            pkey=creds.get("ssh_key", ""),
        )

        try:
            commands = {
                "hostname": "hostname",
                "os": "cat /etc/os-release 2>/dev/null | head -1 || uname -a",
                "apptainer": "apptainer --version 2>/dev/null || echo 'not installed'",
                "python": "python3 --version 2>/dev/null || echo 'not installed'",
                "cuda": "nvcc --version 2>/dev/null || echo 'not installed'",
                "disk": "df -h / | tail -1",
            }
            results = {}
            for key, cmd in commands.items():
                code, out, err = executor.run_command(cmd, timeout=10)
                results[key] = out.strip() if code == 0 else err.strip() if err else "detection failed"

            log_action(
                request.user,
                "server.detect",
                "server",
                server.id,
                project_id=server.project_id,
                ip_address=client_ip(request),
                detail={"result_keys": list(results.keys())},
            )
            return success({
                "hostname": results.get("hostname", ""),
                "os": results.get("os", ""),
                "apptainer_version": results.get("apptainer", ""),
                "python_version": results.get("python", ""),
                "cuda_version": results.get("cuda", ""),
                "disk_info": results.get("disk", ""),
            })
        except Exception as e:
            return error(60001, f"服务器环境检测失败：{str(e)}", status=500)

    @action(detail=True, methods=["get", "post"])
    def allowed_dirs(self, request, pk=None):
        server = self.get_object()
        if request.method == "GET":
            dirs = server.allowed_dirs.all()
            return success(ServerAllowedDirSerializer(dirs, many=True).data)

        path = request.data.get("path")
        purpose = request.data.get("purpose", "general")
        if not path:
            return error(40001, "path is required")
        if not validate_workdir(path):
            return error(40001, "Invalid path")
        if purpose not in dict(ServerAllowedDir.PURPOSE_CHOICES):
            return error(40001, "Invalid purpose")

        allowed_dir = server.allowed_dirs.create(path=path, purpose=purpose)
        log_action(
            request.user,
            "server.allowed_dir.create",
            "server_allowed_dir",
            allowed_dir.id,
            project_id=server.project_id,
            ip_address=client_ip(request),
            detail={"server_id": server.id, "path": path, "purpose": purpose},
        )
        return success(ServerAllowedDirSerializer(allowed_dir).data, status=201)

    @action(detail=True, methods=["delete"], url_path=r"allowed_dirs/(?P<dir_id>[^/.]+)")
    def allowed_dir_detail(self, request, pk=None, dir_id=None):
        server = self.get_object()
        try:
            allowed_dir = server.allowed_dirs.get(id=dir_id)
        except ServerAllowedDir.DoesNotExist:
            return error(40401, "Resource not found", status=404)

        detail = {"server_id": server.id, "path": allowed_dir.path, "purpose": allowed_dir.purpose}
        allowed_dir.delete()
        log_action(
            request.user,
            "server.allowed_dir.delete",
            "server_allowed_dir",
            dir_id,
            project_id=server.project_id,
            ip_address=client_ip(request),
            detail=detail,
        )
        return success({})

    @action(detail=True, methods=["post"])
    def collect_metrics(self, request, pk=None):
        """Collect CPU/MEM/GPU/DISK metrics from a server via SSH."""
        server = self.get_object()
        try:
            metrics = collect_server_metrics(server)
            return success(metrics, "Metrics collected")
        except Exception as e:
            return error(60001, f"Failed to collect metrics: {str(e)}", status=500)

    def list(self, request, *args, **kwargs):
        """List servers with their latest metrics."""
        servers = self.get_queryset()
        serializer = ServerSerializer(servers, many=True)

        # Attach latest metric to each server
        server_ids = [s["id"] for s in serializer.data]
        if server_ids:
            all_records = list(
                ServerMetric.objects.filter(server_id__in=server_ids).order_by("-collected_at")
            )
        else:
            all_records = []
        latest_metrics = {}
        seen = set()
        for m in all_records:
            if m.server_id not in seen:
                seen.add(m.server_id)
                latest_metrics[m.server_id] = m

        result = []
        for s in serializer.data:
            item = dict(s)
            metric = latest_metrics.get(s["id"])
            if metric:
                item["metrics"] = {
                    "cpu_percent": metric.cpu_percent,
                    "mem_percent": metric.mem_percent,
                    "mem_used_gb": metric.mem_used_gb,
                    "gpu_percent": metric.gpu_percent,
                    "gpu_mem_percent": metric.gpu_mem_percent,
                    "disk_percent": metric.disk_percent,
                    "disk_used_gb": metric.disk_used_gb,
                    "collected_at": metric.collected_at,
                }
            else:
                item["metrics"] = None
            result.append(item)

        return success(result)
