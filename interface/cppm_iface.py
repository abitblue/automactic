import os
from cppm_api import CppmApi

Clearpass = CppmApi(host=os.environ['CLEARPASS_HOST'],
                    client_id=os.environ['CLEARPASS_CLIENT_ID'],
                    client_secret=os.environ['CLEARPASS_CLIENT_SECRET'],
                    ssl_validation=False)
