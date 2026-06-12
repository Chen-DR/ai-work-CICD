import json
from .models import AuditLog

SENSITIVE_KEYS = ("password", "token", "secret", "private_key", "ssh_key", "credential", "key")


def client_ip(request) -> str:
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "")


def redact_detail(value):
    if isinstance(value, dict):
        redacted = {}
        for key, item in value.items():
            if any(sensitive in str(key).lower() for sensitive in SENSITIVE_KEYS):
                redacted[key] = "***REDACTED***"
            else:
                redacted[key] = redact_detail(item)
        return redacted
    if isinstance(value, list):
        return [redact_detail(item) for item in value]
    return value


def log_action(
    user,
    action: str,
    resource_type: str,
    resource_id: str = "",
    project_id: int = None,
    ip_address: str = "",
    detail=None,
):
    AuditLog.objects.create(
        user=user if getattr(user, "is_authenticated", False) else None,
        action=action,
        resource_type=resource_type,
        resource_id=str(resource_id),
        project_id=project_id,
        ip_address=ip_address,
        detail=json.dumps(redact_detail(detail or {}), ensure_ascii=False),
    )
