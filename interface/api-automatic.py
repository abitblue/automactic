from datetime import datetime, timedelta
from wrapper import ResponseData
from typing import Optional
import requests
import logging
import time
import json
import os

# CLIENT_ID = os.environ['CLIENT_ID']
# CLIENT_SECRET = os.environ['CLIENT_SECRET']
# BASE_URL = os.environ['BASE_URL']
# ENDPOINT = BASE_URL+"/oauth"

class Token:

    def __init__(self):
        self.id = str(os.environ['CLIENT_ID']).replace("'","")
        self.secret = str(os.environ['CLIENT_SECRET']).replace("'","")
        self.base_url = str(os.environ['BASE_URL']).replace("'","")
        self.api_url = str(os.environ['OAUTH_ENDPOINT']).replace("'","")
        self.grant_type = ["client_credentials", "password", "refresh_token"]
        self.current_time = time.time()
        self.token_expire_time = self.current_time
        self.token = ""
        self.check_token()
        self.check_token()

    def check_token(func):
        def check(*args, **kwargs):
            self = args[0]
            try:
                if self.current_time >= self.token_expire_time:
                    req = requests.post(self.api_url, headers={
                        'Content-Type': 'application/json',
                        'Accept': 'application/json',
                    }, json={
                        'grant_type': self.grant_type[0],
                        'client_id': self.id,
                        'client_secret': self.secret,
                    }, verify=False)
                    if req.status_code == 200:
                        token_data = req.json()
                        self.token_expire_time = token_data["expires_in"] + \
                            self.current_time
                        self.token = token_data["access_token"]
                        print(self.token)
                    elif req.status_code == 400:
                        logging.error(
                            "Make sure the client id and secret are correct <400(bad req)>")
                else:
                    pass

            except requests.exceptions.ConnectionError as error:
                logging.error("Make sure its the right api url", error)
            
            return func(*args, **kwargs)

        return check

    @check_token
    def add_device(self, mac: str, device_name: str, notes: Optional[str] = None, enabled: bool = True, year: Optional[int] = 4) -> dict:

        res = requests.post(f"{self.base_url}/device",
                            data=json.dumps({
                                'expire_time': self._get_expire_date(year),
                                'mac': mac,
                                'sponsor_name': 'oauth2:automatic',
                                'notes': notes,
                                'enabled': enabled,
                                'visitor_name': device_name,
                                'role_id': 2
                            }),
                            headers={
                                "Authorization": f"Bearer {self.token}",
                                'Content-Type': 'application/json',
                                'Accept': 'application/json',
                            }, verify=False
                            )
        return ResponseData(res.status_code, res)

    @check_token
    def delete_device(self, mac: str) -> dict:
        res = requests.delete(f"{self.base_url}/device/mac/{mac}",
                              headers={
                                  "Authorization": f"Bearer {self.token}",
                                  'Content-Type': 'application/json',
                                  'Accept': 'application/json',
                              }, verify=False)
        return ResponseData(res.status_code, res)

    @check_token
    def get_device(self, mac: Optional[str] = None, device_id: Optional[int] = None) -> dict:
        if mac is not None:
            res = requests.get(f"{self.base_url}/device/mac/{mac}",
                               headers={
                                   'Content-Type': 'application/json',
                                   'Accept': 'application/json',
                                   "Authorization": f"Bearer {self.token}"
                               }, verify=False)
            return ResponseData(res.status_code, res)

        elif device_id is not None:
            res = requests.get(f"{self.base_url}/device/{device_id}",
                               headers={
                                   'Content-Type': 'application/json',
                                   'Accept': 'application/json',
                                   "Authorization": f"Bearer {self.token}"
                               }, verify=False)
            return ResponseData(res.status_code, res)
        else:
            raise TypeError('data cannot be empty')

    @check_token
    def update_device(self, mac: str, expire_time: Optional[str] = None, notes: Optional[str] = None, enabled: bool = True, role_id: Optional[int] = 2) -> dict:

        fields = {
            'mac': mac,
            'enabled': enabled,
            'role_id': role_id
        }
        if expire_time: fields['expire_time'] = expire_time
        if notes: fields['notes'] = notes

        res = requests.patch(f"{self.base_url}/device/mac/{mac}",
            data=json.dumps(fields),
            headers={
                "Authorization": f"Bearer {self.token}",
                'Content-Type': 'application/json',
                'Accept': 'application/json',
            }, verify=False
        )
        return ResponseData(res.status_code, res)


    def _get_expire_date(self, year: str) -> str:
        now = datetime.now()
        future = now.replace(month=8, day=31, hour=20,
                             minute=0, second=0) + timedelta(year*365)
        return datetime.timestamp(future)



thing = Token()
thing.add_device()