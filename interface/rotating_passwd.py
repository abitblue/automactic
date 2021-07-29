import base64
from datetime import datetime

import pyotp

from automactic.settings import SECRET_KEY
from siteconfig.models import Configuration


class RotatingCode:
    @classmethod
    def get_totp(cls):
        import time
        t0 = time.time()
        totp = pyotp.TOTP(base64.b32encode(SECRET_KEY.encode()).decode()[:32],
                          digits=Configuration.get('GuestPasswordLength', cast=int)[0],
                          interval=Configuration.get('GuestPasswordUpdateInterval', cast=int)[0])
        print(time.time() - t0)
        return totp

    @classmethod
    def get(cls):
        return cls.get_totp().now()

    @classmethod
    def verify(cls, code) -> bool:
        return cls.get_totp().verify(code)

    @classmethod
    def remaining_time(cls) -> float:
        totp = cls.get_totp()
        return cls.get_totp().interval - datetime.now().timestamp() % cls.get_totp().interval
