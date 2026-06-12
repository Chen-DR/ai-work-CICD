import os
import json
import logging
from celery import shared_task
from django.utils import timezone
from django.conf import settings

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=2)
def run_benchmark_job_task(self, job_id):
    from .models import BenchmarkJob
    from apps.servers.services import get_server_credentials
    from infrastructure.ssh.executor import SSHExecutor
    from infrastructure.ssh.sftp import SFTPClient
    from infrastructure.security.encryptor import decrypt

    job = BenchmarkJob.objects.select_related("script", "server").get(id=job_id)
    job.status = "VALIDATING"
    job.started_at = timezone.now()
    job.save(update_fields=["status", "started_at"])

    log_path = os.path.join("logs", "jobs", f"benchmark_{job_id}.log")
    full_log_path = os.path.join(settings.DATA_ROOT, log_path)
    os.makedirs(os.path.dirname(full_log_path), exist_ok=True)

    def log_line(line: str):
        with open(full_log_path, "a") as f:
            f.write(line)

    try:
        creds = get_server_credentials(job.server)
        password = decrypt(creds["password"]) if creds.get("password") else ""
        pkey = decrypt(creds.get("ssh_key", "")) if creds.get("ssh_key") else ""
        host = job.server.host
        port = job.server.port
        username = job.server.username

        # Upload script
        job.status = "UPLOADING"
        job.save(update_fields=["status"])

        sftp = SFTPClient(host, port, username, password, pkey)
        sftp.mkdir(job.workdir)

        local_script = os.path.join(settings.DATA_ROOT, job.script.storage_path)
        remote_script = os.path.join(job.workdir, job.script.file_name)
        sftp.upload_file(local_script, remote_script)

        # Execute
        job.status = "RUNNING"
        job.log_path = log_path
        job.save(update_fields=["status", "log_path"])

        params = job.params
        report_file = params.get("report_file", "report.html")
        duration = params.get("duration", 300)
        threads = params.get("threads", 16)

        command = (
            f"cd {job.workdir} && chmod +x {job.script.file_name} && "
            f"./{job.script.file_name} --duration {duration} --threads {threads} "
            f"--report-file {report_file}"
        )
        log_line(f"Running: {command}\n")

        executor = SSHExecutor(host, port, username, password, pkey)
        exit_code, stdout, stderr = executor.run_command(
            command, timeout=3600, log_callback=lambda l: log_line(l)
        )

        if exit_code != 0:
          raise RuntimeError(f"Benchmark failed: {stderr or stdout.strip()}")

        # Collect report
        job.status = "COLLECTING"
        job.save(update_fields=["status"])

        remote_report = os.path.join(job.workdir, report_file)
        if sftp.file_exists(remote_report):
            local_report_dir = os.path.join(
                settings.DATA_ROOT, "artifacts", "benchmark", "reports", f"job_{job_id}"
            )
            os.makedirs(local_report_dir, exist_ok=True)
            local_report_path = os.path.join(local_report_dir, report_file)
            sftp.download_file(remote_report, local_report_path)
            job.report_path = os.path.join(
                "artifacts", "benchmark", "reports", f"job_{job_id}", report_file
            )
            job.remote_report_path = remote_report

        job.status = "SUCCESS"
        job.finished_at = timezone.now()
        job.save(update_fields=["status", "report_path", "remote_report_path", "finished_at"])
        log_line("Benchmark completed successfully.\n")

    except Exception as e:
        job.status = "FAILED"
        job.error_message = str(e)
        job.finished_at = timezone.now()
        job.save(update_fields=["status", "error_message", "finished_at"])
        log_line(f"Benchmark failed: {str(e)}\n")
        raise
