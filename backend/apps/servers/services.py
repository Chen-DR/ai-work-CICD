from .models import Server, ServerCredential
from infrastructure.security.encryptor import encrypt, decrypt


def save_server_credentials(server: Server, password: str = "", ssh_key: str = ""):
    if password:
        encrypted = encrypt(password)
        ServerCredential.objects.update_or_create(
            server=server,
            credential_type=ServerCredential.CREDENTIAL_PASSWORD,
            defaults={"encrypted_secret": encrypted, "secret_hint": password[:4] + "****"},
        )
    if ssh_key:
        encrypted = encrypt(ssh_key)
        ServerCredential.objects.update_or_create(
            server=server,
            credential_type=ServerCredential.CREDENTIAL_SSH_KEY,
            defaults={"encrypted_secret": encrypted, "secret_hint": "ssh-key-****"},
        )


def get_server_credentials(server: Server) -> dict:
    result = {"password": "", "ssh_key": ""}
    creds = ServerCredential.objects.filter(server=server)
    for c in creds:
        try:
            decrypted = decrypt(c.encrypted_secret)
            result[c.credential_type] = decrypted
        except Exception:
            continue
    return result
