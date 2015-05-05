import os
import time
import json
import datetime as dt
import csv
import logging
import argparse

from documentcloud import DocumentCloud
from documentcloud import DoesNotExistError
from contracts.settings import Settings
from sqlalchemy import create_engine
from vaultclasses import Contract
from sqlalchemy import desc
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from dateutil import parser

parser = argparse.ArgumentParser(description='Synch the lens db to ducment cloud repo')
parser.add_argument('--force', dest='keep_synching', action='store_true', help="try to synch the whole db, not just the newest")
parser.set_defaults(feature=False)
args = parser.parse_args()
force = args.keep_synching

SETTINGS = Settings()

engine = create_engine(SETTINGS.connection_string)
Session = sessionmaker(bind=engine)
Session.configure(bind=engine)
session = Session()


def get_all_contract_ids():
    dcids = [i[0] for i in session.query(Contract.doc_cloud_id).order_by(desc(Contract.dateadded)).all()]
    return dcids

doc_cloud_ids = get_all_contract_ids()

client = DocumentCloud()

BASEBACKUP = SETTINGS.corpus_loc

logging.basicConfig(level=logging.DEBUG, filename=SETTINGS.log)

logging.info(" {} | {}".format(time.strftime("%H:%M:%S"), "BACKUP START"))


def getMetaData(doc):
    '''
    return the metadata associated with a 
    document cloud contract
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
    Boolean value indicating if contract needs to be backed up
    '''
    if not os.path.exists(BASEBACKUP + "/" + doc_cloud_id.replace("/", "") + ".pdf"):
        return True

    if not os.path.exists(BASEBACKUP + "/" + doc_cloud_id.replace("/", "") + ".txt"):
        return True

    if not os.path.exists(BASEBACKUP + "/" + doc_cloud_id.replace("/", "") + "_text.txt"):
        return True

    return False


def backup(doc_cloud_id):
    '''
    Backup a contract
    '''
    if needs_to_be_backed_up(doc_cloud_id) or force:
        logging.info(" {} | {}".format(time.strftime("%H:%M:%S"), "BACKUP " + doc_cloud_id))
        doc = client.documents.get(doc_cloud_id)
        pdf = doc.pdf
        metadata = getMetaData(doc)
        if not os.path.exists(BASEBACKUP + "/" + doc_cloud_id.replace("/", "") + ".pdf") or force:
            pdf = doc.pdf
            with open(BASEBACKUP + "/" + doc_cloud_id.replace("/", "") + ".pdf", "wb") as outfile:
                outfile.write(pdf)

        if not os.path.exists(BASEBACKUP + "/" + doc_cloud_id.replace("/", "") + ".txt") or force:
            with open(BASEBACKUP + "/" + doc_cloud_id.replace("/", "") + ".txt", "wb") as outfile:
                outfile.write(json.dumps(metadata))

        if not os.path.exists(BASEBACKUP + "/" + doc_cloud_id.replace("/", "") + "_text.txt") or force:
            with open(BASEBACKUP + "/" + doc_cloud_id.replace("/", "") + "_text.txt", "wb") as outfile:
                outfile.write(json.dumps(doc.full_text))
    else:
        logging.info(" {} | {}".format(time.strftime("%H:%M:%S"), doc_cloud_id + " already is backed up"))


for doc_cloud_id in doc_cloud_ids:
    try:
        backup(doc_cloud_id)
    except NotImplementedError:
        pass

session.close()
