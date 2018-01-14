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

random_string = ''.join(random.choice(string.ascii_lowercase) for x in range(6))
timestamp = datetime.now().strftime('%Y-%m-%d.%H-%M-%S-%f')
# datestamp = datetime.now().strftime('%Y-%m-%d')

app_log_filename = 'App_{}_{}.log'.format(timestamp, random_string)
scrape_log_filename = 'Scrape_{}_{}.log'.format(timestamp, random_string)

# LOG = os.path.join(PROJECT_DIR, 'logs', log_filename)
APP_LOG = os.path.join(PROJECT_DIR, 'logs', app_log_filename)
SCRAPE_LOG = os.path.join(PROJECT_DIR, 'logs', scrape_log_filename)

if not os.path.exists(os.path.dirname(APP_LOG)):
    os.makedirs(os.path.dirname(APP_LOG))

# if not os.path.isfile(LOG):
#     open(LOG, "w").close()
if not os.path.isfile(APP_LOG):
    open(APP_LOG, "w").close()
if not os.path.isfile(SCRAPE_LOG):
    open(SCRAPE_LOG, "w").close()

# handler = logging.handlers.RotatingFileHandler(APP_LOG, maxBytes=(5 * 1024 * 1024),  backupCount=5)
formatter = logging.Formatter('%(asctime)s | ' +
                              '%(module)s.%(funcName)s | ' +
                              '%(lineno)d | ' +
                              '%(levelname)s | ' +
                              '%(message)s')

# logger = logging.getLogger('log')
# handler = logging.FileHandler(LOG)
# handler.setFormatter(formatter)
# logger.addHandler(handler)
# logger.setLevel(logging.INFO)

app_logger = logging.getLogger('app log')
app_handler = logging.FileHandler(APP_LOG)
app_handler.setFormatter(formatter)
app_logger.addHandler(app_handler)
app_logger.setLevel(logging.INFO)

scrape_logger = logging.getLogger('scrape log')
scrape_handler = logging.FileHandler(SCRAPE_LOG)
scrape_handler.setFormatter(formatter)
scrape_logger.addHandler(scrape_handler)
scrape_logger.setLevel(logging.INFO)

if args.verbose:
    # logger.setLevel(logging.DEBUG)
    app_logger.setLevel(logging.DEBUG)
    scrape_logger.setLevel(logging.DEBUG)
else:
    # logger.setLevel(logging.INFO)
    app_logger.setLevel(logging.INFO)
    scrape_logger.setLevel(logging.INFO)
