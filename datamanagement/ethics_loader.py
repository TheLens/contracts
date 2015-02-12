import datetime as dt
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Date, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from ethics_classes import EthicsRecord
import ConfigParser
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from dateutil import parser
import csv


Base = declarative_base()

CONFIG_LOCATION = '/apps/contracts/app.cfg'

def get_from_config(field):
    config = ConfigParser.RawConfigParser()
    config.read(CONFIG_LOCATION)
    return config.get('Section1', field)

server = get_from_config('server')
databasepassword = get_from_config('databasepassword')
user = get_from_config('user')
database = get_from_config('database')

engine = create_engine('postgresql://abe:' + databasepassword + '@' + server + ':5432/' +  database)
Session = sessionmaker(bind=engine)
Session.configure(bind=engine)
session = Session()

with open('20150209AllEfiledCFContributions.tab', 'rU') as csvfile:
	spamreader = csv.reader(csvfile, delimiter='\t', quotechar='"')
	for items in spamreader:
		try:
			r = EthicsRecord([i.strip().decode('ascii', 'ignore').encode('ascii', 'ignore') for i in items])
			session.add(r)
			session.flush()
		except:
			pass
session.commit()