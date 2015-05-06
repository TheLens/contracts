#!/usr/bin/python

"""
Holds the settings so that they are accessible to other classes.
Actual configurations are stored in /configs/contracts.cfg, outside the repo.
In other words: the actual configurations are not posted to github!
"""
import ConfigParser
import os
import logging


def get_from_config(field):
    config = ConfigParser.RawConfigParser()
    config.read(CONFIG_LOCATION)
    return config.get('Section1', field)

CONFIG_LOCATION = "/configs/contracts.cfg"
server = get_from_config('server')
databasepassword = get_from_config('databasepassword')
user = get_from_config('user')
corpus_loc = get_from_config('corpus_loc')
database = get_from_config('database')
doc_cloud_user = get_from_config('doc_cloud_user')
doc_cloud_password = get_from_config('doc_cloud_password')
root_folder = get_from_config('root_folder')
log_folder = get_from_config('log_location')
to_list = get_from_config('to_list')
sender = get_from_config('sender')
gmail_user = get_from_config('gmail_user')
email_pw = get_from_config('email_pw')
vendors_location = corpus_loc + "/vendors/"
purchase_order_location = corpus_loc + "/purchaseorders/"
bids_location = corpus_loc + "/bids/"
connection_string = 'postgresql://' + \
    user + ':' + databasepassword + \
    '@' + server + ':5432/' + database
templates = root_folder + "/contracts/templates"

# Logging
if os.path.isfile(log_folder):
    os.remove(log_folder)

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

# Create file handler which logs debug messages or higher
filehandler = logging.FileHandler(log_folder)
filehandler.setLevel(logging.DEBUG)

# Create formatter and add it to the handlers
formatter = logging.Formatter(
    '%(asctime)s - %(filename)s - %(funcName)s - ' +
    '%(levelname)s - %(lineno)d - %(message)s')
filehandler.setFormatter(formatter)

# Add the handlers to the logger
log.addHandler(filehandler)
