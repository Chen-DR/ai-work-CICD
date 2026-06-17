import os

ALLOWED_ACTIONS = {
    "apptainer_build",
    "apptainer_test",
    "benchmark_run",
    "script_run",
    "collect_report",
    "cleanup_workdir",
    "detect_environment",
}

DANGEROUS_PATTERNS = [
    "rm -rf /",
    "mkfs",
    "dd if=",
    "| bash",
    "curl",
    "wget",
    "/etc/shadow",
    "useradd",
    "passwd",
    "visudo",
    "systemctl",
    "reboot",
    "shutdown",
    ":(){ :|:& };:",
]


class CommandPolicy:
    @staticmethod
    def is_allowed_action(action: str) -> bool:
        return action in ALLOWED_ACTIONS

    @staticmethod
    def is_safe_command(command: str) -> bool:
        lower = command.lower()
        for pattern in DANGEROUS_PATTERNS:
            if pattern in lower:
                return False
        return True

    @staticmethod
    def validate_param_value(value: str) -> bool:
        forbidden = [";", "&&", "|", "`", "$(", ">"]
        return not any(c in str(value) for c in forbidden)

    @staticmethod
    def is_allowed_workdir(workdir: str, allowed_dirs: list[str]) -> bool:
        normalized = os.path.abspath(workdir)
        return any(normalized.startswith(os.path.abspath(base)) for base in allowed_dirs)
