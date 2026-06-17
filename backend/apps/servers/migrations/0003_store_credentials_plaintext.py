from django.db import migrations, models


def copy_secret_to_plaintext(apps, schema_editor):
    ServerCredential = apps.get_model("servers", "ServerCredential")

    try:
        from django.conf import settings
        from cryptography.fernet import Fernet, InvalidToken
        import base64
        import hashlib

        key = getattr(settings, "ENCRYPTION_KEY", "")
        if key:
            if len(key) != 44 or not key.endswith("="):
                key = base64.urlsafe_b64encode(hashlib.sha256(key.encode()).digest())
            fernet = Fernet(key)
        else:
            fernet = None
    except Exception:
        fernet = None
        InvalidToken = Exception

    for credential in ServerCredential.objects.all():
        value = credential.encrypted_secret
        if fernet:
            try:
                value = fernet.decrypt(value.encode()).decode()
            except InvalidToken:
                pass
            except Exception:
                pass
        credential.secret = value
        credential.save(update_fields=["secret"])


class Migration(migrations.Migration):
    dependencies = [
        ("servers", "0002_servermetric"),
    ]

    operations = [
        migrations.AddField(
            model_name="servercredential",
            name="secret",
            field=models.TextField(blank=True, default=""),
            preserve_default=False,
        ),
        migrations.RunPython(copy_secret_to_plaintext, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name="servercredential",
            name="encrypted_secret",
        ),
    ]
