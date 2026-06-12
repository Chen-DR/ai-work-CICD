from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True
    dependencies = [
        ("projects", "0001_initial"),
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.CreateModel(
            name="AuditLog",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("action", models.CharField(max_length=128)),
                ("resource_type", models.CharField(max_length=64)),
                ("resource_id", models.CharField(blank=True, max_length=64)),
                ("ip_address", models.GenericIPAddressField(blank=True, null=True)),
                ("detail", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("project", models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to="projects.project")),
                ("user", models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to="auth.user")),
            ],
            options={"ordering": ["-created_at"], "indexes": [models.Index(fields=["project", "action"], name="audit_auditlog_project_86337a_idx"), models.Index(fields=["user"], name="audit_auditlog_user_id_6e8e47_idx"), models.Index(fields=["created_at"], name="audit_auditlog_created_1298fc_idx")]},
        ),
    ]
