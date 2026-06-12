from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True
    dependencies = [
        ("chat", "0001_initial"),
        ("projects", "0001_initial"),
        ("servers", "0001_initial"),
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.CreateModel(
            name="ApptainerDefinition",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=256)),
                ("version", models.CharField(default="v1", max_length=64)),
                ("content", models.TextField()),
                ("storage_path", models.CharField(blank=True, max_length=512)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("conversation", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to="chat.conversation")),
                ("created_by", models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to="auth.user")),
                ("project", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="apptainer_defs", to="projects.project")),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="ApptainerBuildJob",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("workdir", models.CharField(max_length=512)),
                ("output_name", models.CharField(max_length=256)),
                ("status", models.CharField(choices=[("PENDING", "Pending"), ("VALIDATING", "Validating"), ("UPLOADING", "Uploading"), ("RUNNING", "Running"), ("COLLECTING", "Collecting"), ("SUCCESS", "Success"), ("FAILED", "Failed"), ("CANCELLED", "Cancelled"), ("TIMEOUT", "Timeout")], default="PENDING", max_length=32)),
                ("celery_task_id", models.CharField(blank=True, max_length=128)),
                ("log_path", models.CharField(blank=True, max_length=512)),
                ("remote_output_path", models.CharField(blank=True, max_length=512)),
                ("error_message", models.TextField(blank=True)),
                ("started_at", models.DateTimeField(blank=True, null=True)),
                ("finished_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("created_by", models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to="auth.user")),
                ("definition", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="apptainer.apptainerdefinition")),
                ("project", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="build_jobs", to="projects.project")),
                ("server", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="servers.server")),
            ],
            options={"ordering": ["-created_at"]},
        ),
    ]
