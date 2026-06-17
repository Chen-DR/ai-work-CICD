import json
import os
import posixpath
import re
import shlex
from datetime import datetime

from celery import shared_task
from django.conf import settings
from django.utils import timezone

from apps.artifacts.models import Artifact
from apps.artifacts.utils import create_artifact
from .models import ScriptExecutionTask
from .services import ScriptService
from .validators import parse_args, validate_server_run_as
from apps.servers.services import get_server_credentials
from infrastructure.ssh.executor import CommandCancelledError, SSHExecutor
from infrastructure.ssh.guards import validate_safe_command, validate_server_remote_path, validate_server_workdir
from infrastructure.ssh.policy import CommandPolicy
from infrastructure.ssh.sftp import SFTPClient


REMOTE_OUTPUT_EXTENSIONS = {
    ".txt", ".log", ".out", ".err", ".json", ".csv", ".tsv", ".yaml", ".yml",
    ".xml", ".html", ".md", ".report",
}


def _event(kind: str, **payload) -> str:
    data = {"type": kind, "ts": datetime.now().strftime("%H:%M:%S"), **payload}
    return json.dumps(data, ensure_ascii=False) + "\n"


def _append_event(path: str, kind: str, **payload) -> None:
    with open(path, "a", encoding="utf-8") as f:
        f.write(_event(kind, **payload))


def _extract_remote_output_paths(text: str) -> list[str]:
    paths: list[str] = []
    seen: set[str] = set()
    for match in re.finditer(r"(?<![A-Za-z0-9_])(/[A-Za-z0-9._~+\-/]+)", text or ""):
        path = match.group(1).rstrip("。；;，,)")
        ext = os.path.splitext(path)[1].lower()
        if ext not in REMOTE_OUTPUT_EXTENSIONS:
            continue
        if path not in seen:
            seen.add(path)
            paths.append(path)
    return paths


def _register_script_log_artifact(task: ScriptExecutionTask, log_path: str) -> None:
    if not log_path:
        return
    if Artifact.objects.filter(
        project_id=task.project_id,
        job_type="script_execution",
        artifact_type="script_log",
        storage_path=log_path,
    ).exists():
        return
    create_artifact(
        project_id=task.project_id,
        job_type="script_execution",
        job_id=None,
        artifact_type="script_log",
        file_name=os.path.basename(log_path),
        storage_path=log_path,
        local_file=True,
    )


def _collect_script_output_artifacts(
    *,
    task: ScriptExecutionTask,
    sftp: SFTPClient,
    output_text: str,
) -> None:
    local_dir = os.path.join(settings.DATA_ROOT, "artifacts", "scripts", "outputs", str(task.task_id))
    storage_dir = os.path.join("artifacts", "scripts", "outputs", str(task.task_id))
    os.makedirs(local_dir, exist_ok=True)

    for remote_path in _extract_remote_output_paths(output_text):
        try:
            safe_remote_path = validate_server_remote_path(task.server, remote_path)
        except PermissionError:
            continue
        if not sftp.file_exists(safe_remote_path):
            continue

        file_name = os.path.basename(safe_remote_path)
        local_path = os.path.join(local_dir, file_name)
        storage_path = os.path.join(storage_dir, file_name)
        if not os.path.exists(local_path) and not sftp.download_file(safe_remote_path, local_path):
            continue
        if Artifact.objects.filter(
            project_id=task.project_id,
            job_type="script_execution",
            artifact_type="script_output",
            storage_path=storage_path,
        ).exists():
            continue
        create_artifact(
            project_id=task.project_id,
            job_type="script_execution",
            job_id=None,
            artifact_type="script_output",
            file_name=file_name,
            storage_path=storage_path,
            local_file=True,
        )


def _command_for_script(script_path: str, language: str, args: list[str], run_as: str = "") -> list[str]:
    if language == "python":
        command = ["python3", script_path, *args]
    else:
        command = ["bash", script_path, *args]
    if run_as:
        return ["sudo", "-n", "-u", run_as, "--", *command]
    return command


def _remote_script_name(task: ScriptExecutionTask) -> str:
    file_name = os.path.basename(task.script.file_name)
    if re.fullmatch(r"[A-Za-z0-9._-]+", file_name):
        return file_name
    ext = os.path.splitext(file_name)[1].lower() or ".sh"
    return f"script_{task.script_id}{ext}"


def _remote_command(
    workdir: str,
    remote_script_name: str,
    language: str,
    args: list[str],
    run_as: str = "",
) -> tuple[str, list[str]]:
    command_list = _command_for_script(f"./{remote_script_name}", language, args, run_as)
    runner = " ".join(shlex.quote(item) for item in command_list)
    command = f"cd {shlex.quote(workdir)} && {runner}"
    return command, command_list


