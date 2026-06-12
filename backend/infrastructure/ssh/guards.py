from infrastructure.ssh.path_utils import is_subpath, normalize_remote_path
from infrastructure.ssh.policy import CommandPolicy


def allowed_dirs_for_server(server) -> list[str]:
    return [item.path for item in server.allowed_dirs.all()]


def validate_server_workdir(server, workdir: str) -> str:
    normalized = normalize_remote_path(workdir)
    allowed_dirs = allowed_dirs_for_server(server)
    if not allowed_dirs:
        raise PermissionError("Server has no allowed directories configured")
    if not any(is_subpath(normalized, base) for base in allowed_dirs):
        raise PermissionError("Workdir not in server allowed directories")
    return normalized


def validate_server_remote_path(server, path: str) -> str:
    normalized = normalize_remote_path(path)
    allowed_dirs = allowed_dirs_for_server(server)
    if not allowed_dirs:
        raise PermissionError("Server has no allowed directories configured")
    if not any(is_subpath(normalized, base) for base in allowed_dirs):
        raise PermissionError("Remote path not in server allowed directories")
    return normalized


def validate_safe_command(command: str):
    if not CommandPolicy.is_safe_command(command):
        raise PermissionError("Command rejected by policy")


def validate_command_value(value: str, label: str):
    if not CommandPolicy.validate_param_value(value):
        raise PermissionError(f"{label} contains dangerous characters")
