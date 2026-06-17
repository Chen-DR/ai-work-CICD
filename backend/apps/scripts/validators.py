import os
import re
import shlex
from pathlib import Path

from django.conf import settings


ALLOWED_SCRIPT_EXTENSIONS = {".sh", ".bash", ".py"}
FORBIDDEN_ARG_TOKENS = (";", "&&", "|", "`", "$(", ">", "<", "\n", "\r")
MAX_TIMEOUT_SECONDS = 86400
RUN_AS_PATTERN = re.compile(r"^[a-z_][a-z0-9_-]{0,31}$")


def script_language(file_name: str) -> str:
    ext = os.path.splitext(file_name)[1].lower()
    if ext == ".py":
        return "python"
    return "shell"


def validate_script_file(file) -> None:
    ext = os.path.splitext(file.name)[1].lower()
    if ext not in ALLOWED_SCRIPT_EXTENSIONS:
        raise ValueError("仅允许上传 .sh、.bash、.py 脚本文件")


def allowed_cwd_roots() -> list[Path]:
    roots = getattr(settings, "SCRIPT_ALLOWED_CWDS", ["/opt", "/home"])
    return [Path(root).expanduser().resolve() for root in roots]


def validate_cwd(cwd: str) -> str:
    if not cwd or not cwd.strip():
        raise ValueError("目标目录不能为空")
    path = Path(cwd).expanduser().resolve()
    if not path.is_dir():
        raise ValueError("目标目录不存在或不是目录")
    for root in allowed_cwd_roots():
        if path == root or root in path.parents:
            return str(path)
    allowed = "、".join(str(root) for root in allowed_cwd_roots())
    raise ValueError(f"目标目录不在允许范围内：{allowed}")


def parse_args(args: str) -> list[str]:
    args = (args or "").strip()
    if not args:
        return []
    if len(args) > 1024:
        raise ValueError("执行参数过长")
    if any(token in args for token in FORBIDDEN_ARG_TOKENS):
        raise ValueError("执行参数包含不允许的 shell 特殊字符")
    try:
        return shlex.split(args)
    except ValueError as exc:
        raise ValueError(f"执行参数格式错误：{exc}") from exc


def validate_run_as(run_as: str | None) -> str:
    value = (run_as or "").strip()
    if not value:
        return ""
    if not RUN_AS_PATTERN.fullmatch(value):
        raise ValueError("执行用户只能包含小写字母、数字、下划线和短横线，且必须以字母或下划线开头")
    return value


def validate_server_run_as(server, run_as: str | None) -> str:
    value = validate_run_as(run_as)
    if value == "root" and not getattr(server, "allow_script_root", False):
        raise ValueError("该服务器未开启脚本 root 执行权限")
    return value


def validate_timeout(timeout: int | None) -> int:
    value = int(timeout or getattr(settings, "SCRIPT_DEFAULT_TIMEOUT", 3600))
    if value <= 0 or value > MAX_TIMEOUT_SECONDS:
        raise ValueError(f"超时时间必须在 1 到 {MAX_TIMEOUT_SECONDS} 秒之间")
    return value
