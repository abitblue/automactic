import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Optional

import httpx
from netaddr import EUI, mac_bare

from login.utils import mutually_exclusive

log = logging.getLogger('CppmApi')


class CppmApiException(Exception):
    def __init__(self, message):
        super().__init__(message)


class CppmApi:
    def __init__(self, host: str, client_id: str, client_secret: str, ssl_validation: bool):
        self._client_id: str = client_id
        self._client_secret: str = client_secret
        self._ssl_validation: bool = ssl_validation

        self._base_url = f'https://{host}/api'
        self._token_exp: Optional[datetime] = None
        self._token: Optional[str] = None
        self._token_syncing = asyncio.Event()
        self._headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        self._token_syncing.set()

    async def get_token(self) -> str:
        # In the event multiple processes attempt to obtain a token, but an update
        # is already occurring, we wait.
        await self._token_syncing.wait()

        # Use existing token if exists
        if self._token is not None and self._token_exp > datetime.now().astimezone():
            return self._token

        else:
            self._token_syncing.clear()
            async with httpx.AsyncClient(base_url=self._base_url, verify=self._ssl_validation,
                                         headers=self._headers) as client:
                resp = await client.post('/oauth', json={
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
                    log.error(msg)
                    raise CppmApiException(msg)

                self._token_syncing.set()
                log.debug('Obtained new API token: ' + self._token)
                return self._token

    async def _base_action(self, method: str, url: str, params: Optional[dict] = None,
                           data: Optional[dict] = None) -> dict:
        token = await self.get_token()
        async with httpx.AsyncClient(base_url=self._base_url,
                                     headers={**self._headers, 'Authorization': 'Bearer ' + token},
                                     verify=self._ssl_validation) as client:
            resp = await client.request(method, url, params=params, json=data)

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

                log.error(msg)
                raise CppmApiException(msg)

    async def _get_device_id_from_name(self, name: str):
        named_device = await self.get_device(name=name)
        if named_device['count'] != 1:
            raise CppmApiException('Multiple devices with same name returned')
        return int(named_device['items'][0]['id'])

    async def create_device(self, name: str, mac: EUI, expire_time: Optional[datetime] = None,
                            expire_action: int = 2) -> dict:
        # expire_action docs:
        # https://www.arubanetworks.com/techdocs/ClearPass/CPGuest_UG_HTML_6.5/Content/Reference/GuestManagerStandardFields.htm

        if expire_time is None:
            expire_time = datetime(datetime.today().year + 4, 9, 4).astimezone()

        return await self._base_action('POST', '/device', params={'change_of_authorization': True}, data={
            'visitor_name': name,
            'mac': mac.format(dialect=mac_bare),
            'expire_time': int(expire_time.timestamp()),
            "do_expire": expire_action,
            'role_id': 2,  # Guest
            'enabled': True,
            'start_time': int(datetime.now().astimezone().timestamp()),
        })

    @mutually_exclusive('name', 'mac')
    async def get_device(self, name: Optional[str] = None, mac: Optional[EUI] = None, sort='-id'):
        if name is not None:
            return await self._base_action('GET', '/device', params={
                'filter': json.dumps({'visitor_name': name}),
                'sort': sort,
                'calculate_count': True,
                'limit': 1000,
            })

        elif mac is not None:
            return await self._base_action('GET', f'/device/mac/{mac.format(dialect=mac_bare)}')

    @mutually_exclusive('device_id', 'name', 'mac')
    async def update_device(self, device_id: Optional[int] = None, name: Optional[str] = None,
                            mac: Optional[EUI] = None, data: dict = None):
        if data is None or len(data) == 0:
            raise TypeError('data cannot be empty')

        if name is not None:
            device_id = self._get_device_id_from_name(name)
        if device_id is not None:
            return await self._base_action('PATCH', f'/device/{device_id}', params={'change_of_authorization': True},
                                           data=data)
        elif mac is not None:
            return await self._base_action('PATCH', f'/device/mac/{mac.format(dialect=mac_bare)}',
                                           params={'change_of_authorization': True}, data=data)

    @mutually_exclusive('device_id', 'name', 'mac')
    async def remove_device(self, device_id: Optional[int] = None, name: Optional[str] = None,
                            mac: Optional[EUI] = None):
        if name is not None:
            device_id = self._get_device_id_from_name(name)
        if device_id is not None:
            return await self._base_action('DELETE', f'/device/{device_id}', params={'change_of_authorization': True})
        elif mac is not None:
            return await self._base_action('DELETE', f'/device/mac/{mac.format(dialect=mac_bare)}',
                                           params={'change_of_authorization': True})
