'''
Matches the lens db with document cloud
'''
import ConfigParser
import logging
import datetime

from documentcloud import DocumentCloud
from contracts.lib.vaultclasses import Vendor, Department, Contract
from contracts.settings import Settings
from contracts.datamanagement.lib.models import LensDatabase

SETTINGS = Settings()
logging.basicConfig(level=logging.DEBUG, filename=SETTINGS.log)

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
        fields = {}
        fields['purchaseno'] = get_from_metadata(doc, "purchase order")
        fields['contractno'] = get_from_metadata(doc, "contract number")
        fields['vendor'] = get_from_metadata(doc, "vendor").replace(".", "")
        fields['department'] = get_from_metadata(doc, "vendor").replace(".", "")
        fields['dateadded'] = doc.created_at
        fields['title'] = doc.title
        fields['description'] = doc.description
        lens_db.add_department(fields['department'])
        lens_db.add_vendor(fields['vendor'])
        fields['department'] = lens_db.get_department_id(fields['department'])
        fields['vendor'] = lens_db.get_lens_vendor_id(fields['vendor'])
        lens_db.update_contract_from_doc_cloud_doc(doc.id, fields)

    return keep_synching


def matchLensDBtoDocumentCloud():
    '''
    Match the Lens database to document cloud
    '''
    with LensDatabase() as db:
        for c in db.get_half_filled_contracts():
            try:
                match_contract(client.documents.get(c.doc_cloud_id))
            except documentcloud.toolbox.DoesNotExistError:
                print c.doc_cloud_id + 'is not quite ready yet'
                log_string = '{} | DC still processing {}'.format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), c.doc_cloud_id)


if __name__ == '__main__':
    matchLensDBtoDocumentCloud()
