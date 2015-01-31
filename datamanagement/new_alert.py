import sys
import math
import pprint
import re
import datetime
import ConfigParser
sys.path.append('datamanagement')
from flask import Flask
from flask import render_template, make_response, send_from_directory
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import desc
from flask.ext.cache import Cache
from vaultclasses import Vendor, Department, Contract, Person, VendorOfficer
from documentcloud import DocumentCloud


CONFIG_LOCATION = '/apps/contracts/app.cfg'

def get_from_config(field):
    config = ConfigParser.RawConfigParser()
    config.read(CONFIG_LOCATION)
    return config.get('Section1', field)

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

today_string = datetime.datetime.now().strftime('%Y-%m-%d')

contracts = session.query(Contract).filter(Contract.dateadded==today_string).all()
print contracts

session.close()