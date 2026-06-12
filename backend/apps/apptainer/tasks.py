import os
import logging
from celery import shared_task
from django.utils import timezone
from django.conf import settings
from apps.common.response import success

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=2)
def run_apptainer_build_task(self, job_id):
    from .models import ApptainerBuildJob
    from apps.servers.models import Server
    from apps.servers.services import get_server_credentials
    from infrastructure.ssh.executor import SSHExecutor
    from infrastructure.ssh.sftp import SFTPClient
    from infrastructure.ssh.policy import CommandPolicy
    from infrastructure.security.encryptor import decrypt

    job = ApptainerBuildJob.objects.select_related("definition", "server").get(id=job_id)
    job.status = "VALIDATING"
    job.started_at = timezone.now()
    job.save(update_fields=["status", "started_at"])

    log_path = os.path.join("logs", "jobs", f"apptainer_build_{job_id}.log")
    full_log_path = os.path.join(settings.DATA_ROOT, log_path)
    os.makedirs(os.path.dirname(full_log_path), exist_ok=True)

    def log_line(line: str):
        with open(full_log_path, "a") as f:
            f.write(line)

    try:
        # Validate
        if not CommandPolicy.is_allowed_workdir(job.workdir, ["/data", "/home", "/tmp"]):
            raise PermissionError("Workdir not in allowed directories")

        creds = get_server_credentials(job.server)
        password = decrypt(creds["password"]) if creds.get("password") else ""
        pkey = decrypt(creds.get("ssh_key", "")) if creds.get("ssh_key") else ""

        host = job.server.host
        port = job.server.port
        username = job.server.username

        # Upload definition file
        job.status = "UPLOADING"
        job.save(update_fields=["status"])

        sftp = SFTPClient(host, port, username, password, pkey)
        sftp.mkdir(job.workdir)

        local_def_path = os.path.join(settings.DATA_ROOT, job.definition.storage_path)
        remote_def_path = os.path.join(job.workdir, f"{job.definition.name}.def")
        sftp.upload_file(local_def_path, remote_def_path)

        # Execute build
        job.status = "RUNNING"
        job.log_path = log_path
        job.save(update_fields=["status", "log_path"])

        command = f"cd {job.workdir} && apptainer build {job.output_name} {job.definition.name}.def"
        log_line(f"Running: {command}\n")

        executor = SSHExecutor(host, port, username, password, pkey)
        exit_code, stdout, stderr = executor.run_command(
            command,
            timeout=3600,
            log_callback=lambda line: log_line(line),
        )

        if exit_code != 0:
              raise RuntimeError(f"Build failed with exit code {exit_code}: {stderr or stdout.strip()}")

        # Check output
        job.status = "COLLECTING"
        job.save(update_fields=["status"])

        remote_sif = os.path.join(job.workdir, job.output_name)
        if sftp.file_exists(remote_sif):
            job.remote_output_path = remote_sif

        job.status = "SUCCESS"
        job.finished_at = timezone.now()
        job.save(update_fields=["status", "remote_output_path", "finished_at"])
        log_line("Build completed successfully.\n")

    except Exception as e:
        job.status = "FAILED"
        job.error_message = str(e)
        job.finished_at = timezone.now()
        job.save(update_fields=["status", "error_message", "finished_at"])
        log_line(f"Build failed: {str(e)}\n")
        raise
