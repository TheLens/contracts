
'''
This script backs up a local file system with everything from the DocumentCloud
project. These go to /backups/contracts/documents on the server.
This is different from local_backup.sh, which then copies this local
file repository to a remote file repository (ex. server to local).
'''

import argparse
import json
import os

from pythondocumentcloud import DocumentCloud
from pythondocumentcloud.toolbox import DoesNotExistError
from contracts.lib.lens_database import LensDatabase
from contracts import DOCUMENT_CLOUD_DIR, log


class Backup(object):

    '''Keeps a local file system backup of DocumentCloud project.'''

    def __init__(self):
        parser = argparse.ArgumentParser(
            description='Sync the local database to DocumentCloud project.')
        parser.add_argument(
            '--force',
            dest='keep_synching',
            action='store_true',
            help="Sync the entire database, not just the newest records."
        )

        parser.set_defaults(feature=False)
        args = parser.parse_args()
        self.force = args.keep_synching

        self.client = DocumentCloud()

        document_cloud_ids = LensDatabase().get_all_contract_ids()

        for document_cloud_id in document_cloud_ids:
            try:
                self._backup(document_cloud_id)
            except DoesNotExistError:
                log.exception("DoesNotExistError: %s", document_cloud_id)

    def __str__(self):
        return '{}'.format(self.__class__.__name__)

    def __repr__(self):
        return '{}()'.format(self.__class__.__name__)

    def _backup(self, document_cloud_id):
        '''Backup a contract.'''
        needs_backup = self._needs_to_be_backed_up(document_cloud_id)

        if needs_backup or self.force:
            log.info("Creating backup for %s", document_cloud_id)

            document = self.client.documents.get(document_cloud_id)
            metadata = self._get_meta_data(document)

            pdf_path = self._get_path(document_cloud_id, ".pdf")
            pdf_exists = os.path.exists(pdf_path)
            if not pdf_exists or self.force:
                pdf = document.pdf
                with open(pdf_path, "wb") as outfile:
                    outfile.write(pdf)

            txt_path = self._get_path(document_cloud_id, ".txt")
            txt_exists = os.path.exists(txt_path)
            if not txt_exists or self.force:
                with open(txt_path, "wb") as outfile:
                    outfile.write(json.dumps(metadata))

            text_txt_path = self._get_path(document_cloud_id, "_text.txt")
            text_txt_exists = os.path.exists(text_txt_path)
            if not text_txt_exists or self.force:
                with open(text_txt_path, "wb") as outfile:
                    outfile.write(json.dumps(document.full_text))
        else:
            log.info("%s is already is backed up", document_cloud_id)

    @staticmethod
    def _get_path(document_cloud_id, extension):
        '''Return the appropriate path for a file with a certain extension.'''
        path = "%s/%s%s" % (
            DOCUMENT_CLOUD_DIR,
            document_cloud_id.replace("/", ""),
            extension
        )

        return path

    @staticmethod
    def _get_meta_data(document):
        '''Return the metadata associated with a DocumentCloud contract.'''
        metadata = {}

        try:
            metadata['vendor'] = document.data['vendor']
        except KeyError:
            metadata['vendor'] = "unknown"

        try:
            metadata['department'] = document.data['department']
        except KeyError:
            metadata['department'] = "unknown"

        try:
            metadata['contract number'] = document.data['contract number']
        except KeyError:
            metadata['contract number'] = ""

        try:
            metadata['purchase order'] = document.data['purchase order']
        except KeyError:
            metadata['purchase order'] = ""

        metadata['title'] = document.title
        metadata['description'] = document.description

        return metadata

    def _needs_to_be_backed_up(self, document_cloud_id):
        '''
        Boolean value indicating if contract needs to be backed up.

        :params document_cloud_id: The contract's DocumentCloud ID.
        :type document_cloud_id: string.
        :returns: boolean. True if this needs to be backed up, False if not.
        '''

        # if not os.path.exists(self._get_path(document_cloud_id, ".pdf")):
        #     return True
        # elif not os.path.exists(self._get_path(document_cloud_id, ".txt")):
        #     return True
        # elif not os.path.exists(self._get_path(doc_cloud_id, "_text.txt")):
        #     return True
        # else:
        #     return False

        condition = (
            os.path.exists(self._get_path(document_cloud_id, ".pdf")) and
            os.path.exists(self._get_path(document_cloud_id, ".txt")) and
            os.path.exists(self._get_path(document_cloud_id, "_text.txt"))
        )
        if condition:
            return False
        else:
            return True

if __name__ == "__main__":
    Backup()
