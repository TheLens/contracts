#!/usr/bin/python

'''
Holds the settings so that they are accessible to other classes.
All private information is stored in environment variables and should never
be written into files in this repo.
'''

import getpass
import os

from datetime import date

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from logger import logger as log

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
CONTRACTS_DATABASE_NAME = 'contracts'
CONTRACTS_DATABASE_SERVER = 'localhost'
CONNECTION_STRING = 'postgresql://{0}:{1}@{2}:5432/{3}'.format(
    os.environ.get('CONTRACTS_DATABASE_USERNAME'),
    os.environ.get('CONTRACTS_DATABASE_PASSWORD'),
    CONTRACTS_DATABASE_SERVER,
    CONTRACTS_DATABASE_NAME)

CAMPAIGN_CONNECTION_STRING = 'postgresql://%s:%s@%s:5432/%s' % (
    os.environ.get('CONTRACTS_DATABASE_USERNAME'),
    os.environ.get('CONTRACTS_DATABASE_PASSWORD'),
    CONTRACTS_DATABASE_SERVER,
    'campaigncontributions',
)

# Data files
CORPUS_LOC = '%s/data' % PROJECT_DIR

ATTACHMENTS_DIR = '%s/attachments' % CORPUS_LOC
DOCUMENTS_DIR = '%s/documents' % CORPUS_LOC
DOCUMENT_CLOUD_DIR = '%s/document-cloud' % CORPUS_LOC
PURCHASE_ORDER_DIR = '%s/purchase-orders' % CORPUS_LOC
VENDORS_DIR = '%s/vendors' % CORPUS_LOC

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
BANNER_CSS = '%s/css/banner.css' % STATIC_ASSET_PATH
CONTRACTS_CSS = '%s/css/contracts.css' % STATIC_ASSET_PATH
LENS_CSS = '%s/css/lens.css' % STATIC_ASSET_PATH

# JavaScript
LENS_JS = '%s/js/lens.js' % STATIC_ASSET_PATH
PARSERATOR_JS = '%s/js/parserator.js' % STATIC_ASSET_PATH
RESULTS_JS = '%s/js/results.js' % STATIC_ASSET_PATH
SEARCH_JS = '%s/js/search.js' % STATIC_ASSET_PATH

# SQLAlchemy session
engine = create_engine(CONNECTION_STRING)
sn = sessionmaker(bind=engine)
SESSION = sn()  # Import this to any files that need database

engine = create_engine(CAMPAIGN_CONNECTION_STRING)
campaign_sn = sessionmaker(bind=engine)
CAMPAIGN_SESSION = campaign_sn()
