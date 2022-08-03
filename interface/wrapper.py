from dataclasses import dataclass, field, fields

@dataclass
class ResponseData:
    id: list[int] = None
    mac: list[str] = None
    notes: list[str] = None
    start_time: list[int] = None
    expire_time: list[int] = None
    sponsor_name: list[str] = None
    device_name: list[str] = None
    status_code: int = None
    def __init__(self, status, res):
        self.status_code = status
        self._init_fields()
        try:
            response = res.json()
        except:
            return
        if '4' in str(self.status_code)[0]:
            return

        if '_embedded' in response:
            for data in response['_embedded']['items']:
                self._add_field(data)
        else:
            self._add_field(response)

    def __eq__(self, other):
        return (
            self.mac == other.mac and
            self.notes == other.notes and
            self.start_time == other.start_time and
            self.expire_time == other.expire_time and 
            self.sponsor_name == other.sponsor_name and
            self.device_name == other.device_name and
            self.id == other.id
        )

    def _add_field(self, data):
        self.mac.append(data['mac'])
        self.notes.append(data['notes'])
        self.start_time.append(data['start_time'])
        self.expire_time.append(data['expire_time'])
        self.sponsor_name.append(data['sponsor_name'])
        self.device_name.append(data['visitor_name'])
        self.id.append(int(data['id']))

    def _init_fields(self):
        self.mac = []
        self.notes = []
        self.start_time = []
        self.expire_time = []
        self.sponsor_name = []
        self.device_name = []
        self.id = []
