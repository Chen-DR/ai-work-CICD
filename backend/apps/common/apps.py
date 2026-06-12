from django.apps import AppConfig
from django.db.models.signals import post_migrate


def enable_sqlite_wal(sender, **kwargs):
    """Enable SQLite WAL mode only when the active database is SQLite."""
    from django.db import connection
    if connection.vendor != "sqlite":
        return
    try:
        with connection.cursor() as cursor:
            cursor.execute("PRAGMA journal_mode=WAL;")
            cursor.execute("PRAGMA synchronous=NORMAL;")
            cursor.execute("PRAGMA busy_timeout=30000;")
    except Exception:
        pass


class CommonConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.common"

    def ready(self):
        post_migrate.connect(enable_sqlite_wal, sender=self)
