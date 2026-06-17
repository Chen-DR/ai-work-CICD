# Generated manually for scripts module.

import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("projects", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="ScriptFile",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=256)),
                ("file_name", models.CharField(max_length=256)),
                ("storage_path", models.CharField(max_length=512)),
                ("description", models.TextField(blank=True)),
                ("language", models.CharField(choices=[("shell", "Shell"), ("python", "Python")], default="shell", max_length=32)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("created_by", models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ("project", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="managed_scripts", to="projects.project")),
            ],
            options={"ordering": ["-updated_at"]},
        ),
        migrations.CreateModel(
            name="ScriptExecutionTask",
            fields=[
                ("task_id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("cwd", models.CharField(max_length=512)),
                ("args", models.CharField(blank=True, max_length=1024)),
                ("timeout", models.PositiveIntegerField(default=3600)),
                ("status", models.CharField(choices=[("PENDING", "Pending"), ("RUNNING", "Running"), ("SUCCESS", "Success"), ("FAILED", "Failed"), ("CANCELLED", "Cancelled"), ("TIMEOUT", "Timeout")], default="PENDING", max_length=32)),
                ("celery_task_id", models.CharField(blank=True, max_length=128)),
                ("log_path", models.CharField(blank=True, max_length=512)),
                ("exit_code", models.IntegerField(blank=True, null=True)),
                ("process_id", models.IntegerField(blank=True, null=True)),
                ("error_message", models.TextField(blank=True)),
                ("started_at", models.DateTimeField(blank=True, null=True)),
                ("finished_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("created_by", models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ("project", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="script_tasks", to="projects.project")),
                ("script", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="tasks", to="scripts.scriptfile")),
            ],
            options={"ordering": ["-created_at"]},
        ),
    ]
