import os
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
    from infrastructure.ssh.guards import validate_safe_command, validate_server_remote_path, validate_server_workdir
    from apps.artifacts.utils import create_artifact
    from .validators import validate_benchmark_params

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

    streamed_chunks: list[str] = []

    def stream_log(line: str):
        normalized = line.replace("\r", "\n")
        streamed_chunks.append(normalized)
        log_line(normalized)

    def append_unstreamed_output(*outputs: str):
        streamed_text = "".join(streamed_chunks)
        for output in outputs:
            if output and output not in streamed_text:
                normalized = output.replace("\r", "\n")
                log_line(normalized if normalized.endswith("\n") else f"{normalized}\n")

    try:
        param_errors = validate_benchmark_params(job.params or {})
        if param_errors:
            raise ValueError("; ".join(param_errors))
        job.workdir = validate_server_workdir(job.server, job.workdir)
        local_script = os.path.join(settings.DATA_ROOT, job.script.storage_path)
        if not os.path.isfile(local_script):
            raise FileNotFoundError(f"Benchmark script not found: {job.script.storage_path}")

        creds = get_server_credentials(job.server)
        password = creds.get("password", "")
        pkey = creds.get("ssh_key", "")
        host = job.server.host
        port = job.server.port
        username = job.server.username

        # Upload script
        job.status = "UPLOADING"
        job.save(update_fields=["status"])

        sftp = SFTPClient(host, port, username, password, pkey)
        if not sftp.mkdir(job.workdir):
            raise RuntimeError(f"Failed to create remote workdir: {job.workdir}")

        remote_script_name = f"benchmark_script_{job.script_id}.sh"
        remote_script = validate_server_remote_path(job.server, os.path.join(job.workdir, remote_script_name))
        if not sftp.upload_file(local_script, remote_script):
            raise RuntimeError(f"Failed to upload benchmark script to: {remote_script}")

        # Execute
        job.status = "RUNNING"
        job.log_path = log_path
        job.save(update_fields=["status", "log_path"])

        params = job.params
        report_file = params.get("report_file", "report.html")
        duration = params.get("duration", 300)
        threads = params.get("threads", 16)

        command = (
            f"cd {job.workdir} && chmod +x {remote_script_name} && "
            f"./{remote_script_name} --duration {duration} --threads {threads} "
            f"--report-file {report_file}"
        )
        validate_safe_command(command)
        log_line(f"Running: {command}\n")

        executor = SSHExecutor(host, port, username, password, pkey)
        exit_code, stdout, stderr = executor.run_command(
            command,
            timeout=3600,
            log_callback=stream_log,
            get_pty=True,
        )
        append_unstreamed_output(stdout, stderr)

        if exit_code != 0:
          raise RuntimeError(f"Benchmark failed: {stderr or stdout.strip()}")

        # Collect report
        job.status = "COLLECTING"
        job.save(update_fields=["status"])

        remote_report = validate_server_remote_path(job.server, os.path.join(job.workdir, report_file))
        if sftp.file_exists(remote_report):
            local_report_dir = os.path.join(
                settings.DATA_ROOT, "artifacts", "benchmark", "reports", f"job_{job_id}"
            )
            os.makedirs(local_report_dir, exist_ok=True)
            local_report_path = os.path.join(local_report_dir, report_file)
            if not sftp.download_file(remote_report, local_report_path):
                raise RuntimeError(f"Failed to download benchmark report from: {remote_report}")
            job.report_path = os.path.join(
                "artifacts", "benchmark", "reports", f"job_{job_id}", report_file
            )
            job.remote_report_path = remote_report
        else:
            raise FileNotFoundError(f"Expected benchmark report not found: {remote_report}")

        job.status = "SUCCESS"
        job.finished_at = timezone.now()
        job.save(update_fields=["status", "report_path", "remote_report_path", "finished_at"])
        create_artifact(
            project_id=job.project_id,
            job_type="benchmark",
            job_id=job.id,
            artifact_type="benchmark_log",
            file_name=os.path.basename(log_path),
            storage_path=log_path,
            local_file=True,
        )
        create_artifact(
            project_id=job.project_id,
            job_type="benchmark",
            job_id=job.id,
            artifact_type="benchmark_report",
            file_name=report_file,
            storage_path=job.report_path,
            local_file=True,
        )
        log_line("Benchmark completed successfully.\n")

    except Exception as e:
        job.status = "FAILED"
        job.error_message = str(e)
        job.finished_at = timezone.now()
        job.save(update_fields=["status", "error_message", "finished_at"])
        log_line(f"Benchmark failed: {str(e)}\n")
        raise
