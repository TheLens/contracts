#!/usr/bin/python

"""
This script backs up a local file system with everything from the DocumentCloud
repo.
"""

import os
import time
import json
import argparse

from contracts.datamanagement.lib.models import LensDatabase
from pythondocumentcloud import DocumentCloud
from pythondocumentcloud.toolbox import DoesNotExistError
from contracts import log, CORPUS_LOC

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
force = args.keep_synching

with LensDatabase() as lens_db:
    DOC_CLOUD_IDS = lens_db.get_all_contract_ids()

client = DocumentCloud()


def get_path(doc_cloud_id, extension):
    '''
    Return the appropriate path for a file with a certain extension.
    '''

    output = CORPUS_LOC + "/" + doc_cloud_id.replace("/", "") + extension
    return output


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


def needs_to_be_backed_up(doc_cloud_id):
    '''
    Boolean value indicating if contract needs to be backed up.
    '''

    if not os.path.exists(get_path(doc_cloud_id, ".pdf")):
        return True

    if not os.path.exists(get_path(doc_cloud_id, ".txt")):
        return True

    if not os.path.exists(get_path(doc_cloud_id, "_text.txt")):
        return True

    return False


def backup(doc_cloud_id):
    '''
    Backup a contract.
    '''

    if needs_to_be_backed_up(doc_cloud_id) or force:
        log.info(" {} | {}".format(
            time.strftime("%H:%M:%S"), "BACKUP " + doc_cloud_id))
        doc = client.documents.get(doc_cloud_id)
        pdf = doc.pdf
        metadata = get_meta_data(doc)
        if not os.path.exists(get_path(doc_cloud_id, ".pdf")) or force:
            pdf = doc.pdf
            with open(get_path(doc_cloud_id, ".pdf"), "wb") as outfile:
                outfile.write(pdf)

        if not os.path.exists(get_path(doc_cloud_id, ".txt")) or force:
            with open(get_path(doc_cloud_id, ".txt"), "wb") as outfile:
                outfile.write(json.dumps(metadata))

        if not os.path.exists(get_path(doc_cloud_id, "_text.txt")) or force:
            with open(get_path(doc_cloud_id, "_text.txt"), "wb") as outfile:
                outfile.write(json.dumps(doc.full_text))
    else:
        log.info(" {} | {}".format(
            time.strftime("%H:%M:%S"),
            doc_cloud_id + " already is backed up"))

if __name__ == "__main__":
    for document_cloud_id in DOC_CLOUD_IDS:
        try:
            backup(document_cloud_id)
        except DoesNotExistError:
            log.info(" {} | {}".format(
                time.strftime("%H:%M:%S"),
                document_cloud_id + " DoesNotExistError"))
