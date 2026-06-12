"""Shared validators for AI-Ops platform."""

import re
import os


def validate_host(host: str) -> bool:
    """Validate IP address or hostname."""
    ip_pattern = re.compile(r"^(\d{1,3}\.){3}\d{1,3}$")
    hostname_pattern = re.compile(
        r"^[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?)*$"
    )
    return bool(ip_pattern.match(host)) or bool(hostname_pattern.match(host))


def validate_port(port: int) -> bool:
    """Validate TCP port number."""
    return isinstance(port, int) and 1 <= port <= 65535


def validate_workdir(workdir: str) -> bool:
    """Validate workdir is an absolute path without traversal."""
    if not workdir.startswith("/"):
        return False
    if ".." in workdir.split("/"):
        return False
    return bool(re.match(r"^/[a-zA-Z0-9/._-]+$", workdir))


def validate_filename(name: str) -> bool:
    """Validate filename has no path traversal."""
    return bool(re.match(r"^[a-zA-Z0-9._-]+$", name)) and ".." not in name


def validate_param_value(value: str) -> bool:
    """Check parameter value for dangerous shell characters."""
    forbidden = [";", "&&", "|", "`", "$(", ">", "<", "\n", "\r"]
    return not any(c in str(value) for c in forbidden)


def validate_file_extension(filename: str, allowed_extensions: set) -> bool:
    """Check file extension is in allowed set."""
    ext = os.path.splitext(filename)[1].lower()
    return ext in allowed_extensions
