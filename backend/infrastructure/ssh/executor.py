import io
import logging
import paramiko
import socket
from typing import Callable, Optional

logger = logging.getLogger(__name__)


class SSHExecutor:
    def __init__(self, host: str, port: int, username: str, password: str = "", pkey: str = "", timeout: int = 30):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.pkey = pkey
        self.timeout = timeout

    def _connect(self) -> paramiko.SSHClient:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        kwargs = {
            "hostname": self.host,
            "port": self.port,
            "username": self.username,
            "timeout": self.timeout,
        }
        if self.password:
            kwargs["password"] = self.password
        if self.pkey:
            kwargs["pkey"] = paramiko.RSAKey.from_private_key(io.StringIO(self.pkey))
        client.connect(**kwargs)
        return client

    def run_command(
        self,
        command: str,
        timeout: Optional[int] = None,
        log_callback: Optional[Callable[[str], None]] = None,
    ) -> tuple[int, str, str]:
        """Execute a command and return (exit_code, stdout, stderr)."""
        client = self._connect()
        try:
            stdin, stdout, stderr = client.exec_command(command, timeout=timeout)
            out = stdout.read().decode("utf-8", errors="ignore")
            for line in out.splitlines():
                if log_callback:
                    log_callback(line)
            err = stderr.read().decode("utf-8", errors="ignore")
            exit_code = stdout.channel.recv_exit_status()
            logger.info("SSH command exit=%d on %s", exit_code, self.host)
            return exit_code, out, err
        finally:
            client.close()

    def test_connection(self) -> tuple[bool, str]:
        try:
            self._connect().close()
            return True, "Connection successful"
        except (paramiko.SSHException, socket.error) as e:
            return False, str(e)

    def close(self):
        pass
