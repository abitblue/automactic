from dataclasses import dataclass, field, fields
from typing import Union


@dataclass
class ResponseData:
    device: list[dict[str, Union[str, int]]] = None
    status_code: int = None

    def __init__(self, status, res):
        self.status_code = status
        self._initiate_field()
        try:
            response = res.json()
        except:
            return
        if '4' in str(self.status_code)[0]:
            print(response)
            return

        if '_embedded' in response:
            for data in response['_embedded']['items']:
                self._add_device(self._create_device(data))
        else:
            self._add_device(self._create_device(response))

    def __eq__(self, other):
        return self.device == other.device

    def _initiate_field(self):
        self.device = []

    def _create_device(self, data):
        return {
            'id': int(data['id']),
            'mac': data['mac'],
            'notes': data['notes'],
            'start_time': data['start_time'],
            'expire_name': data['expire_time'],
            'sponosor_name': data['sponsor_name'],
            'device_name': data['visitor_name']
        }

    def _add_device(self, d):
        self.device.append(d)
