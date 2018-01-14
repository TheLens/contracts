'''Sync the local database with DocumentCloud.'''

from pythondocumentcloud import DocumentCloud
from contracts.lib.lens_database import LensDatabase
from contracts import scrape_log as log


class SyncLocalDatabaseDocumentCloud(object):

    '''Syncs the local database with our DocumentCloud project.'''

    def __init__(self):
        '''Initialize with the Python-DocumentCloud object.'''

        self.client = DocumentCloud()

    @staticmethod
    def _get_metadata(document, field):
        '''Fetch this metadata from our DocumentCloud project.'''

        try:
            output = document.data[field]
            if len(output) == 0:
                output = "unknown"
        except Exception as e:
            log.error(e, exc_info=True)
            output = "unknown"

        return output

    def _match_contract(self, document):
        '''
        Match a particular contract. TODO: Better description

        :params document: A Python-DocumentCloud object representing a contract
        :type document: Python-DocumentCloud object.
        '''
        log.info('Syncing document %s', document.id)

        fields = {}
        fields['purchaseno'] = self._get_metadata(document, "purchase order")
        fields['contractno'] = self._get_metadata(document, "contract number")
        fields['vendor'] = self._get_metadata(document, "vendor").replace(".", "")
        fields['department'] = self._get_metadata(document, "vendor").replace(".", "")
        fields['dateadded'] = document.created_at
        fields['title'] = document.title
        fields['description'] = document.description

        LensDatabase().add_department(fields['department'])
        LensDatabase().add_vendor(fields['vendor'])

        fields['department'] = LensDatabase().get_department_id(fields['department'])
        fields['vendor'] = LensDatabase().get_lens_vendor_id(fields['vendor'])

        LensDatabase().update_contract_from_document_cloud(document.id, fields)

    def match_local_database_to_document_cloud(self):
        '''
        Match our local database to our DocumentCloud project.

        TODO: Why fetching half-filled contracts?
        '''

        half_filled_contracts = LensDatabase().get_half_filled_contracts()
        log.info('%d half-filled contracts need to be synced',
                 len(half_filled_contracts))

        for half_filled_contract in half_filled_contracts:
            try:
                contract = self.client.documents.get(
                    half_filled_contract.doc_cloud_id
                )
                self._match_contract(contract)
            except Exception as e:
                log.error(e, exc_info=True)

if __name__ == '__main__':
    SyncLocalDatabaseDocumentCloud().match_local_database_to_document_cloud()
