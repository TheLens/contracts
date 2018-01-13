"""Logger."""

import argparse
import logging
import os
import random
import string

from datetime import datetime

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# CLI
parser = argparse.ArgumentParser()
parser.add_argument("-v", "--verbose", action="store_true")
args = parser.parse_args()

# uuid = ''.join(random.choice(string.ascii_lowercase) for x in range(6))
# timestamp = datetime.now().strftime('%Y-%d-%m.%H-%M-%S-%f')
# file_name = '{}.{}.log'.format(timestamp, uuid)

datestamp = datetime.now().strftime('%Y-%m-%d')
file_name = '{}.log'.format(datestamp)

LOG_FILE = os.path.join(PROJECT_DIR, 'logs', file_name)

if not os.path.exists(os.path.dirname(LOG_FILE)):
    os.makedirs(os.path.dirname(LOG_FILE))

if not os.path.isfile(LOG_FILE):
    open(LOG_FILE, "w").close()

formatter = logging.Formatter('%(asctime)s | %(module)s.%(funcName)s | %(levelname)s | %(lineno)d | %(message)s')

# handler = logging.handlers.RotatingFileHandler(LOG_FILE, maxBytes=(5 * 1024 * 1024),  backupCount=5)
handler = logging.FileHandler(LOG_FILE)
handler.setFormatter(formatter)

logger = logging.getLogger(__name__)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

if args.verbose:
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.INFO)
