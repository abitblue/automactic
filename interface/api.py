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
        self.id = str(os.environ['CLIENT_ID'])
        self.secret = str(os.environ['CLIENT_SECRET'])
        self.base_url = str(os.environ['BASE_URL'])
        self.api_url = self.base_url + '/oauth'
        self.grant_type = ["client_credentials", "password", "refresh_token"]
        self.current_time = time.time()
        self.token_expire_time = self.current_time
        self.token = ""
        
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
                        self.token_expire_time = token_data["expires_in"] + self.current_time - 60
                        self.token = token_data["access_token"]
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
    def add_device(self, mac: str, username: str, userType: str, device_name: Optional[str] = None, enabled: bool = True, customTime: timedelta = None) -> dict:

        res = requests.post(f"{self.base_url}/device",
                            data=json.dumps({
                                'expire_time': self._get_expire_date(userType, customTime),
                                'mac': mac,
                                'notes': device_name,
                                'enabled': enabled,
                                'visitor_name': username,
                                'role_id': 2,
                                'do_expire': True,
                                'start_time': self._get_expire_date('custom', timedelta(minutes=20)) # ClearPass system clock 20 minutes faster
                            }),
                            headers=self._get_header(), 
                            verify=False
                            )
        return ResponseData(res.status_code, res)

    @check_token
    def delete_device(self, mac: str):
        res = requests.delete(f"{self.base_url}/device/mac/{mac}",
                              headers=self._get_header(), 
                              verify=False)
        return ResponseData(res.status_code, res)

    @check_token
    def get_device(self, mac: Optional[str] = None, device_id: Optional[int] = None) -> dict:
        if mac is not None:
            res = requests.get(f"{self.base_url}/device/mac/{mac}",
                headers=self._get_header(), 
                verify=False
            )
            return ResponseData(res.status_code, res)

        elif device_id is not None:
            res = requests.get(f"{self.base_url}/device/{device_id}",
                headers=self._get_header(), 
                verify=False
            )
            return ResponseData(res.status_code, res)
        else:
            raise TypeError('data cannot be empty')

    @check_token
    def update_device(self, mac: Optional[str] = None, name: Optional[str] = None, device_id: Optional[int] = None, expire_time: Optional[str] = None, notes: Optional[str] = None, enabled: bool = True, role_id: Optional[int] = 2) -> dict:
        fields = {
            'mac': mac,
            'enabled': enabled,
            'role_id': role_id
        }
        if expire_time: fields['expire_time'] = expire_time
        if notes: fields['notes'] = notes
        if mac is not None:
            res = requests.patch(f"{self.base_url}/device/mac/{mac}",
                data=json.dumps(fields),
                headers=self._get_header(), 
                verify=False
            )
            return ResponseData(res.status_code, res)
        elif name is not None:
            res = requests.patch(f"{self.base_url}device/{device_id}",
                                 data=json.dumps(fields),
                                 headers=self._get_header(), 
                                 verify=False
                                 )
            return ResponseData(res.status_code, res)
        elif device_id is not None:
            res = requests.patch(f"{self.base_url}device/{device_id}",
                                 data=json.dumps(fields),
                                 headers=self._get_header(), 
                                 verify=False
                                 )
            return ResponseData(res.status_code, res)
        else:
            raise TypeError('data cannot be empty')

    def _get_expire_date(self, userType: str, custom: timedelta) -> str:
        now = datetime.now()
        result = None
        if (userType == 'student'):
            result = datetime.timestamp(now.replace(month=8, day=31, hour=20, minute=0, second=0) + timedelta(days=4*365))
        elif (userType == 'teacher'):
            pass
        elif (userType == 'guest'):
            result = datetime.timestamp(now + timedelta(days=1))
        elif (userType == 'custom'):
            result = datetime.timestamp(now + custom)
        else:
            logging.warn(f'{userType} is not a valid User Type, setting expiration to no expiration.\nValid user types are: teacher, student, guest.')

        return result

    def _get_header(self):
        return {
            "Authorization": f"Bearer {self.token}",
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }
