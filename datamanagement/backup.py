import os, time, json
from documentcloud import DocumentCloud

import datetime as dt
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from vaultclasses import Contract
import ConfigParser
from sqlalchemy import desc
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from dateutil import parser
import csv

import argparse

parser = argparse.ArgumentParser(description='Synch the lens db to ducment cloud repo')
parser.add_argument('--force', dest='keep_synching', action='store_true', help="try to synch the whole db, not just the newest")
parser.set_defaults(feature=False)
args = parser.parse_args()
force = args.keep_synching


Base = declarative_base()

CONFIG_LOCATION = '/apps/contracts/app.cfg'

def get_from_config(field):
    config = ConfigParser.RawConfigParser()
    config.read(CONFIG_LOCATION)
    return config.get('Section1', field)

server = get_from_config('server')
databasepassword = get_from_config('databasepassword')
user = get_from_config('user')
database = get_from_config('database')

engine = create_engine('postgresql://abe:' + databasepassword + '@' + server + ':5432/' +  database)
Session = sessionmaker(bind=engine)
Session.configure(bind=engine)
session = Session()

def get_all_contract_ids():
	dcids = [i[0] for i in session.query(Contract.doc_cloud_id).order_by(desc(Contract.dateadded)).all()]
	return dcids

doc_cloud_ids = get_all_contract_ids()

client = DocumentCloud()

BASEBACKUP = "/Volumes/usb/"
LOGFILE = "/Volumes/usb/log.txt"

with open(LOGFILE, "a") as f:
	f.writelines(",".join((time.strftime("%H:%M:%S"),"BACKUP", "START")))


def getMetaData(doc):
	metadata={}
	try:
		metadata['vendor'] = doc.data['vendor']
	except:
		metadata['vendor'] = "unknown"
	try:
		metadata['department'] = doc.data['department']
	except:
		metadata['department'] = "unknown"
	metadata['contract number'] = doc.data['contract number']
	metadata['purchase order'] = doc.data['purchase order']
	metadata['title'] = doc.title
	metadata['description'] = doc.description
	return metadata


def needs_to_be_backed_up(doc_cloud_id):
	if not os.path.exists(BASEBACKUP + "/" + doc_cloud_id.replace("/","") + ".pdf"):
		return True

	if not os.path.exists(BASEBACKUP + "/" + doc_cloud_id.replace("/","") + ".txt"):
		return True

	if not os.path.exists(BASEBACKUP + "/" + doc_cloud_id.replace("/","") + "_text" + ".txt"):
		return True

	return False

def backup(doc_cloud_id):
	if needs_to_be_backed_up(doc_cloud_id) or force:
		print "{} needs to be backed up".format(doc_cloud_id)
		doc = client.documents.get(doc_cloud_id)
		pdf = doc.pdf
		metadata = getMetaData(doc)
		if not os.path.exists(BASEBACKUP + "/" + doc_cloud_id.replace("/","") + ".pdf"):
			pdf = doc.pdf
			with open(BASEBACKUP + "/" + doc_cloud_id.replace("/","") + ".pdf", "wb") as f:
				f.write(pdf)

		if not os.path.exists(BASEBACKUP + "/" + doc_cloud_id.replace("/","") + ".txt"):
			with open(BASEBACKUP + "/" + doc_cloud_id.replace("/","") + ".txt", "wb") as f:
				f.write(json.dumps(metadata))

		if not os.path.exists(BASEBACKUP + "/" + doc_cloud_id.replace("/","") + "_text" + ".txt"):
			with open(BASEBACKUP + "/" + doc_cloud_id.replace("/","") + "_text", "wb") as f:
				f.write(json.dumps(doc.full_text))

for doc_cloud_id in doc_cloud_ids:
	print "checking {}".format(doc_cloud_id)
	backup(doc_cloud_id)

session.close()