@shared_task(bind=True, name="apps.scripts.tasks.run_script_task")
def run_script_task(self, task_id: str):
    task = ScriptExecutionTask.objects.select_related("script", "server").get(task_id=task_id)
    log_path = os.path.join("logs", "jobs", f"script_task_{task_id}.jsonl")
    full_log_path = os.path.join(settings.DATA_ROOT, log_path)
    os.makedirs(os.path.dirname(full_log_path), exist_ok=True)

    task.status = "RUNNING"
    task.started_at = timezone.now()
    task.log_path = log_path
    task.save(update_fields=["status", "started_at", "log_path"])

    try:
        if not task.server:
            raise ValueError("未指定目标服务器")
        if not CommandPolicy.is_allowed_action("script_run"):
            raise PermissionError("Script run action is not allowed")

        script_path = ScriptService().script_full_path(task.script)
        if not os.path.isfile(script_path):
            raise FileNotFoundError("脚本文件不存在")

        args = parse_args(task.args)
        run_as = validate_server_run_as(task.server, task.run_as)
        task.cwd = validate_server_workdir(task.server, task.cwd, {"script", "general"})

        creds = get_server_credentials(task.server)
        password = creds.get("password", "")
        pkey = creds.get("ssh_key", "")
        host = task.server.host
        port = task.server.port
        username = task.server.username

        remote_script_name = _remote_script_name(task)
        remote_script = validate_server_remote_path(task.server, posixpath.join(task.cwd, remote_script_name))
        _append_event(
            full_log_path,
            "meta",
            line=f"Uploading script to {task.server.name}: {remote_script}",
            cwd=task.cwd,
            run_as=run_as or username,
        )

        sftp = SFTPClient(host, port, username, password, pkey)
        if not sftp.mkdir(task.cwd):
            raise RuntimeError(f"无法创建远程工作目录：{task.cwd}")
        if not sftp.upload_file(script_path, remote_script):
            raise RuntimeError(f"脚本上传失败：{remote_script}")

        effective_run_as = run_as if run_as and run_as != username else ""
        command, command_list = _remote_command(task.cwd, remote_script_name, task.script.language, args, effective_run_as)
        validate_safe_command(command)
        _append_event(
            full_log_path,
            "meta",
            line=f"Running on {task.server.name}: {command}",
            command=command_list,
            cwd=task.cwd,
            run_as=run_as or username,
        )

        streamed_chunks: list[str] = []

        def stream_stdout(chunk: str):
            normalized = chunk.replace("\r", "\n")
            streamed_chunks.append(normalized)
            for line in normalized.splitlines():
                _append_event(full_log_path, "stdout", line=line)

        def stream_stderr(chunk: str):
            normalized = chunk.replace("\r", "\n")
            streamed_chunks.append(normalized)
            for line in normalized.splitlines():
                _append_event(full_log_path, "stderr", line=line)

        def append_unstreamed_output(kind: str, *outputs: str):
            streamed_text = "".join(streamed_chunks)
            for output in outputs:
                if not output or output in streamed_text:
                    continue
                for line in output.replace("\r", "\n").splitlines():
                    _append_event(full_log_path, kind, line=line)

        def should_stop():
            task.refresh_from_db(fields=["status"])
            return task.status == "CANCELLED"

        executor = SSHExecutor(host, port, username, password, pkey)
        try:
            exit_code, stdout, stderr = executor.run_command(
                command,
                timeout=task.timeout,
                log_callback=stream_stdout,
                stderr_callback=stream_stderr,
                get_pty=False,
                stop_callback=should_stop,
            )
            append_unstreamed_output("stdout", stdout)
            append_unstreamed_output("stderr", stderr)
        except TimeoutError:
            task.status = "TIMEOUT"
            task.exit_code = -1
            task.error_message = f"脚本执行超过 {task.timeout} 秒"
            _append_event(full_log_path, "stderr", line=task.error_message)
            exit_code = -1
        except CommandCancelledError:
            task.status = "CANCELLED"
            task.exit_code = -1
            task.error_message = "脚本执行已终止"
            _append_event(full_log_path, "stderr", line=task.error_message)
            exit_code = -1

        task.exit_code = exit_code
        if task.status in ("CANCELLED", "TIMEOUT"):
            pass
        elif exit_code == 0:
            task.status = "SUCCESS"
        else:
            task.status = "FAILED"
            task.error_message = f"脚本执行失败，退出码 {exit_code}"
        task.finished_at = timezone.now()
        task.process_id = None
        task.save(update_fields=["status", "exit_code", "error_message", "finished_at", "process_id"])
        _register_script_log_artifact(task, log_path)
        _collect_script_output_artifacts(
            task=task,
            sftp=sftp,
            output_text="\n".join(streamed_chunks + [stdout or "", stderr or ""]),
        )
        _append_event(full_log_path, "exit", code=task.exit_code)
    except Exception as exc:
        task.status = "FAILED"
        task.error_message = str(exc)
        task.finished_at = timezone.now()
        task.process_id = None
        task.save(update_fields=["status", "error_message", "finished_at", "process_id"])
        _register_script_log_artifact(task, log_path)
        _append_event(full_log_path, "stderr", line=str(exc))
        _append_event(full_log_path, "exit", code=-1)
        raise
