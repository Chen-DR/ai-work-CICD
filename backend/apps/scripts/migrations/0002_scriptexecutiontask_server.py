from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("scripts", "0001_initial"),
        ("servers", "0003_store_credentials_plaintext"),
    ]

    operations = [
        migrations.AddField(
            model_name="scriptexecutiontask",
            name="server",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="script_tasks",
                to="servers.server",
            ),
        ),
    ]
