import os
import json
import logging.config
from subprocess import PIPE, Popen

from sseclient import SSEClient

logging.config.dictConfig({
    'version': 1,
    'formatters': {
        'standard': {
            'format': '%(asctime)-15s | %(name)-8s | %(levelname)-8s : %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'formatter': 'standard',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',
        },
    },
    'loggers': {
        '': {  # root logger
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False
        },
    }
})

logger = logging.getLogger('webkook')


def main():
    host = os.environ.get('SSE_HOST')
    assert host is not None, 'SSE_HOST not defined'

    messages = SSEClient(host)
    logger.info('Started SSE webhook client')
    for msg in messages:
        parsed = json.loads(msg.data)
        if parsed:
            query = parsed.pop('query')
            body = parsed.pop('body')
            headers = {k: str(v) for k, v in parsed.items() if k.lower() != 'content-length'}

            if body.get('ref') == 'refs/heads/main':
                logger.info('Hook triggered')

                with Popen('/opt/automactic/deploy_update.sh', shell=True, stdout=PIPE, universal_newlines=True) as sp:
                    for stdout_line in iter(sp.stdout.readline, ""):
                        print(stdout_line, end='', flush=True)
                logger.info('Hook finished')


if __name__ == '__main__':
    main()
