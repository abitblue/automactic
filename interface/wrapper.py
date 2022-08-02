from dataclasses import dataclass

@dataclass
class ResponseData:
    mac: str = None
    notes: str = None
    start_time: int = None
    expire_time: int = None
    sponsor_name: str = None
    device_name: str = None
    status_code: int = None
    def __init__(self, status, res):
        try:
            response = res.json()
            self.mac = response['mac']
            self.notes = response['notes']
            self.start_time = response['start_time']
            self.expire_time = response['expire_time']
            self.sponsor_name = response['sponsor_name']
            self.device_name = response['visitor_name']
        except:
            pass
        self.status_code = status
