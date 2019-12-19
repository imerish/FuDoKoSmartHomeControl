import requests
import json
import subprocess


class FudokoApi:
    while 1:
        try:
            command = "cat /sys/class/net/eth0/address"
            mac = ""
            mac = mac + str(subprocess.check_output(command, shell=True))
            mac = mac.rstrip()
            mac = mac.replace(':', "")
            print(mac)
            break
        except subprocess.CalledProcessError:
            continue

    def __init__(self):
        self.url = "https://fudokosmarthome.azurewebsites.net/api/ControllerHardware/Sensors"
        self.headers = {
            'fudoko-mac-address': "b827eb5a4969",
            'Content-Type': "application/json"
        }

    def get_all_available_sensors(self):
        self.url = "https://fudokosmarthome.azurewebsites.net/api/ControllerHardware/Sensors"
        response = requests.request("GET", self.url, headers=self.headers)
        while 1:
            try:
                response = requests.request("GET", self.url, headers=self.headers)
                break
            except requests.ConnectionError:
                print("Trying to restore connection")
                continue
        if response.status_code != 200:
            print(response)
        else:
            response_dict = json.loads(response.text)
            return response_dict

    def update_sensor(self, sensor):
        self.url = "https://fudokosmarthome.azurewebsites.net" \
                   "/api/ControllerHardware/Sensors"
        payload = json.dumps(sensor)
        while 1:
            try:
                response = requests.request("POST", self.url, data=payload, headers=self.headers)
                response_dict = json.loads(response.text)
                return response_dict
            except requests.ConnectionError:
                print("Trying to restore connection")
                continue

    def get_scripts_ids(self):
        self.url = "https://fudokosmarthome.azurewebsites.net/api/ControllerHardware/Scripts/Ids"
        while 1:
            try:
                response = requests.request("GET", self.url, headers=self.headers)
                response_dict = json.loads(response.text)
                return response_dict
            except requests.ConnectionError:
                print("Trying to restore connection")
                continue

    def get_new_script(self, script_id):
        self.url = "https://fudokosmarthome.azurewebsites.net/api/ControllerHardware/Scripts/"\
                   + str(script_id)
        while 1:
            try:
                response = requests.request("GET", self.url, headers=self.headers)
                response_dict = json.loads(response.text)
                return response_dict
            except requests.ConnectionError:
                print("Trying to restore connection")
                continue

    def delete_script(self, script_id):
        self.url = "https://fudokosmarthome.azurewebsites.net/api/ControllerHardware/Scripts/"\
                   + str(script_id)
        while 1:
            try:
                response = requests.request("DELETE", self.url, headers=self.headers)
                print(response.text)
                break
            except requests.ConnectionError:
                print("Trying to restore connection")
                continue

    def notification(self, sensor_id):
        self.url = "https://fudokosmarthome.azurewebsites.net/api/ControllerHardware/Notification/"+str(sensor_id)
        while 1:
            try:
                response = requests.request("PUT", self.url, headers=self.headers)
                print(response.text)
                break
            except requests.ConnectionError:
                print("Trying to restore connection")
                continue




