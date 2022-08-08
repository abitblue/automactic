import os

from .base import *
if os.environ.get('AMAC_ENV') == 'prod':
    from .prod import *
else:
    from .dev import *
