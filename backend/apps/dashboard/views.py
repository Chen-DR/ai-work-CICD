"""Dashboard aggregated data API."""

from datetime import timedelta
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django.utils import timezone
from .serializers import ServerHealthSerializer, BuildJobBriefSerializer, BenchmarkJobBriefSerializer, ArtifactBriefSerializer
from .response import success
from apps.servers.models import Server, ServerMetric
from apps.apptainer.models import ApptainerBuildJob
from apps.benchmark.models import BenchmarkJob
from apps.artifacts.models import Artifact


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def dashboard_data(request):
    """Return all dashboard data in one request."""
    now = timezone.now()
    trend_window = now - timedelta(hours=2)

    # ── KPI: online servers ──
    total_servers = Server.objects.count()
    online_servers = Server.objects.filter(status="ACTIVE").count()

    # ── KPI: running tasks (both build + benchmark) ──
    running_build = ApptainerBuildJob.objects.filter(status="RUNNING").count()
    running_benchmark = BenchmarkJob.objects.filter(status="RUNNING").count()
    total_running = running_build + running_benchmark

    # ── KPI: failed tasks ──
    failed_build = ApptainerBuildJob.objects.filter(status="FAILED").count()
    failed_benchmark = BenchmarkJob.objects.filter(status="FAILED").count()
    total_failed = failed_build + failed_benchmark

    # ── KPI: GPU / CPU / storage usage (from latest metrics) ──
    active_servers = list(Server.objects.filter(status="ACTIVE")[:20])
    active_ids = [s.id for s in active_servers]

    if active_ids:
        latest_records = list(
            ServerMetric.objects.filter(server_id__in=active_ids)
            .order_by("-collected_at")
        )
        # Deduplicate: keep latest per server
        seen = set()
        unique_latest = []
        for m in latest_records:
            if m.server_id not in seen:
                seen.add(m.server_id)
                unique_latest.append(m)

        total_cpu = sum(m.cpu_percent for m in unique_latest)
        total_mem = sum(m.mem_percent for m in unique_latest)
        total_gpu = sum(m.gpu_percent for m in unique_latest)
        n = len(unique_latest) or 1
        avg_cpu = round(total_cpu / n)
        avg_mem = round(total_mem / n)
        avg_gpu = round(total_gpu / n)
        total_storage_gb = sum(m.disk_used_gb for m in unique_latest)
    else:
        avg_cpu = avg_mem = avg_gpu = 0
        total_storage_gb = 0

    # ── Time-series: resource trend (last 2 hours, per-server averages) ──
    if active_ids:
        trend_records = list(
            ServerMetric.objects.filter(
                server_id__in=active_ids,
                collected_at__gte=trend_window,
            ).order_by("collected_at")
        )
        # Average across all active servers for each time point
        time_points = {}
        for m in trend_records:
            key = m.collected_at.strftime("%H:%M")
            if key not in time_points:
                time_points[key] = {"cpu": 0, "mem": 0, "gpu": 0, "count": 0}
            time_points[key]["cpu"] += m.cpu_percent
            time_points[key]["mem"] += m.mem_percent
            time_points[key]["gpu"] += m.gpu_percent
            time_points[key]["count"] += 1

        labels = sorted(time_points.keys())
        cpu_data = [round(time_points[k]["cpu"] / time_points[k]["count"]) for k in labels]
        mem_data = [round(time_points[k]["mem"] / time_points[k]["count"]) for k in labels]
        gpu_data = [round(time_points[k]["gpu"] / time_points[k]["count"]) for k in labels]
    else:
        labels = []
        cpu_data = []
        mem_data = []
        gpu_data = []

    # ── Chart: task status distribution (pie) ──
    all_jobs = list(ApptainerBuildJob.objects.values("status")) + list(
        BenchmarkJob.objects.values("status")
    )
    status_counts = {}
    for j in all_jobs:
        status_counts[j["status"]] = status_counts.get(j["status"], 0) + 1
    pie_data = [
        {"name": "运行中", "value": status_counts.get("RUNNING", 0)},
        {"name": "已完成", "value": status_counts.get("SUCCESS", 0)},
        {"name": "失败", "value": status_counts.get("FAILED", 0)},
        {"name": "等待中", "value": status_counts.get("PENDING", 0)},
    ]

    # ── List: server health with metrics ──
    all_servers = list(Server.objects.all()[:20])
    latest_metrics = {}
    if active_ids:
        all_metric_records = list(
            ServerMetric.objects.filter(server_id__in=active_ids)
            .order_by("-collected_at")
        )
        seen = set()
        for m in all_metric_records:
            if m.server_id not in seen:
                seen.add(m.server_id)
                latest_metrics[m.server_id] = m

    servers_data = []
    for s in all_servers:
        sd = ServerHealthSerializer(s).data
        metric = latest_metrics.get(s.id)
        if metric:
            sd["metrics"] = {
                "cpu_percent": metric.cpu_percent,
                "mem_percent": metric.mem_percent,
                "mem_used_gb": round(metric.mem_used_gb, 1),
                "gpu_percent": metric.gpu_percent,
                "gpu_mem_percent": metric.gpu_mem_percent,
                "disk_percent": metric.disk_percent,
                "disk_used_gb": round(metric.disk_used_gb, 1),
                "collected_at": str(metric.collected_at) if metric.collected_at else "",
            }
        else:
            sd["metrics"] = {
                "cpu_percent": 0, "mem_percent": 0, "mem_used_gb": 0,
                "gpu_percent": 0, "gpu_mem_percent": 0,
                "disk_percent": 0, "disk_used_gb": 0,
                "collected_at": "",
            }
        servers_data.append(sd)

    # ── List: failed tasks ──
    failed_builds = BuildJobBriefSerializer(
        ApptainerBuildJob.objects.filter(status="FAILED")[:10], many=True
    ).data
    failed_benchmarks = BenchmarkJobBriefSerializer(
        BenchmarkJob.objects.filter(status="FAILED")[:10], many=True
    ).data

    for j in failed_builds:
        j["type"] = "build"
    for j in failed_benchmarks:
        j["type"] = "benchmark"
    failed_tasks = sorted(
        failed_builds + failed_benchmarks,
        key=lambda x: x["created_at"],
        reverse=True,
    )[:10]

    # ── List: recent reports ──
    reports = ArtifactBriefSerializer(
        Artifact.objects.filter(
            Q(artifact_type="benchmark_report") | Q(artifact_type="build_log")
        )[:10],
        many=True,
    ).data

    for r in reports:
        if r["artifact_type"] == "benchmark_report":
            r["name"] = r["file_name"]
        else:
            r["name"] = f"构建日志: {r['file_name']}"
        size = r["file_size"]
        if size >= 1024 * 1024:
            r["size"] = f"{size / (1024 * 1024):.1f} MB"
        elif size >= 1024:
            r["size"] = f"{size / 1024:.1f} KB"
        else:
            r["size"] = f"{size} B"

    return success({
        "kpi": {
            "total_servers": total_servers,
            "online_servers": online_servers,
            "total_running": total_running,
            "gpu_usage": avg_gpu,
            "cpu_load": avg_cpu,
            "storage_used_gb": round(total_storage_gb),
            "total_failed": total_failed,
        },
        "pie_data": pie_data,
        "servers": servers_data,
        "failed_tasks": failed_tasks,
        "recent_reports": reports,
        "resource_trend": {
            "labels": labels,
            "cpu": cpu_data,
            "mem": mem_data,
            "gpu": gpu_data,
        },
        "bar_trend": {
            "labels": [],
            "data": [],
        },
    })
