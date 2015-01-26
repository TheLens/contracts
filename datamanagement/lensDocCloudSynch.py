#At end of this, DB will be synched with DC. All will be backed up. Ready for new stuff. 
import ConfigParser
from sqlalchemy import create_engine
from documentcloud import DocumentCloud
from sqlalchemy.orm import sessionmaker
from vaultclasses import Vendor, Department, Contract
import argparse

parser = argparse.ArgumentParser(description='Synch the lens db to ducment cloud repo')
parser.add_argument('--force', dest='keep_synching', action='store_true', help="try to synch the whole db, not just the newest")
parser.set_defaults(feature=False)
args = parser.parse_args()
force = args.keep_synching

CONFIG_LOCATION = '/apps/contracts/app.cfg'

client = DocumentCloud()

def get_from_config(field):
    config = ConfigParser.RawConfigParser()
    config.read(CONFIG_LOCATION)
    return config.get('Section1', field)

databasepassword = get_from_config('databasepassword')
server = get_from_config('server')
database = get_from_config('database')
user = get_from_config('user')

server = "projects.thelensnola.org"
engine = create_engine('postgresql://' + user + ':' + databasepassword + '@' + server + ':5432/' + database)
Session = sessionmaker(bind=engine)
session = Session()

def addVendor(vendor):

	c = session.query(Vendor).filter(Vendor.name==vendor).count()
	if len(vendor)>0 and c==0:
		x = Vendor(vendor)
		session.add(x)
		session.commit()
	session.close()

def addDepartment(department):
	c = session.query(Department).filter(Department.name==department).count()
	if len(department)>0 and c==0:
		x = Department(department)
		session.add(x)
		session.commit()
	session.close()

def match_contract(doc):
	keep_synching = True; 
	print "adding {}".format(doc.id)

	try:
		purchaseno = doc.data["purchase order"]
	except:
		purchaseno = "unknown"

	try:
		contractno = doc.data["contract number"]
	except:
		contractno = "unknown"

	try:
		vendor = doc.data["vendor"]
		if len(vendor)==0:
			vendor="unknown"
	except:
		vendor = "unknown"

	try:
		department = doc.data["department"]
		if len(department)==0:
			department="unknown"
	except:
		department = "unknown"

	dateadded = doc.created_at
	title = doc.title
	description = doc.description

	addDepartment(department)
	addVendor(vendor)

	department = session.query(Department).filter(Department.name==department).first().id
	vendorid = session.query(Vendor).filter(Vendor.name==vendor).first().id

	if session.query(Contract).filter(Contract.purchaseordernumber==purchaseno).count() == 0:
		contract = Contract(purchaseno)
		keep_synching = True
	else:
		contract = session.query(Contract).filter(Contract.purchaseordernumber==purchaseno).first()
		keep_synching = False

	contract.contractno=contractno
	contract.doc_cloud_id = doc.id
	contract.vendorid = vendorid
	contract.department = department
	contract.dateadded = dateadded
	contract.title = title
	contract.description = description
	session.add(contract)
	session.commit()
	return keep_synching


def matchLensDBtoDocumentCloud():

	docs = client.documents.search('projectid: 1542-city-of-new-orleans-contracts')
	keep_synching = True

	for i in range(0,len(docs)):   #loop thru docs. assumption is document cloud returns newist first (it does)
		if keep_synching or force:          #if newest is not in the db, keep looking
			keep_synching = match_contract(docs[i])
		else:
			break   #else end the loop

matchLensDBtoDocumentCloud()