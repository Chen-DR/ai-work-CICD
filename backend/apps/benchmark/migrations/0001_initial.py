from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True
    dependencies = [
        ("projects", "0001_initial"),
        ("servers", "0001_initial"),
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.CreateModel(
            name="BenchmarkScript",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=256)),
                ("script_type", models.CharField(choices=[("cpu", "CPU"), ("disk", "Disk"), ("gpu", "GPU"), ("mixed", "Mixed"), ("custom", "Custom")], max_length=32)),
                ("version", models.CharField(default="v1", max_length=64)),
                ("file_name", models.CharField(max_length=256)),
                ("storage_path", models.CharField(max_length=512)),
                ("description", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("created_by", models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to="auth.user")),
                ("project", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="benchmark_scripts", to="projects.project")),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="BenchmarkJob",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("workdir", models.CharField(max_length=512)),
                ("params", models.JSONField(default=dict)),
                ("status", models.CharField(choices=[("PENDING", "Pending"), ("VALIDATING", "Validating"), ("UPLOADING", "Uploading"), ("RUNNING", "Running"), ("COLLECTING", "Collecting"), ("SUCCESS", "Success"), ("FAILED", "Failed"), ("CANCELLED", "Cancelled"), ("TIMEOUT", "Timeout")], default="PENDING", max_length=32)),
                ("celery_task_id", models.CharField(blank=True, max_length=128)),
                ("log_path", models.CharField(blank=True, max_length=512)),
                ("report_path", models.CharField(blank=True, max_length=512)),
                ("remote_report_path", models.CharField(blank=True, max_length=512)),
                ("error_message", models.TextField(blank=True)),
                ("started_at", models.DateTimeField(blank=True, null=True)),
                ("finished_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("created_by", models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to="auth.user")),
                ("project", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="benchmark_jobs", to="projects.project")),
                ("script", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="benchmark.benchmarkscript")),
                ("server", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="servers.server")),
            ],
            options={"ordering": ["-created_at"]},
        ),
    ]
