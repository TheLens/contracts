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


class RichmondRecord(Base):
	__tablename__ = 'richmond'

	id = Column(Integer, primary_key=True)
	seat = Column(String)
	committee_ext_id = Column(String)
	seat_held = Column(String)
	recipient_party = Column(String)
	transaction_type_description = Column(String)
	recipient_type = Column(String)
	seat_status = Column(String)
	recipient_state = Column(String)
	contributor_category = Column(String)
	contributor_gender = Column(String)
	contributor_state = Column(String)
	recipient_category = Column(String)
	is_amendment = Column(String)
	organization_name = Column(String)
	recipient_ext_id = Column(String)
	parent_organization_name = Column(String)
	contributor_address = Column(String)
	transaction_id = Column(String)
	contributor_occupation = Column(String)
	filing_id = Column(String)
	contributor_city = Column(String)
	district_held = Column(String)
	recipient_name = Column(String)
	recipient_state_held = Column(String) 
	district_held = Column(String)
	recipient_name = Column(String)
	organization_ext_id = Column(String)
	contributor_zipcode = Column(String) 
	transaction_namespace = Column(String)
	date = Column(String)
	committee_name = Column(String)
	candidacy_status = Column(String)
	parent_organization_ext_id = Column(String)
	cycle = Column(String)
	contributor_name = Column(String) 
	contributor_type = Column(String)
	contributor_employer = Column(String)
	seat_result = Column(String)
	transaction_type = Column(String) 
	amount = Column(String) 
	contributor_ext_id = Column(String) 
	committee_party = Column(String) 

	def __init__(self, params):
		self.seat = params[0]
		self.committee_ext_id = params[1]
		self.seat_held = params[2]
		self.recipient_party = params[3]
		self.transaction_type_description = params[4]
		self.recipient_type = params[5]
		self.seat_status = params[6]
		self.recipient_state = params[7]
		self.contributor_category = params[8]
		self.contributor_gender = params[9]
		self.contributor_state = params[10]
		self.recipient_category = params[11]
		self.is_amendment = params[12]
		self.organization_name = params[13]
		self.recipient_ext_id = params[14]
		self.parent_organization_name = params[15]
		self.contributor_address = params[16]
		self.transaction_id = params[17]
		self.contributor_occupation = params[18]
		self.filing_id = params[19]
		self.contributor_city = params[20]
		self.district_held = params[21]
		self.recipient_name = params[22]
		self.recipient_state_held = params[23] 
		self.district_held = params[24]
		self.recipient_name = params[25]
		self.organization_ext_id = params[26]
		self.contributor_zipcode = params[27] 
		self.transaction_namespace = params[28]
		self.date = params[29]
		self.committee_name = params[30]
		self.candidacy_status = params[31]
		self.parent_organization_ext_id = params[32]
		self.cycle = params[33]
		self.contributor_name = params[34] 
		self.contributor_type = params[35]
		self.contributor_employer = params[36]
		self.seat_result = params[37]
		self.transaction_type = params[38] 
		self.amount = params[39] 
		self.contributor_ext_id = params[40] 
		self.committee_party = params[41] 


'''

class LandrieuRecord(Base):
	__tablename__ = 'landrieu'

	id = Column(Integer, primary_key=True)
	seat = Column(String)
	committee_ext_id = Column(String)
	seat_held = Column(String)
	recipient_party = Column(String)
	transaction_type_description = Column(String)
	recipient_type = Column(String)
	seat_status = Column(String)
	recipient_state = Column(String)
	contributor_category = Column(String)
	contributor_gender = Column(String)
	contributor_state = Column(String)
	recipient_category = Column(String)
	is_amendment = Column(String)
	organization_name = Column(String)
	recipient_ext_id = Column(String)
	parent_organization_name = Column(String)
	contributor_address = Column(String)
	transaction_id = Column(String)
	contributor_occupation = Column(String)
	filing_id = Column(String)
	contributor_city = Column(String)
	district_held = Column(String)
	recipient_name = Column(String)
	recipient_state_held = Column(String) 
	district_held = Column(String)
	recipient_name = Column(String)
	organization_ext_id = Column(String)
	contributor_zipcode = Column(String) 
	transaction_namespace = Column(String)
	date = Column(String)
	committee_name = Column(String)
	candidacy_status = Column(String)
	parent_organization_ext_id = Column(String)
	cycle = Column(String)
	contributor_name = Column(String) 
	contributor_type = Column(String)
	contributor_employer = Column(String)
	seat_result = Column(String)
	transaction_type = Column(String) 
	amount = Column(String) 
	contributor_ext_id = Column(String) 
	committee_party = Column(String) 

	def __init__(self, params):
		self.seat = params[0]
		self.committee_ext_id = params[1]
		self.seat_held = params[2]
		self.recipient_party = params[3]
		self.transaction_type_description = params[4]
		self.recipient_type = params[5]
		self.seat_status = params[6]
		self.recipient_state = params[7]
		self.contributor_category = params[8]
		self.contributor_gender = params[9]
		self.contributor_state = params[10]
		self.recipient_category = params[11]
		self.is_amendment = params[12]
		self.organization_name = params[13]
		self.recipient_ext_id = params[14]
		self.parent_organization_name = params[15]
		self.contributor_address = params[16]
		self.transaction_id = params[17]
		self.contributor_occupation = params[18]
		self.filing_id = params[19]
		self.contributor_city = params[20]
		self.district_held = params[21]
		self.recipient_name = params[22]
		self.recipient_state_held = params[23] 
		self.district_held = params[24]
		self.recipient_name = params[25]
		self.organization_ext_id = params[26]
		self.contributor_zipcode = params[27] 
		self.transaction_namespace = params[28]
		self.date = params[29]
		self.committee_name = params[30]
		self.candidacy_status = params[31]
		self.parent_organization_ext_id = params[32]
		self.cycle = params[33]
		self.contributor_name = params[34] 
		self.contributor_type = params[35]
		self.contributor_employer = params[36]
		self.seat_result = params[37]
		self.transaction_type = params[38] 
		self.amount = params[39] 
		self.contributor_ext_id = params[40] 
		self.committee_party = params[41] 

	def __repr__(self):
		self.return "<Department(Department='%s')>" % (self.department)

'''

def remakeDB():
	engine = create_engine('postgresql://' + user + ':' + databasepassword + '@' + server + ':5432/thevault')
	Base.metadata.create_all(engine)

remakeDB()
#CREATE UNIQUE INDEX uniquename ON basics (first, last);
