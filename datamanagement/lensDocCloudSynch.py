'''
Matches the lens db with document cloud
'''
import ConfigParser
import logging
import argparse
import datetime


from documentcloud import DocumentCloud
from contracts.lib.vaultclasses import Vendor, Department, Contract
from contracts.settings import Settings
from contracts.datamanagement.lib.models import LensDatabase

SETTINGS = Settings()
logging.basicConfig(level=logging.DEBUG, filename=SETTINGS.log)

parser = argparse.ArgumentParser(description='Synch the lens db to ducment cloud repo')
parser.add_argument('--force', dest='keep_synching', action='store_true', help="try to synch the whole db, not just the newest")
parser.set_defaults(feature=False)
args = parser.parse_args()
force = args.keep_synching

client = DocumentCloud()


def get_from_metadata(doc, field):
    try:
        output = doc.data[field]
        if len(output)==0:
        	output = "unknown"
    except:
        output = "unknown"
    return output


def match_contract(doc):
    '''
    Match a particular contract
    '''
    keep_synching = True 
    log_string = '{} | Synching {}'.format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), doc.id)
    logging.info(log_string)
    with LensDatabase() as lens_db: 
        purchaseno = get_from_metadata(doc, "purchase order")
        contractno = get_from_metadata(doc, "contract number")
        vendor = get_from_metadata(doc, "vendor").replace(".", "")
        department = get_from_metadata(doc, "department").replace(".", "")

        dateadded = doc.created_at
        title = doc.title
        description = doc.description

        lens_db.add_department(department)
        lens_db.add_vendor(vendor)

        department = lens_db.get_department_id(department)
        vendorid = lens_db.get_lens_vendor_id(vendor)

        if not lens_db.has_contract(purchaseno):
            contract = Contract(purchaseno)
            keep_synching = True
        else:
            contract = lens_db.get_contract(purchaseno)
            keep_synching = False

        contract.contractnumber = contractno
        contract.doc_cloud_id = doc.id
        contract.vendorid = vendorid
        contract.departmentid = department
        contract.dateadded = dateadded
        contract.title = title
        contract.description = description
        lens_db.add_contract(contract)

    return keep_synching


def matchLensDBtoDocumentCloud():
    '''
    Match the Lens database to document cloud
    '''
    docs = client.documents.search('projectid: 1542-city-of-new-orleans-contracts')
    keep_synching = True

    for i in range(0,len(docs)):   #loop thru docs. assumption is document cloud returns newist first (it does)
        if keep_synching or force:          #if newest is not in the db, keep looking
            keep_synching = match_contract(docs[i])
        else:
            break   #else end the loop


if __name__ == '__main__':
    matchLensDBtoDocumentCloud()
