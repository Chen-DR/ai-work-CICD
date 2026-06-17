import re
from infrastructure.ssh.policy import CommandPolicy


def validate_definition_content(content: str) -> list[str]:
    errors = []
    required_sections = ["Bootstrap:", "From:"]
    for section in required_sections:
        if section not in content:
            errors.append(f"缺少必需字段 {section}")

    # Check for dangerous patterns
    dangerous = [
        "mkfs", "dd if=", "| bash",
        "chmod -R 777", "/etc/shadow", "useradd",
        "passwd", "visudo", "systemctl", "reboot", "shutdown",
    ]
    for pattern in dangerous:
        if pattern in content.lower():
            errors.append(f"包含危险命令片段：{pattern}")

    return errors


def validate_build_params(workdir: str, output_name: str) -> list[str]:
    errors = []
    if not re.match(r"^/[a-zA-Z0-9/._-]+$", workdir):
        errors.append("工作目录格式不正确，必须是合法的绝对路径")
    if ".." in workdir:
        errors.append("工作目录不能包含路径穿越片段 '..'")
    if not re.match(r"^[a-zA-Z0-9._-]+\.sif$", output_name):
        errors.append("输出文件名必须是合法的 .sif 文件名")
    return errors
