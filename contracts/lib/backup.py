
"""
This script backs up a local file system with everything from the DocumentCloud
repo.
"""

import os
# import time
import json
import argparse

from contracts.lib.lens_database import LensDatabase
from pythondocumentcloud import DocumentCloud
from pythondocumentcloud.toolbox import DoesNotExistError
from contracts import log, CORPUS_LOC


class Backup(object):

    def __init__(self):
        parser = argparse.ArgumentParser(
            description='Synch the lens db to document cloud repo')
        parser.add_argument(
            '--force',
            dest='keep_synching',
            action='store_true',
            help="try to synch the whole db, not just the newest"
        )

        parser.set_defaults(feature=False)
        args = parser.parse_args()
        self.force = args.keep_synching

        self.DOC_CLOUD_IDS = LensDatabase().get_all_contract_ids()

        self.client = DocumentCloud()

    @staticmethod
    def get_path(doc_cloud_id, extension):
        '''
        Return the appropriate path for a file with a certain extension.
        '''

        output = CORPUS_LOC + "/" + doc_cloud_id.replace("/", "") + extension
        return output

    @staticmethod
    def get_meta_data(doc):
        '''
        Return the metadata associated with a DocumentCloud contract.
        '''

        metadata = {}

        try:
            metadata['vendor'] = doc.data['vendor']
        except KeyError:
            metadata['vendor'] = "unknown"

        try:
            metadata['department'] = doc.data['department']
        except KeyError:
            metadata['department'] = "unknown"

        try:
            metadata['contract number'] = doc.data['contract number']
        except KeyError:
            metadata['contract number'] = ""

        try:
            metadata['purchase order'] = doc.data['purchase order']
        except KeyError:
            metadata['purchase order'] = ""

        metadata['title'] = doc.title
        metadata['description'] = doc.description

        return metadata

    def needs_to_be_backed_up(self, doc_cloud_id):
        '''
        Boolean value indicating if contract needs to be backed up.
        '''

        if not os.path.exists(self.get_path(doc_cloud_id, ".pdf")):
            return True
        elif not os.path.exists(self.get_path(doc_cloud_id, ".txt")):
            return True
        elif not os.path.exists(self.get_path(doc_cloud_id, "_text.txt")):
            return True
        else:
            return False

    def backup(self, doc_cloud_id):
        '''
        Backup a contract.
        '''

        if self.needs_to_be_backed_up(doc_cloud_id) or self.force:
            log.info("{}".format("BACKUP " + doc_cloud_id))
            doc = self.client.documents.get(doc_cloud_id)
            pdf = doc.pdf
            metadata = self.get_meta_data(doc)
            path_check = os.path.exists(self.get_path(doc_cloud_id, ".pdf"))
            if not path_check or self.force:
                pdf = doc.pdf
                file_path = self.get_path(doc_cloud_id, ".pdf")
                with open(file_path, "wb") as outfile:
                    outfile.write(pdf)

            path_check = os.path.exists(self.get_path(doc_cloud_id, ".txt"))
            if not path_check or self.force:
                file_path = self.get_path(doc_cloud_id, ".txt")
                with open(file_path, "wb") as outfile:
                    outfile.write(json.dumps(metadata))

            path_check = os.path.exists(
                self.get_path(doc_cloud_id, "_text.txt"))
            if not path_check or self.force:
                file_path = self.get_path(doc_cloud_id, "_text.txt")
                with open(file_path, "wb") as outfile:
                    outfile.write(json.dumps(doc.full_text))
        else:
            log.info("{}".format(doc_cloud_id + " already is backed up"))


if __name__ == "__main__":
    for document_cloud_id in Backup().DOC_CLOUD_IDS:
        try:
            Backup().backup(document_cloud_id)
        except DoesNotExistError:
            log.info("{}".format(document_cloud_id + " DoesNotExistError"))
