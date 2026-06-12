"""Collect server resource metrics via SSH."""

import logging
import re

from .models import Server, ServerMetric
from .services import get_server_credentials
from infrastructure.ssh.executor import SSHExecutor

logger = logging.getLogger(__name__)

# Shell commands for collecting metrics
METRIC_CMDS = {
    "cpu": "top -bn1 | grep 'Cpu(s)' | awk '{print $2}' 2>/dev/null || mpstat 1 1 2>/dev/null | awk '/Average/ {print 100 - $NF}'",
    "mem": "free -b | awk '/Mem:/ {printf \"%.1f %.1f %.1f\", $3/$2*100, $3/1024/1024/1024, $2/1024/1024/1024}'",
    "gpu": "nvidia-smi --query-gpu=utilization.gpu,memory.used,memory.total --format=csv,noheader,nounits 2>/dev/null || echo ''",
    "disk": "df -BG / | awk 'NR==2 {gsub(/G/,\"\"); printf \"%.1f %.1f %.1f\", $5, $3, $2}'",
}


def collect_server_metrics(server: Server) -> dict:
    """SSH into a server and collect CPU/MEM/GPU/DISK metrics.

    Returns dict with metric values or defaults on failure.
    """
    creds = get_server_credentials(server)

    executor = SSHExecutor(
        host=server.host,
        port=server.port,
        username=server.username,
        password=creds.get("password", ""),
        pkey=creds.get("ssh_key", ""),
        timeout=30,
    )

    metrics = {
        "cpu_percent": 0,
        "mem_percent": 0,
        "mem_used_gb": 0,
        "mem_total_gb": 0,
        "gpu_percent": 0,
        "gpu_mem_percent": 0,
        "disk_percent": 0,
        "disk_used_gb": 0,
        "disk_total_gb": 0,
    }

    try:
        # CPU
        code, out, err = executor.run_command(METRIC_CMDS["cpu"], timeout=15)
        if code == 0 and out.strip():
            try:
                metrics["cpu_percent"] = float(out.strip().split()[0])
            except (ValueError, IndexError):
                pass

        # Memory
        code, out, err = executor.run_command(METRIC_CMDS["mem"], timeout=10)
        if code == 0 and out.strip():
            parts = out.strip().split()
            if len(parts) >= 3:
                metrics["mem_percent"] = float(parts[0])
                metrics["mem_used_gb"] = float(parts[1])
                metrics["mem_total_gb"] = float(parts[2])

        # GPU
        code, out, err = executor.run_command(METRIC_CMDS["gpu"], timeout=10)
        if code == 0 and out.strip():
            parts = out.strip().split(",")
            if len(parts) >= 3:
                metrics["gpu_percent"] = float(parts[0].strip())
                try:
                    gpu_mem_used = float(parts[1].strip())
                    gpu_mem_total = float(parts[2].strip())
                    metrics["gpu_mem_percent"] = (gpu_mem_used / gpu_mem_total * 100) if gpu_mem_total > 0 else 0
                except (ValueError, ZeroDivisionError):
                    pass

        # Disk
        code, out, err = executor.run_command(METRIC_CMDS["disk"], timeout=10)
        if code == 0 and out.strip():
            parts = out.strip().split()
            if len(parts) >= 3:
                metrics["disk_percent"] = float(parts[0])
                metrics["disk_used_gb"] = float(parts[1])
                metrics["disk_total_gb"] = float(parts[2])

        # Save to DB
        ServerMetric.objects.create(server=server, **metrics)
        logger.info("Collected metrics for %s", server.name)

    except Exception as e:
        logger.error("Failed to collect metrics for %s: %s", server.name, e)
        # Don't save failed metrics; return defaults

    return metrics


def collect_all_servers_metrics() -> list[dict]:
    """Collect metrics from all ACTIVE servers.

    Returns list of (server, metrics) tuples.
    """
    results = []
    for server in Server.objects.filter(status="ACTIVE"):
        try:
            metrics = collect_server_metrics(server)
            results.append({"server": server, "metrics": metrics})
        except Exception as e:
            logger.error("Failed to collect metrics for %s: %s", server.name, e)
    return results
