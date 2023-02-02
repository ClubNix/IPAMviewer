from .apiclient import APIClient
from .sshclient import SSHCPClient
from flask import Flask, render_template
from requests import ConnectionError
import datetime
from zoneinfo import ZoneInfo
from urllib3 import disable_warnings

disable_warnings()

app = Flask(__name__)

@app.route('/')
def hello():
    apiClient = APIClient()
    try:
        content = {}
        apiClient.connect()
        subnets = apiClient.get_subnets_list()
        for subnet in subnets:
            subnet["hosts"] = apiClient.get_hosts_list(subnet)
        content["selected_subnets"] = [subnet for subnet in subnets if subnet["subnet"] != "10.0.2.0"]
        sshClient = SSHCPClient() # supervinix dans 103 -> ouverture port vers 42 pour test
        content["weathermap_exists"] = sshClient.get_weathermap()
        return render_template('index.html', utc_dt=datetime.datetime.now(tz=ZoneInfo("Europe/Paris")), **content)
    except ConnectionError as e:
        return render_template("error.html", error=e)

def main():
    app.run(debug=False, host='0.0.0.0', port=5000)

if __name__ == "__main__":
    main()