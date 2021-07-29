import json
import logging
import sys
from datetime import datetime, timedelta
from typing import Optional, Union

import httpx
from netaddr import EUI, mac_bare

from login.utils import mutually_exclusive
from siteconfig.models import Configuration

logger = logging.getLogger('CppmApi')


class CppmApiException(Exception):
    def __init__(self, error_code, message='', *args, **kwargs):
        self.error_code = error_code
        self.traceback = sys.exc_info()
        super().__init__(message)


class CppmApi:
    def __init__(self, host: str, client_id: str, client_secret: str, ssl_validation: bool):
        self._client_id: str = client_id
        self._client_secret: str = client_secret
        self._ssl_validation: bool = ssl_validation

        self._base_url = f'https://{host}/api'
        self._token_exp: Optional[datetime] = None
        self._token: Optional[str] = None
        # self._token_syncing = asyncio.Event()
        self._headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        self._proxies = {
            'http://': None,
            'https://': None,
        }
        # self._token_syncing.set()

    def get_token(self) -> str:
        # Use existing token if exists
        if self._token is not None and self._token_exp > datetime.now().astimezone():
            return self._token

        else:
            # self._token_syncing.clear()
            with httpx.Client(base_url=self._base_url, verify=self._ssl_validation, timeout=10.0,
                              proxies=self._proxies, headers=self._headers) as client:
                resp = client.post('/oauth', json={
                    'grant_type': 'client_credentials',
                    'client_id': self._client_id,
                    'client_secret': self._client_secret
                })
                if not resp.is_error:
                    data = resp.json()
                    self._token = data['access_token']
                    self._token_exp = datetime.now().astimezone() + timedelta(seconds=data['expires_in'] - 5)
                else:
                    msg = 'Unable to obtain Clearpass token: ' + resp.text
                    logger.error(msg)
                    raise CppmApiException(resp.status_code, msg)

                # self._token_syncing.set()
                logger.debug('Obtained new API token: ' + self._token)
                return self._token

    def _base_action(self, method: str, url: str, params: Optional[dict] = None,
                     data: Optional[dict] = None, ret_resp: bool = False) -> dict:
        token = self.get_token()
        with httpx.Client(base_url=self._base_url, proxies=self._proxies, timeout=10.0,
                          headers={**self._headers, 'Authorization': 'Bearer ' + token},
                          verify=self._ssl_validation) as client:
            resp = client.request(method, url, params=params, json=data)

            if ret_resp:
                return resp

            # Process data if there are no errors
            if not resp.is_error:
                data: dict = resp.json()
                if '_embedded' in data.keys() and 'items' in data['_embedded']:
                    data['items'] = data['_embedded']['items']
                    del data['_embedded']
                return data

            else:
                msg = str(resp)
                if resp.text:
                    msg += f' {resp.json()["detail"]}'

                logger.error(msg)
                raise CppmApiException(resp.status_code, msg)

    def _get_device_id_from_name(self, name: str):
        named_device = self.get_device(name=name)
        if named_device['count'] != 1:
            raise CppmApiException(406, 'Multiple devices with same name returned')
        return int(named_device['items'][0]['id'])

    def create_device(self, name: str, mac: EUI, notes: Optional[str] = None,
                      expire_time: Optional[Union[datetime, int]] = None,
                      expire_action: Optional[int] = None, ret_resp: bool = False) -> dict:
        if expire_time is None:
            update_val = lambda val, reftime: reftime + eval(val) if val[0] in ('+', '-') else int(val)
            m, d, y = tuple(map(update_val,
                                Configuration.get('ClearpassDeviceExpireDate'),
                                [datetime.today().month, datetime.today().day, datetime.today().year]))
            expire_time = datetime(y, m, d).astimezone()

        if expire_action is None:
            expire_action = Configuration.get('ClearpassExpireAction', cast=int)[0]

        return self._base_action('POST', '/device', params={'change_of_authorization': True}, data={
            'visitor_name': name,
            'mac': mac.format(dialect=mac_bare),
            'expire_time': int(expire_time.timestamp()) if isinstance(expire_time, datetime) else expire_time,
            "do_expire": expire_action,
            'role_id': 2,  # Guest
            'enabled': True,
            'start_time': int(datetime.now().astimezone().timestamp()),
            'notes': '' if notes is None else notes
        }, ret_resp=ret_resp)

    @mutually_exclusive('name', 'mac')
    def get_device(self, name: Optional[str] = None, mac: Optional[EUI] = None, sort: str = '-id',
                   additional_filers: dict = None, ret_resp: bool = False) -> dict:
        if name is not None:
            return self._base_action('GET', '/device', params={
                'filter': json.dumps({
                    'visitor_name': name,
                    **(additional_filers or {})
                }),
                'sort': sort,
                'calculate_count': True,
                'limit': 1000,
            }, ret_resp=ret_resp)

        elif mac is not None:
            return self._base_action('GET', f'/device/mac/{mac.format(dialect=mac_bare)}', ret_resp=ret_resp)

    @mutually_exclusive('device_id', 'name', 'mac')
    def update_device(self, device_id: Optional[int] = None, name: Optional[str] = None,
                      mac: Optional[EUI] = None, data: dict = None, ret_resp: bool = False) -> dict:
        if data is None or len(data) == 0:
            raise TypeError('data cannot be empty')

        if name is not None:
            device_id = self._get_device_id_from_name(name)
        if device_id is not None:
            return self._base_action('PATCH', f'/device/{device_id}', params={'change_of_authorization': True},
                                     data=data, ret_resp=ret_resp)
        elif mac is not None:
            return self._base_action('PATCH', f'/device/mac/{mac.format(dialect=mac_bare)}',
                                     params={'change_of_authorization': True}, data=data, ret_resp=ret_resp)

    @mutually_exclusive('device_id', 'name', 'mac')
    def remove_device(self, device_id: Optional[int] = None, name: Optional[str] = None,
                      mac: Optional[EUI] = None, ret_resp: bool = False) -> dict:
        if name is not None:
            device_id = self._get_device_id_from_name(name)
        if device_id is not None:
            return self._base_action('DELETE', f'/device/{device_id}', params={'change_of_authorization': True},
                                     ret_resp=ret_resp)
        elif mac is not None:
            return self._base_action('DELETE', f'/device/mac/{mac.format(dialect=mac_bare)}',
                                     params={'change_of_authorization': True}, ret_resp=ret_resp)
