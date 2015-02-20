import datetime
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Date, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
import ConfigParser

Base = declarative_base()

CONFIG_LOCATION = '/apps/contracts/app.cfg'

def get_from_config(field):
    config = ConfigParser.RawConfigParser()
    config.read(CONFIG_LOCATION)
    return config.get('Section1', field)

server = get_from_config('server')
databasepassword = get_from_config('databasepassword')
user = get_from_config('user')


class EthicsRecord(Base):
	__tablename__ = 'ethics_records'

	id = Column(Integer, primary_key=True)
	last = Column(String)
	first = Column(String)
	reportno = Column(String)
	form = Column(String)
	schedule = Column(String)
	contributiontype = Column(String)
	contributorname = Column(String)
	address1 = Column(String)
	address2 = Column(String)
	city = Column(String)
	state = Column(String)
	zipcode = Column(String)
	receiptdate = Column(String)
	receiptamount = Column(String)
	description = Column(String)

	def __init__(self, name):
		self.last = last
		self.first = first
		self.reportno = reportno
		self.form = form
		self.schedule = schedule
		self.contributiontype = contributiontype
		self.contributorname = contributorname
		self.address1 = address1
		self.address2 = address2
		self.city = city
		self.state = state
		self.zipcode = zipcode
		self.receiptdate = receiptdate
		self.receiptamount = receiptamount
		self.description = description


	def __str__(self):
		return "${} to {} {} on {}".format(self.receiptamount, self.first, self.last, self.receiptdate)


	def __repr__(self):
		return "${} to {} {} on {}".format(self.receiptamount, self.first, self.last, self.receiptdate)

def remakeDB():
	engine = create_engine('postgresql://' + user + ':' + databasepassword + '@' + server + ':5432/thevault')
	Base.metadata.create_all(engine)

remakeDB()
#CREATE UNIQUE INDEX uniquename ON basics (first, last);
