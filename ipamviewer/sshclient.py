from pathlib import Path
from paramiko import SSHClient, ssh_exception, AutoAddPolicy
from scp import SCPClient
from dotenv import load_dotenv
from os import getenv
from tempfile import mkdtemp


class WeathermapRetriever:
    load_dotenv()

    _HOST = getenv("SSH_HOST")
    _USER = getenv("SSH_USER")
    _WEATHERMAP_RDIR = Path(getenv("WEATHERMAP_RDIR"))

    def __init__(self):
        self.ssh = SSHClient()
        self.ssh.load_system_host_keys()
        self.ssh.set_missing_host_key_policy(AutoAddPolicy())
        self.weathermap_ldir = Path(mkdtemp())

    def get_weathermap(self) -> tuple[Path] | None:

        if not WeathermapRetriever._WEATHERMAP_RDIR:
            print("Error: Weather map directory not referenced")
            print("Skipping weathermap retrieval")
            return False

        try:
            with self.ssh:
                self.ssh.connect(
                    hostname=WeathermapRetriever._HOST,
                    username=WeathermapRetriever._USER,
                    timeout=3,
                )

                with SCPClient(self.ssh.get_transport()) as scp:
                    stdin, stdout, stderr = self.ssh.exec_command(
                        f"ls {WeathermapRetriever._WEATHERMAP_RDIR} | grep '^[0-9]+.png$'"
                    )
                    if not stdout:
                        print("Error: No weathermap files found")
                        print("Skipping weathermap retrieval")
                        return False
                    else:
                        for line in stdout:
                            scp.get(
                                WeathermapRetriever._WEATHERMAP_RDIR
                                / line.strip(),
                                self.weathermap_ldir,
                            )

        except ssh_exception.AuthenticationException as e:
            print(f"Error: {e}")
            print("Skipping weathermap retrieval")
            return False

        print("Weathermap retrieved from supervisor")

        return True
