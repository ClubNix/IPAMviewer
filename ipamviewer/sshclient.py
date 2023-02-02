#!/usr/bin/env python3

from pathlib import Path
from paramiko import SSHClient, ssh_exception
from scp import SCPClient
from dotenv import load_dotenv
from os import getenv

class SSHClient():

    load_dotenv()

    _HOST = getenv('SSH_HOST')
    _USER = getenv('SSH_USER')
    _WEATHERMAP_RDIR = Path(getenv('WEATHERMAP_RDIR'))

    def __init__(self):
        self.ssh = SSHClient()
        self.scp = SCPClient()
        self.ssh.load_system_host_keys()

    def get_weathermap(self) -> tuple[Path] | None:

        if not SSHClient._WEATHERMAP_RDIR:
            print("Error: Weather map directory not referenced")
            print("Skipping weathermap retrieval")
            return

        weathermap_ldir = Path.cwd() / "weathermap"
        Path.mkdir(weathermap_ldir, exist_ok=True)

        try:
            with self.ssh:
                self.ssh.connect(hostname=SSHClient._HOST, username=SSHClient._USER)

                with self.scp(self.ssh.get_transport()):
                    self.scp.get(SSHClient._WEATHERMAP_RDIR / "2.png", weathermap_ldir)
                    self.scp.get(SSHClient._WEATHERMAP_RDIR / "3.png", weathermap_ldir)
        except ssh_exception.AuthenticationException as e:
            print(f"Error: {e}")
            print("Skipping weathermap retrieval")
        
        print("Weathermap retrieved from supervisor")

        return (weathermap_ldir / "2.png", weathermap_ldir / "3.png")
