import requests
import logging
from pathlib import Path
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from dotenv import load_dotenv
from os import getenv


timezone = "Europe/Paris"

class APIClient:
    load_dotenv()

    _BASE_URL = "https://ipamix.clubnix.fr/api/"
    _AUTHENT_API = "user/"
    _SUBNETS_API = "subnets/"
    _API_ID = getenv('IPAM_API_ID')
    _USER = getenv('IPAM_USER')
    _PASS = getenv('IPAM_PASS')

    def __init__(self):
        self.session = requests.Session()
        self.session.verify = False
        self.logger = logging.getLogger("IPAMviewer.APIClient")

    def connect(self):
        try_nb = 0
        print(type(APIClient._USER))
        while try_nb < 5:
            api_request = self.session.post(
                APIClient._BASE_URL + APIClient._API_ID + APIClient._AUTHENT_API,
                auth = (APIClient._USER, APIClient._PASS),
            )

            if api_request.status_code != requests.codes.ok:
                self.logger.critical(f"Error {api_request.status_code}")
                self.logger.info(f"Retry #{try_nb}")
                try_nb += 1
            else:
                break
        
        if try_nb >= 5:
            raise requests.ConnectionError("IPAM API is unreachable...\n" + str(api_request.json()))
        
        self.session.headers = {"token": api_request.json()["data"]["token"]}

    def _get_data(self, endpoint, keys):
        api_request = self.session.get(endpoint)

        if api_request.status_code != requests.codes.ok:
            self.logger.critical(f"Error {api_request.status_code} : IPAM API is unreachable...\n" + api_request.json()["message"])
            return False
        
        data = []
        for elm in api_request.json()["data"]:
            data.append({key: elm[key] for key in keys})
        
        return data
    
    def get_subnets_list(self):
        return self._get_data(
            APIClient._BASE_URL + APIClient._API_ID + APIClient._SUBNETS_API,
            ["id", "sectionId", "subnet", "mask", "description", "lastScan"]
            )
        
    
    def get_hosts_list(self, subnet):
        hosts = self._get_data(
            APIClient._BASE_URL + APIClient._API_ID + APIClient._SUBNETS_API + subnet["id"] + "/addresses/",
            ["ip", "description", "hostname", "mac", "lastSeen", "note", "port"]
            )
        for host in hosts:
            last_seen = datetime.strptime(host["lastSeen"], "%Y-%m-%d %H:%M:%S").replace(tzinfo=ZoneInfo(timezone))
            now = datetime.now(tz=ZoneInfo(timezone))
            if now - last_seen <= timedelta(minutes=11.0):
                host["status"] = True
            else:
                host["status"] = False
        return hosts