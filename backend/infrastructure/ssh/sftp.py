import io
import logging
import paramiko
import os
from typing import Optional

logger = logging.getLogger(__name__)


class SFTPClient:
    def __init__(self, host: str, port: int, username: str, password: str = "", pkey: str = "", timeout: int = 30):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.pkey = pkey
        self.timeout = timeout

    def _connect_sftp(self):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
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
        ssh.connect(**kwargs)
        return ssh.open_sftp()

    def upload_file(self, local_path: str, remote_path: str) -> bool:
        try:
            sftp = self._connect_sftp()
            sftp.put(local_path, remote_path)
            sftp.close()
            logger.info("SFTP upload %s -> %s", local_path, remote_path)
            return True
        except Exception as e:
            logger.error("SFTP upload failed: %s", str(e))
            return False

    def download_file(self, remote_path: str, local_path: str) -> bool:
        try:
            sftp = self._connect_sftp()
            sftp.get(remote_path, local_path)
            sftp.close()
            logger.info("SFTP download %s -> %s", remote_path, local_path)
            return True
        except Exception as e:
            logger.error("SFTP download failed: %s", str(e))
            return False

    def file_exists(self, remote_path: str) -> bool:
        try:
            sftp = self._connect_sftp()
            sftp.stat(remote_path)
            sftp.close()
            return True
        except FileNotFoundError:
            return False
        except Exception as e:
            logger.error("SFTP stat failed: %s", str(e))
            return False

    def mkdir(self, remote_path: str) -> bool:
        try:
            sftp = self._connect_sftp()
            sftp.mkdir(remote_path)
            sftp.close()
            return True
        except Exception as e:
            logger.error("SFTP mkdir failed: %s", str(e))
            return False
