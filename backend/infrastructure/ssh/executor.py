import io
import logging
import paramiko
import socket
import time
from typing import Callable, Optional

logger = logging.getLogger(__name__)


class CommandCancelledError(Exception):
    pass


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
        stderr_callback: Optional[Callable[[str], None]] = None,
        get_pty: bool = False,
        stop_callback: Optional[Callable[[], bool]] = None,
    ) -> tuple[int, str, str]:
        """Execute a command and return (exit_code, stdout, stderr)."""
        client = self._connect()
        try:
            stdin, stdout, stderr = client.exec_command(command, timeout=timeout, get_pty=get_pty)
            channel = stdout.channel
            out_chunks: list[str] = []
            err_chunks: list[str] = []
            deadline = time.monotonic() + timeout if timeout else None

            def collect_ready_output():
                while channel.recv_ready():
                    chunk = channel.recv(4096).decode("utf-8", errors="ignore")
                    out_chunks.append(chunk)
                    if log_callback:
                        log_callback(chunk)
                while channel.recv_stderr_ready():
                    chunk = channel.recv_stderr(4096).decode("utf-8", errors="ignore")
                    err_chunks.append(chunk)
                    if stderr_callback:
                        stderr_callback(chunk)
                    elif log_callback:
                        log_callback(chunk)

            while True:
                collect_ready_output()
                if channel.exit_status_ready():
                    collect_ready_output()
                    break
                if stop_callback and stop_callback():
                    channel.close()
                    raise CommandCancelledError("SSH command cancelled")
                if deadline and time.monotonic() > deadline:
                    channel.close()
                    raise TimeoutError(f"SSH command timed out after {timeout} seconds")
                time.sleep(0.1)

            exit_code = channel.recv_exit_status()
            out = "".join(out_chunks)
            err = "".join(err_chunks)
            logger.info("SSH command exit=%d on %s", exit_code, self.host)
            return exit_code, out, err
        finally:
            client.close()

    def test_connection(self) -> tuple[bool, str]:
        try:
            self._connect().close()
            return True, "连接成功"
        except paramiko.AuthenticationException:
            return False, "服务器认证失败，请检查用户名、密码或 SSH 私钥是否正确"
        except paramiko.ssh_exception.NoValidConnectionsError:
            return False, "无法连接到服务器，请检查主机地址、端口和防火墙"
        except socket.timeout:
            return False, "连接服务器超时，请检查网络连通性和安全组规则"
        except (paramiko.SSHException, socket.error) as e:
            message = str(e).strip()
            if "Authentication failed" in message:
                return False, "服务器认证失败，请检查用户名、密码或 SSH 私钥是否正确"
            return False, str(e)

    def close(self):
        pass
