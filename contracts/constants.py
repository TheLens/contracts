#!/usr/bin/python

'''
Holds the settings so that they are accessible to other classes.
All private information is stored in environment variables and should never
be written into files in this repo.
'''

import getpass
import logging
import logging.handlers
import os
import random
import string
import sys

from datetime import date, datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

__VERSION__ = '1.0.0'

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

PROJECT_URL = 'http://vault.thelensnola.org/contracts'

# Common variables
TODAY_DATE_STRING = date.today().strftime('%Y-%m-%d')
TODAY_DATE = date.today()

# Parserator
TAGS_URL = os.path.join(PROJECT_DIR, 'data/tags.json')
XML_LOCATION = os.path.join(PROJECT_DIR, 'data/parseratorxml')
NUMBER_WORDS_LOCATION = os.path.join(PROJECT_DIR, 'parser/number_words.txt')

# DocumentCloud
DOC_CLOUD_USERNAME = os.environ.get('DOCUMENT_CLOUD_USERNAME')
DOC_CLOUD_PASSWORD = os.environ.get('DOCUMENT_CLOUD_PASSWORD')

# Database
CONTRACTS_DATABASE_NAME = 'contracts'
CONTRACTS_DATABASE_SERVER = 'localhost'
CONNECTION_STRING = 'postgresql://{}:{}@{}:5432/{}'.format(
    os.environ.get('CONTRACTS_DATABASE_USERNAME'),
    os.environ.get('CONTRACTS_DATABASE_PASSWORD'),
    CONTRACTS_DATABASE_SERVER,
    CONTRACTS_DATABASE_NAME)

CAMPAIGN_CONNECTION_STRING = 'postgresql://{}:{}@{}:5432/{}'.format(
    os.environ.get('CONTRACTS_DATABASE_USERNAME'),
    os.environ.get('CONTRACTS_DATABASE_PASSWORD'),
    CONTRACTS_DATABASE_SERVER,
    'campaigncontributions')

# Data files
CORPUS_LOC = os.path.join(PROJECT_DIR, 'data')

ATTACHMENTS_DIR = os.path.join(CORPUS_LOC, 'attachments')
DOCUMENTS_DIR = os.path.join(CORPUS_LOC, 'documents')
DOCUMENT_CLOUD_DIR = os.path.join(CORPUS_LOC, 'document-cloud')
PURCHASE_ORDER_DIR = os.path.join(CORPUS_LOC, 'purchase-orders')
VENDORS_DIR = os.path.join(CORPUS_LOC, 'vendors')

USER = getpass.getuser()

if USER == 'ubuntu':  # Server
    STATIC_ASSET_PATH = 'https://s3-us-west-2.amazonaws.com/lensnola/contracts'

    # Flask config
    RELOADER = False
    DEBUG = False
else:
    STATIC_ASSET_PATH = '/static'

    # Flask config
    RELOADER = True
    DEBUG = True

# CSS
BANNER_CSS = os.path.join(STATIC_ASSET_PATH, 'css/banner.css')
CONTRACTS_CSS = os.path.join(STATIC_ASSET_PATH, 'css/contracts.css')
LENS_CSS = os.path.join(STATIC_ASSET_PATH, 'css/lens.css')

# JavaScript
LENS_JS = os.path.join(STATIC_ASSET_PATH, 'js/lens.js')
PARSERATOR_JS = os.path.join(STATIC_ASSET_PATH, 'js/parserator.js')
RESULTS_JS = os.path.join(STATIC_ASSET_PATH, 'js/results.js')
SEARCH_JS = os.path.join(STATIC_ASSET_PATH, 'js/search.js')

# SQLAlchemy session
engine = create_engine(CONNECTION_STRING)
sn = sessionmaker(bind=engine)
SESSION = sn()  # Import this to any files that need database

engine = create_engine(CAMPAIGN_CONNECTION_STRING)
campaign_sn = sessionmaker(bind=engine)
CAMPAIGN_SESSION = campaign_sn()

# Logging

log_uuid = ''.join(random.choice(string.ascii_lowercase) for x in range(6))
log_timestamp = datetime.now().strftime('%Y-%d-%m-%H-%M-%S.%f')
log_file_name = '{}.{}.log'.format(log_timestamp, log_uuid)

LOG_FILE = os.path.join(PROJECT_DIR, 'logs', log_file_name)
LOG_PATH = LOG_FILE

if not os.path.exists(os.path.dirname(LOG_PATH)):
    os.makedirs(os.path.dirname(LOG_PATH))

if not os.path.isfile(LOG_PATH):
    open(LOG_PATH, 'w').close()

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

# Create file handler which logs debug messages or higher
filehandler = logging.handlers.RotatingFileHandler(
    LOG_PATH,
    maxBytes=(5 * 1024 * 1024),  # 5 MB
    backupCount=5  # TODO
)
filehandler.setLevel(logging.DEBUG)

# Create formatter and add it to the handlers
formatter = logging.Formatter(
    '%(asctime)s | %(module)s.%(funcName)s | ' +
    '%(levelname)s | %(lineno)d | %(message)s')
filehandler.setFormatter(formatter)

# Add the handlers to the logger
log.addHandler(filehandler)
