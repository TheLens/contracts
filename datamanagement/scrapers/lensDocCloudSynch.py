#At end of this, DB will be synched with DC. All will be backed up. Ready for new stuff. 
import ConfigParser
from sqlalchemy import create_engine
from documentcloud import DocumentCloud
from sqlalchemy.orm import sessionmaker
import argparse

from contracts.datamanagement.lib.vaultclasses import Vendor, Department, Contract
from contracts.datamanagement.lib.models import add_vendor
from contracts.datamanagement.lib.models import add_department

parser = argparse.ArgumentParser(description='Synch the lens db to ducment cloud repo')
parser.add_argument('--force', dest='keep_synching', action='store_true', help="try to synch the whole db, not just the newest")
parser.set_defaults(feature=False)
args = parser.parse_args()
force = args.keep_synching

from ... settings import Settings

s = Settings()


def get_from_config(field):
    config = ConfigParser.RawConfigParser()
    config.read(CONFIG_LOCATION)
    return config.get('Section1', field)


engine = create_engine('postgresql://' + user + ':' + databasepassword + '@' + server + ':5432/' + database)
Session = sessionmaker(bind=engine)
session = Session()


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
		vendor = doc.data["vendor"].replace(".", "")
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
	addVendor(vendor.replace(".", ""))

	department = session.query(Department).filter(Department.name==department).first().id
	vendorid = session.query(Vendor).filter(Vendor.name==vendor).first().id

	if session.query(Contract).filter(Contract.purchaseordernumber==purchaseno).count() == 0:
		contract = Contract(purchaseno)
		keep_synching = True
	else:
		contract = session.query(Contract).filter(Contract.purchaseordernumber==purchaseno).first()
		keep_synching = False

	contract.contractnumber=contractno
	contract.doc_cloud_id = doc.id
	contract.vendorid = vendorid
	contract.departmentid = department
	contract.dateadded = dateadded
	contract.title = title
	contract.description = description
	session.add(contract)
	session.flush()
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


if __name__ == "__main__":
    matchLensDBtoDocumentCloud()