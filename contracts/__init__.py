#!/usr/bin/python

"""
Holds the settings so that they are accessible to other classes.
All private information is stored in environment variables and should never
be written into files in this repo.
"""

import os
import logging
import logging.handlers
import getpass

USER = getpass.getuser()
PROJECT_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..'))

LOG_PATH = "%s/logs/contracts.log" % PROJECT_DIR
XML_LOCATION = "%s/data/parseratorxml" % PROJECT_DIR

# this stores the json that describes the tags for parserator tokens
TAGS_URL = "%s/data/tags.json" % PROJECT_DIR

DOC_CLOUD_USERNAME = os.environ.get('DOCUMENT_CLOUD_USERNAME')
DOC_CLOUD_PASSWORD = os.environ.get('DOCUMENT_CLOUD_PASSWORD')

S3_URL = "https://s3-us-west-2.amazonaws.com/lensnola/contracts"
TEMPLATES = "%s/contracts/templates" % PROJECT_DIR
NUMBER_WORDS_LOCATION = '%s/parser/number_words.txt' % PROJECT_DIR

CONNECTION_STRING = 'postgresql://%s:%s@%s:5432/%s' % (
    os.environ.get('DATABASE_USERNAME'),
    os.environ.get('DATABASE_PASSWORD'),
    os.environ.get('DATABASE_SERVER'),
    os.environ.get('DATABASE_NAME'),
)

if USER == 'ubuntu':  # Server
    CORPUS_LOC = "/backups/contracts"
    ROOT_FOLDER = "/home/%s" % USER

    # Static assets
    LENS_CSS = '%s/css/lens.css' % S3_URL
    BANNER_CSS = '%s/css/banner.css' % S3_URL
    CONTRACTS_CSS = '%s/css/contracts.css' % S3_URL

    DOWNLOAD_JS = '%s/js/download.js' % S3_URL
    LENS_JS = '%s/js/lens.js' % S3_URL
    RESULTS_JS = '%s/js/results.js' % S3_URL
    SEARCH_JS = '%s/js/search.js' % S3_URL

    # app.py config
    RELOADER = False
    DEBUG = False

if USER == 'abe':  # Server
    CORPUS_LOC = "%s/backups/contracts" % PROJECT_DIR
    ROOT_FOLDER = "/home/%s" % USER

    TEMPLATES = "%s/templates" % PROJECT_DIR

    # Static assets
    LENS_CSS = '%s/css/lens.css' % S3_URL
    BANNER_CSS = '%s/css/banner.css' % S3_URL
    CONTRACTS_CSS = '%s/css/contracts.css' % S3_URL

    DOWNLOAD_JS = '%s/js/download.js' % S3_URL
    LENS_JS = '%s/js/lens.js' % S3_URL
    RESULTS_JS = '%s/js/results.js' % S3_URL
    SEARCH_JS = '%s/js/search.js' % S3_URL

    # app.py config
    RELOADER = False
    DEBUG = False

if USER == 'thomasthoren':  # Tom's Local
    CORPUS_LOC = "/Volumes/External HDD/contracts-backup"
    ROOT_FOLDER = "/Users/%s" % USER

    # Static assets
    LENS_CSS = '/static/css/lens.css'
    BANNER_CSS = '/static/css/banner.css'
    CONTRACTS_CSS = '/static/css/contracts.css'

    DOWNLOAD_JS = '/static/js/download.js'
    LENS_JS = '/static/js/lens.js'
    RESULTS_JS = '/static/js/results.js'
    SEARCH_JS = '/static/js/search.js'

    # app.py config
    RELOADER = True
    DEBUG = True

# These must go after user-specific definitions, since they rely on them:
VENDORS_LOCATION = CORPUS_LOC + "/vendors/"
PURCHASE_ORDER_LOCATION = CORPUS_LOC + "/purchaseorders/"
BIDS_LOCATION = CORPUS_LOC + "/bids/"

# Logging
if os.path.isfile(LOG_PATH):
    os.remove(LOG_PATH)

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

# Create file handler which logs debug messages or higher
filehandler = logging.FileHandler(LOG_PATH)
filehandler.setLevel(logging.DEBUG)

# Create formatter and add it to the handlers
formatter = logging.Formatter(
    '%(asctime)s - %(filename)s - %(funcName)s - ' +
    '%(levelname)s - %(lineno)d - %(message)s')
filehandler.setFormatter(formatter)

# Add the handlers to the logger
log.addHandler(filehandler)
