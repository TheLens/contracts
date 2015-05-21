
'''
Matches the Lens database with DocumentCloud.
'''

from pythondocumentcloud import DocumentCloud
from contracts.lib.models import LensDatabase
from contracts import log

client = DocumentCloud()


def get_from_metadata(doc, field):
    '''docstring'''

    try:
        output = doc.data[field]
        if len(output) == 0:
            output = "unknown"
    except:
        output = "unknown"

    return output


def match_contract(doc):
    '''
    Match a particular contract.
    '''

    keep_synching = True
    log_string = 'Synching {}'.format(
        doc.id)
    log.info(log_string)
    with LensDatabase() as lens_db:
        fields = {}
        fields['purchaseno'] = get_from_metadata(doc, "purchase order")
        fields['contractno'] = get_from_metadata(doc, "contract number")
        fields['vendor'] = get_from_metadata(doc, "vendor").replace(".", "")
        fields['department'] = get_from_metadata(
            doc, "vendor").replace(".", "")
        fields['dateadded'] = doc.created_at
        fields['title'] = doc.title
        fields['description'] = doc.description
        lens_db.add_department(fields['department'])
        lens_db.add_vendor(fields['vendor'])
        fields['department'] = lens_db.get_department_id(fields['department'])
        fields['vendor'] = lens_db.get_lens_vendor_id(fields['vendor'])
        lens_db.update_contract_from_doc_cloud_doc(doc.id, fields)

    return keep_synching


def match_lens_db_to_document_cloud():
    '''
    Match the Lens database to DocumentCloud.

    DocumentCloud can take anywhere from one minute to 30 minutes to cache new
    uploads and reflect their changes in its API.

    This checks DocumentCloud to make sure that the latest changes have been
    synched.
    '''

    with LensDatabase() as db:
        half_filled_contracts = db.get_half_filled_contracts()
        log.info(
            '%d half filled contracts need to be synched',
            len(half_filled_contracts))
        for contract in half_filled_contracts:
            try:
                match_contract(client.documents.get(contract.doc_cloud_id))
            except Exception, ex:
                template = "An exception of type {0} occured. " + \
                    "Arguments:\n{1!r}"
                message = template.format(type(ex).__name__, ex.args)
                print message
                print contract.doc_cloud_id
                log_string = '{} | Error {}'.format(
                    contract.doc_cloud_id, message)
                log.info(log_string)

if __name__ == '__main__':
    match_lens_db_to_document_cloud()
