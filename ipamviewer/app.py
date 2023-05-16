from .apiclient import APIClient
from .sshclient import SSHCPClient
from flask import Flask, render_template
from requests import ConnectionError
import datetime
from zoneinfo import ZoneInfo
from urllib3 import disable_warnings

disable_warnings()

app = Flask(__name__)

exclude_subnets = "10.0.2.0"

@app.route('/')
def hello():
    api_client = APIClient()
    try:
        content = {}
        api_client.connect()
        subnets = api_client.get_subnets_list()
        for subnet in subnets:
            subnet["hosts"] = api_client.get_hosts_list(subnet)
        content["selected_subnets"] = [subnet for subnet in subnets if subnet["subnet"] != exclude_subnets]
        ssh_client = SSHCPClient()
        content["weathermap_exists"] = ssh_client.get_weathermap()
        return render_template('index.html', utc_dt=datetime.datetime.now(tz=ZoneInfo("Europe/Paris")), **content)
    except ConnectionError as e:
        return render_template("error.html", error=e)

def main():
    app.run(debug=False, host='0.0.0.0', port=5000)

if __name__ == "__main__":
    main()