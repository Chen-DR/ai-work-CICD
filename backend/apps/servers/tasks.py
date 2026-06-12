"""Celery tasks for server metrics collection."""

import logging
from celery import shared_task

from .metrics import collect_all_servers_metrics

logger = logging.getLogger(__name__)


@shared_task(name="servers.collect_metrics")
def collect_metrics_task():
    """Periodically collect metrics from all ACTIVE servers.

    Runs via Celery Beat every 30 seconds.
    """
    logger.info("Starting periodic metrics collection...")
    results = collect_all_servers_metrics()
    collected = sum(1 for r in results if r["metrics"]["cpu_percent"] > 0 or r["metrics"]["mem_percent"] > 0)
    logger.info("Metrics collection complete: %d/%d servers responded", collected, len(results))
    return {"collected": collected, "total": len(results)}
