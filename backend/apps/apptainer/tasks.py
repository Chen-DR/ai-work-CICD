import os
import logging
from celery import shared_task
from django.utils import timezone
from django.conf import settings

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=2)
def run_apptainer_build_task(self, job_id):
    from .models import ApptainerBuildJob
    from apps.servers.services import get_server_credentials
    from infrastructure.ssh.executor import SSHExecutor
    from infrastructure.ssh.sftp import SFTPClient
    from infrastructure.ssh.guards import validate_safe_command, validate_server_remote_path, validate_server_workdir
    from infrastructure.security.encryptor import decrypt
    from apps.artifacts.utils import create_artifact
    from .validators import validate_build_params

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
        param_errors = validate_build_params(job.workdir, job.output_name)
        if param_errors:
            raise ValueError("; ".join(param_errors))
        job.workdir = validate_server_workdir(job.server, job.workdir)
        if not job.definition.storage_path:
            raise FileNotFoundError("Definition file storage_path is empty")
        local_def_path = os.path.join(settings.DATA_ROOT, job.definition.storage_path)
        if not os.path.isfile(local_def_path):
            raise FileNotFoundError(f"Definition file not found: {job.definition.storage_path}")

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
        if not sftp.mkdir(job.workdir):
            raise RuntimeError(f"Failed to create remote workdir: {job.workdir}")

        remote_def_name = f"definition_{job.definition_id}.def"
        remote_def_path = validate_server_remote_path(job.server, os.path.join(job.workdir, remote_def_name))
        if not sftp.upload_file(local_def_path, remote_def_path):
            raise RuntimeError(f"Failed to upload definition to: {remote_def_path}")

        # Execute build
        job.status = "RUNNING"
        job.log_path = log_path
        job.save(update_fields=["status", "log_path"])

        command = f"cd {job.workdir} && apptainer build {job.output_name} {remote_def_name}"
        validate_safe_command(command)
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

        remote_sif = validate_server_remote_path(job.server, os.path.join(job.workdir, job.output_name))
        if sftp.file_exists(remote_sif):
            job.remote_output_path = remote_sif
        else:
            raise FileNotFoundError(f"Expected SIF output not found: {remote_sif}")

        job.status = "SUCCESS"
        job.finished_at = timezone.now()
        job.save(update_fields=["status", "remote_output_path", "finished_at"])
        create_artifact(
            project_id=job.project_id,
            job_type="apptainer_build",
            job_id=job.id,
            artifact_type="sif_path_record",
            file_name=job.output_name,
            storage_path=job.remote_output_path,
            local_file=False,
        )
        create_artifact(
            project_id=job.project_id,
            job_type="apptainer_build",
            job_id=job.id,
            artifact_type="build_log",
            file_name=os.path.basename(log_path),
            storage_path=log_path,
            local_file=True,
        )
        log_line("Build completed successfully.\n")

    except Exception as e:
        job.status = "FAILED"
        job.error_message = str(e)
        job.finished_at = timezone.now()
        job.save(update_fields=["status", "error_message", "finished_at"])
        log_line(f"Build failed: {str(e)}\n")
        raise
