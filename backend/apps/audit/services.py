from .models import AuditLog


def log_action(
    user,
    action: str,
    resource_type: str,
    resource_id: str = "",
    project_id: int = None,
    ip_address: str = "",
    detail: str = "",
):
    AuditLog.objects.create(
        user=user,
        action=action,
        resource_type=resource_type,
        resource_id=str(resource_id),
        project_id=project_id,
        ip_address=ip_address,
        detail=detail,
    )
