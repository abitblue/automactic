from dataclasses import dataclass, field

@dataclass
class ResponseData:
    mac: list[str]
    notes: str = None
    start_time: int = None
    expire_time: int = None
    sponsor_name: str = None
    device_name: str = None
    status_code: int = None
    def __init__(self, status, res):
        self.mac = []
        try:
            response = res.json()
            if (type(response['mac']) != list):
                if (not self.mac):
                     self.mac = []
                self.mac.append(response['mac'])
            else:
                self.mac = response['mac']
            self.notes = response['notes']
            self.start_time = response['start_time']
            self.expire_time = response['expire_time']
            self.device_name = response['visitor_name']
        except:
            pass

        self.status_code = status

    def __eq__(self, other):
        return (
            self.mac == other.mac and
            self.notes == other.notes and
            self.start_time == other.start_time and
            self.expire_time == other.expire_time and 
            self.sponsor_name == other.sponsor_name and
            self.device_name == other.device_name
        )
     
