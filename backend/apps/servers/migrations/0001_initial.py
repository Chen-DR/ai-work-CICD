from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True
    dependencies = [
        ("projects", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Server",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=128)),
                ("host", models.CharField(max_length=128)),
                ("port", models.IntegerField(default=22)),
                ("username", models.CharField(max_length=128)),
                ("auth_type", models.CharField(default="password", max_length=32)),
                ("status", models.CharField(choices=[("ACTIVE", "Active"), ("DISABLED", "Disabled"), ("UNKNOWN", "Unknown"), ("FAILED", "Failed")], default="UNKNOWN", max_length=32)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("project", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="servers", to="projects.project")),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="ServerAllowedDir",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("path", models.CharField(max_length=512)),
                ("purpose", models.CharField(choices=[("build", "Build"), ("benchmark", "Benchmark"), ("report", "Report"), ("general", "General")], default="general", max_length=32)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("server", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="allowed_dirs", to="servers.server")),
            ],
        ),
        migrations.CreateModel(
            name="ServerCredential",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("credential_type", models.CharField(max_length=32)),
                ("encrypted_secret", models.TextField()),
                ("secret_hint", models.CharField(blank=True, max_length=128)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("server", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="credentials", to="servers.server")),
            ],
            options={"unique_together": {("server", "credential_type")}},
        ),
    ]
