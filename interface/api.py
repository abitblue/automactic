from datetime import datetime, timedelta

from netaddr import EUI

from interface.wrapper import ResponseData
from django.utils import timezone
from typing import Optional, Union
import requests
import logging
import json
import os


CLIENT_ID = os.environ['CLIENT_ID']
CLIENT_SECRET = os.environ['CLIENT_SECRET']
BASE_URL = os.environ['BASE_URL']
ENDPOINT = BASE_URL+"/oauth"


class Token:
    def __init__(self):
        self.id = str(os.environ['CLIENT_ID'])
        self.secret = str(os.environ['CLIENT_SECRET'])
        self.base_url = str(os.environ['BASE_URL'])
        self.api_url = self.base_url + '/oauth'
        self.grant_type = ["client_credentials", "password", "refresh_token"]
        self.erorr_code = [401, 403]
        self.token = ""

    def renew_token(self):
        try:
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
                self.token = token_data["access_token"]
                print(f'{self.token=}')
            elif req.status_code == 400:
                logging.error(
                    "Make sure the client id and secret are correct <400(bad req)>")

        except requests.exceptions.ConnectionError as error:
            logging.error("Make sure its the right api url", error)

    def check_token(func):
        def check(*args, **kwargs):
            self = args[0]

            response = func(*args, **kwargs)

            if response.status_code in self.erorr_code:
                self.renew_token()
                response = func(*args, **kwargs)

                if (response.status_code in self.erorr_code):
                    raise TypeError("ClearPass Token Error")

            return response

        return check

    @check_token
    def add_device(self, mac: EUI, username: str, device_name: Optional[str] = None,
                   time: Union[timedelta, datetime] = None) -> ResponseData:

        res = requests.post(f"{self.base_url}/device",
                            data=json.dumps({
                                'expire_time': self._get_expire_date(time),
                                'mac': str(mac),
                                'notes': device_name,
                                'enabled': True,
                                'visitor_name': username,
                                'role_id': 2, # guest role
                                'do_expire': 4,  # when the device expires delete the device
                                'start_time': self._get_expire_date(timezone.now() - timedelta(minutes=20)) # ClearPass system clock 20 minutes faster
                            }),
                            headers=self._get_header(),
                            verify=False
                            )
        return ResponseData(res.status_code, res)

    @check_token
    def delete_device(self, mac: EUI):
        res = requests.delete(f"{self.base_url}/device/mac/{EUI(mac)}",
                              #   params={'change_of_authorization': True},
                              headers=self._get_header(),
                              verify=False)
        return ResponseData(res.status_code, res)

    @check_token
    def get_device(self, mac: Optional[EUI] = None, name: Optional[str] = None, sort: str = "-id",
                   limit: int = 100) -> ResponseData:
        if mac is not None:
            res = requests.get(f"{self.base_url}/device/mac/{EUI(mac)}",
                               headers=self._get_header(),
                               verify=False
                               )
            return ResponseData(res.status_code, res)

        elif name is not None:
            res = requests.get(f"{self.base_url}/device",
                               params={
                                   'filter': json.dumps({'visitor_name': name}),
                                   'sort': sort,
                                   'limit': limit
                               },
                               headers=self._get_header(),
                               verify=False
                               )
            return ResponseData(res.status_code, res)
        else:
            raise TypeError('data cannot be empty')

    @check_token
    def update_device(self, mac: Optional[EUI] = None, username: Optional[str] = None, device_id: Optional[int] = None,
                      updated_fields: Optional[dict] = None) -> ResponseData:
        updated_fields = {
            **updated_fields,
            'start_time': self._get_expire_date(timezone.now() - timedelta(minutes=20))
        }
        if mac is not None:
            res = requests.patch(f"{self.base_url}/device/mac/{mac}",
                                 # params={'change_of_authorization': True},
                                 data=json.dumps(updated_fields),
                                 headers=self._get_header(),
                                 verify=False
                                 )
            return ResponseData(res.status_code, res)
        elif username is not None:
            device_response = self.get_device(name=username)
            if len(device_response.device) != 1:
                logging.error('Multiple devices with same name returned or the name does not exist')
            else:
                clearpass_device_id = int(device_response.device[0]['id'])
                res = requests.patch(f"{self.base_url}/device/{clearpass_device_id}",
                                     # params={'change_of_authorization': 1},
                                     data=json.dumps(updated_fields),
                                     headers=self._get_header(),
                                     verify=False
                                     )
                return ResponseData(res.status_code, res)
        elif device_id is not None:
            res = requests.patch(f"{self.base_url}/device/{device_id}",
                                 # params={'change_of_authorization': 1},
                                 data=json.dumps(updated_fields),
                                 headers=self._get_header(),
                                 verify=False
                                 )
            return ResponseData(res.status_code, res)
        else:
            raise TypeError('data cannot be empty')

    def _get_expire_date(self, time: Union[timedelta, datetime, None]) -> str:
        result = None
        if not time:
            pass
        elif type(time) == timedelta:
            result = str(datetime.timestamp(timezone.now() + time))
        elif type(time) == datetime:
            result = str(datetime.timestamp(time))
        else:
            logging.error("Invalid time argument!")

        return result

    def _get_header(self):
        return {
            "Authorization": f"Bearer {self.token}",
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }
