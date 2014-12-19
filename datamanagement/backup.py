import os, time, json
from documentcloud import DocumentCloud

client = DocumentCloud()
docs = client.documents.search('projectid: 1542-city-of-new-orleans-contracts')

BASEBACKUP = "/backups/contracts"
LOGFILE = "/backups/contracts"

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


def backup(doc):
	pdf = doc.pdf
	metadata = getMetaData(doc)
	if not os.path.exists(BASEBACKUP + "/" +doc.id.replace("/","") + ".pdf"):
		pdf = doc.pdf
		with open(BASEBACKUP + "/" +doc.id.replace("/","") + ".pdf", "wb") as f:
			f.write(pdf)
			with open(LOGFILE, "a") as f:
				f.writelines(",".join((time.strftime("%H:%M:%S"),"BACKUP","Saving PDF:" + BASEBACKUP + "/" +doc.id.replace("/","") + ".pdf")))

	if not os.path.exists(BASEBACKUP + "/" +doc.id.replace("/","") + ".txt"):
		with open(BASEBACKUP + "/" +doc.id.replace("/","") + ".txt", "wb") as f:
			f.write(json.dumps(metadata))


for doc in docs:
	try:
		backup(doc)
	except:
		pass