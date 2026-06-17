from .models import Server, ServerCredential


def save_server_credentials(server: Server, password: str = "", ssh_key: str = ""):
    if password:
        ServerCredential.objects.update_or_create(
            server=server,
            credential_type=ServerCredential.CREDENTIAL_PASSWORD,
            defaults={"secret": password, "secret_hint": password[:4] + "****"},
        )
    if ssh_key:
        ServerCredential.objects.update_or_create(
            server=server,
            credential_type=ServerCredential.CREDENTIAL_SSH_KEY,
            defaults={"secret": ssh_key, "secret_hint": "ssh-key-****"},
        )


def get_server_credentials(server: Server) -> dict:
    result = {"password": "", "ssh_key": ""}
    creds = ServerCredential.objects.filter(server=server)
    for c in creds:
        result[c.credential_type] = c.secret
    return result
