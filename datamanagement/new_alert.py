import sys
import math
import pprint
import re
import time
import ConfigParser
sys.path.append('datamanagement')
from flask import Flask
from flask import render_template, make_response, send_from_directory
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from flask.ext.cache import Cache
from vaultclasses import Vendor, Department, Contract, Person, VendorOfficer
from documentcloud import DocumentCloud


CONFIG_LOCATION = '/apps/contracts/app.cfg'

def get_from_config(field):
    config = ConfigParser.RawConfigParser()
    config.read(CONFIG_LOCATION)
    return config.get('Section1', field)

PAGELENGTH = 8

app = Flask(__name__)
cache = Cache(app, config={'CACHE_TYPE': 'simple'})
documentCloudClient = DocumentCloud()

server = get_from_config('server')
databasepassword = get_from_config('databasepassword')
user = get_from_config('user')
dc_query = 'projectid: "1542-city-of-new-orleans-contracts"'

engine = create_engine('postgresql://abe:' + databasepassword + '@' + server + ':5432/thevault')
Session = sessionmaker(bind=engine)
Session.configure(bind=engine)
session = Session()
contracts = session.query(Contract).order_by(Contract.dateadded.desc()).first()
print contracts
session.close()