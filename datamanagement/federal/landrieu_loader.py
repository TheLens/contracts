import datetime as dt
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Date, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from federal_classes import RichmondRecord
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

counter = 0

with open('landrieu.csv', 'rU') as csvfile:
	spamreader = csv.reader(csvfile, delimiter=',', quotechar='"')
	for items in spamreader:
		try:
			r = RichmondRecord([i.strip().decode('ascii', 'ignore').encode('ascii', 'ignore') for i in items])
			session.add(r)
			session.flush()
			counter = counter + 1
		except:
			pass
		if counter % 1000 == 0: 
			session.commit()
			print counter 
			counter = 0

session.commit()