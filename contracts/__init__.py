#!/usr/bin/python

'''
Holds the settings so that they are accessible to other classes.
All private information is stored in environment variables and should never
be written into files in this repo.
'''

import os
from datetime import date
import logging
import logging.handlers
import getpass

# Project directory paths
PROJECT_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..'))

PROJECT_URL = 'http://vault.thelensnola.org/contracts'

# Common variables
TODAY_DATE_STRING = date.today().strftime('%Y-%m-%d')
TODAY_DATE = date.today()

# Parserator
TAGS_URL = '%s/data/tags.json' % PROJECT_DIR  # JSON for parserator tokens.
XML_LOCATION = '%s/data/parseratorxml' % PROJECT_DIR
NUMBER_WORDS_LOCATION = '%s/parser/number_words.txt' % PROJECT_DIR

# DocumentCloud
DOC_CLOUD_USERNAME = os.environ.get('DOCUMENT_CLOUD_USERNAME')
DOC_CLOUD_PASSWORD = os.environ.get('DOCUMENT_CLOUD_PASSWORD')

# Database
DATABASE_NAME = 'contracts'
DATABASE_SERVER = 'localhost'
CONNECTION_STRING = 'postgresql://%s:%s@%s:5432/%s' % (
    os.environ.get('DATABASE_USERNAME'),
    os.environ.get('DATABASE_PASSWORD'),
    DATABASE_SERVER,
    DATABASE_NAME,
)
CAMPAIGN_CONNECTION_STRING = 'postgresql://%s:%s@%s:5432/%s' % (
    os.environ.get('DATABASE_USERNAME'),
    os.environ.get('DATABASE_PASSWORD'),
    DATABASE_SERVER,
    'campaigncontributions',
)

USER = getpass.getuser()

if USER == 'ubuntu':  # Server
    CORPUS_LOC = '/backups/contracts'

    S3_URL = 'https://s3-us-west-2.amazonaws.com/lensnola/contracts'

    # CSS
    BANNER_CSS = '%s/css/banner.css' % S3_URL
    CONTRACTS_CSS = '%s/css/contracts.css' % S3_URL
    LENS_CSS = '%s/css/lens.css' % S3_URL

    # JavaScript
    LENS_JS = '%s/js/lens.js' % S3_URL
    PARSERATOR_JS = '%s/js/parserator.js' % S3_URL
    RESULTS_JS = '%s/js/results.js' % S3_URL
    SEARCH_JS = '%s/js/search.js' % S3_URL

    # Flask config
    RELOADER = False
    DEBUG = False
elif USER == 'abe':  # Local
    CORPUS_LOC = '%s/backups/contracts' % PROJECT_DIR

    S3_URL = 'https://s3-us-west-2.amazonaws.com/lensnola/contracts'

    # CSS
    BANNER_CSS = '%s/css/banner.css' % S3_URL
    CONTRACTS_CSS = '%s/css/contracts.css' % S3_URL
    LENS_CSS = '%s/css/lens.css' % S3_URL

    # JavaScript
    LENS_JS = '%s/js/lens.js' % S3_URL
    PARSERATOR_JS = '%s/js/parserator.js' % S3_URL
    RESULTS_JS = '%s/js/results.js' % S3_URL
    SEARCH_JS = '%s/js/search.js' % S3_URL

    # Flask config
    RELOADER = False
    DEBUG = False
else:  # USER == 'thomasthoren' or Read the Docs
    CORPUS_LOC = '%s/data' % PROJECT_DIR

    # CSS
    BANNER_CSS = '/static/css/banner.css'
    CONTRACTS_CSS = '/static/css/contracts.css'
    LENS_CSS = '/static/css/lens.css'

    # JavaScript
    LENS_JS = '/static/js/lens.js'
    PARSERATOR_JS = '/static/js/parserator.js'
    RESULTS_JS = '/static/js/results.js'
    SEARCH_JS = '/static/js/search.js'

    # Flask config
    RELOADER = True
    DEBUG = True

ATTACHMENTS_DIR = '%s/attachments' % CORPUS_LOC
DOCUMENTS_DIR = '%s/documents' % CORPUS_LOC
DOCUMENT_CLOUD_DIR = '%s/document-cloud' % CORPUS_LOC
PURCHASE_ORDER_DIR = '%s/purchase-orders' % CORPUS_LOC
VENDORS_DIR = '%s/vendors' % CORPUS_LOC

# Logging
LOG_PATH = '%s/logs/contracts.log' % PROJECT_DIR

if os.path.isfile(LOG_PATH):  # TODO: Remove this once live.
    os.remove(LOG_PATH)

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

# Create file handler which logs debug messages or higher
filehandler = logging.FileHandler(LOG_PATH)
filehandler.setLevel(logging.DEBUG)

# Create formatter and add it to the handlers
formatter = logging.Formatter(
    '%(asctime)s | %(filename)s | %(funcName)s | ' +
    '%(levelname)s | %(lineno)d | %(message)s')
filehandler.setFormatter(formatter)

# Add the handlers to the logger
log.addHandler(filehandler)
