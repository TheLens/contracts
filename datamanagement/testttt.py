import sys
import math
import pprint
import re
import time
import ConfigParser
from ethics_classes import EthicsRecord
sys.path.append('datamanagement')
from flask import Flask
from flask import render_template, make_response, send_from_directory
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from flask.ext.cache import Cache
from vaultclasses import Vendor, Department, Contract, Person, VendorOfficer
from documentcloud import DocumentCloud
from sqlalchemy import func

from sqlalchemy.ext.declarative import declarative_base


CONFIG_LOCATION = '/apps/contracts/app.cfg'


def get_from_config(field):
    config = ConfigParser.RawConfigParser()
    config.read(CONFIG_LOCATION)
    return config.get('Section1', field)


server = get_from_config('server')
databasepassword = get_from_config('databasepassword')
user = get_from_config('user')
database = get_from_config('database')


Base = declarative_base()
# an Engine, which the Session will use for connection
engine = create_engine('postgresql://' + user + ':' + databasepassword + '@' + server + ':5432/' + database)
# create a configured "Session" class
Session = sessionmaker(bind=engine)
# create a Session
session = Session()


def get_records(name):
	recccs = session.query(EthicsRecord).filter(EthicsRecord.contributorname==name).all()
	recccs.sort(key = lambda x: x.receiptdate)
	return recccs

print get_records('BURCH & ASSOCIATES HENRY J.')