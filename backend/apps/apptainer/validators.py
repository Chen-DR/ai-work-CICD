import re
from infrastructure.ssh.policy import CommandPolicy


def validate_definition_content(content: str) -> list[str]:
    errors = []
    required_sections = ["Bootstrap:", "From:"]
    for section in required_sections:
        if section not in content:
            errors.append(f"Missing required section: {section}")

    # Check for dangerous patterns
    dangerous = [
        "rm -rf /", "mkfs", "dd if=", "| bash",
        "chmod -R 777", "/etc/shadow", "useradd",
        "passwd", "visudo", "systemctl", "reboot", "shutdown",
    ]
    for pattern in dangerous:
        if pattern in content.lower():
            errors.append(f"Contains dangerous pattern: {pattern}")

    return errors


def validate_build_params(workdir: str, output_name: str) -> list[str]:
    errors = []
    if not re.match(r"^/[a-zA-Z0-9/._-]+$", workdir):
        errors.append("Invalid workdir format")
    if ".." in workdir:
        errors.append("Path traversal detected in workdir")
    if not re.match(r"^[a-zA-Z0-9._-]+\.sif$", output_name):
        errors.append("Output name must be a valid .sif filename")
    return errors
