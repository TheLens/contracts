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

if USER == 'ubuntu':  # Server
    CORPUS_LOC = "%s/backups/contracts" % PROJECT_DIR
    DOC_CLOUD_USERNAME = os.environ.get('DOCUMENT_CLOUD_USERNAME')
    DOC_CLOUD_PASSWORD = os.environ.get('DOCUMENT_CLOUD_PASSWORD')
    ROOT_FOLDER = "/home/%s" % USER
    LOG_PATH = "/home/%s/contracts/logs/contracts.log" % USER

    VENDORS_LOCATION = CORPUS_LOC + "/vendors/"
    PURCHASE_ORDER_LOCATION = CORPUS_LOC + "/purchaseorders/"
    BIDS_LOCATION = CORPUS_LOC + "/bids/"
    CONNECTION_STRING = 'postgresql://%s:%s@%s:5432/%s' % (
        os.environ.get('DATABASE_USERNAME'),
        os.environ.get('DATABASE_PASSWORD'),
        os.environ.get('DATABASE_SERVER'),
        os.environ.get('DATABASE_NAME'),
    )
    TEMPLATES = "%s/templates" % PROJECT_DIR
else:  # Local
    CORPUS_LOC = "%s/backups/contracts" % PROJECT_DIR
    DOC_CLOUD_USERNAME = os.environ.get('DOCUMENT_CLOUD_USERNAME')
    DOC_CLOUD_PASSWORD = os.environ.get('DOCUMENT_CLOUD_PASSWORD')
    ROOT_FOLDER = "/Users/%s" % USER
    LOG_PATH = "/Users/%s/projects/contracts/logs/contracts.log" % USER

    VENDORS_LOCATION = CORPUS_LOC + "/vendors/"
    PURCHASE_ORDER_LOCATION = CORPUS_LOC + "/purchaseorders/"
    BIDS_LOCATION = CORPUS_LOC + "/bids/"
    CONNECTION_STRING = 'postgresql://%s:%s@%s:5432/%s' % (
        os.environ.get('DATABASE_USERNAME'),
        os.environ.get('DATABASE_PASSWORD'),
        os.environ.get('DATABASE_SERVER'),
        os.environ.get('DATABASE_NAME'),
    )
    TEMPLATES = "%s/contracts/templates" % PROJECT_DIR

    BANNER_CSS = '/static/css/banner.css'
    CONTRACTS_CSS = '/static/css/contracts.css'

    LENS_JS = '/static/js/lens.js'
    CONTRACTS_JS = '/static/js/contracts.js'

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
