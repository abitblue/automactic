import base64
from datetime import datetime

import pyotp

from automactic.settings import SECRET_KEY


class RotatingCode:
    totp = pyotp.TOTP(base64.b32encode(SECRET_KEY.encode()).decode()[:32],
                      digits=9,
                      interval=86400)

    @classmethod
    def get(cls):
        return cls.totp.now()

    @classmethod
    def verify(cls, code) -> bool:
        return cls.totp.verify(code)

    @classmethod
    def remaining_time(cls) -> float:
        return cls.totp.interval - datetime.now().timestamp() % cls.totp.interval
