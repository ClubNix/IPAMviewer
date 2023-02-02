#!/usr/bin/env python3

from pathlib import Path
from paramiko import SSHClient, ssh_exception
from scp import SCPClient
from dotenv import load_dotenv
from os import getenv
import socket

class SSHCPClient():

    load_dotenv()

    _HOST = getenv('SSH_HOST')
    _USER = getenv('SSH_USER')
    _WEATHERMAP_RDIR = Path(getenv('WEATHERMAP_RDIR'))

    def __init__(self):
        self.ssh = SSHClient()
        self.ssh.load_system_host_keys()

    def get_weathermap(self) -> tuple[Path] | None:

        if not SSHCPClient._WEATHERMAP_RDIR:
            print("Error: Weather map directory not referenced")
            print("Skipping weathermap retrieval")
            return False

        weathermap_ldir = Path.cwd() / "ipamviewer" / "static" / "img" / "weathermap"
        Path.mkdir(weathermap_ldir, exist_ok=True)

        try:
            with self.ssh:
                print(socket.gethostbyname(socket.gethostname()))
                print(SSHCPClient._USER)
                self.ssh.connect(hostname=SSHCPClient._HOST, username=SSHCPClient._USER, timeout=3)

                with SCPClient(self.ssh.get_transport()) as scp:
                    scp.get(SSHCPClient._WEATHERMAP_RDIR / "2.png", weathermap_ldir)
                    scp.get(SSHCPClient._WEATHERMAP_RDIR / "3.png", weathermap_ldir)
        except ssh_exception.AuthenticationException as e:
            print(f"Error: {e}")
            print("Skipping weathermap retrieval")
            return False
        
        print("Weathermap retrieved from supervisor")

        return True

        
