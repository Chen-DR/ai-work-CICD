from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True
    dependencies = [
        ("projects", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Artifact",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("job_type", models.CharField(blank=True, max_length=64)),
                ("job_id", models.IntegerField(blank=True, null=True)),
                ("artifact_type", models.CharField(choices=[("knowledge_file", "Knowledge File"), ("apptainer_def", "Apptainer Definition"), ("build_log", "Build Log"), ("sif_path_record", "SIF Path Record"), ("benchmark_script", "Benchmark Script"), ("benchmark_log", "Benchmark Log"), ("benchmark_report", "Benchmark Report")], max_length=64)),
                ("file_name", models.CharField(max_length=256)),
                ("storage_path", models.CharField(max_length=512)),
                ("file_size", models.IntegerField(default=0)),
                ("checksum", models.CharField(blank=True, max_length=128)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("project", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="artifacts", to="projects.project")),
            ],
            options={"ordering": ["-created_at"]},
        ),
    ]
