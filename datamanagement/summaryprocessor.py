#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import csv
import pprint
import sys
import sqlalchemy.exc
import urllib2
import re
import os
import subprocess
import sqlalchemy.exc
import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from vaultclasses import Contract
from bs4 import BeautifulSoup
from vaultclasses import Contract, Vendor, Department
import datetime
import subprocess
import os
import re
from bs4 import BeautifulSoup
import ConfigParser
import traceback
import smtplib
from documentcloud import DocumentCloud

ATTACHMENTSPATH = "/data/attachments"
PURCHASEORDERPATH = "/data/purchaseorders"
PURCHASEORDERPROCESSED = "/data/purchaseorders/processed"
NOCONTRACTNO = "/data/errors/nocontractno"
SYSTEMERROR = "/data/errors/systemerror"

CONFIG_LOCATION = '/apps/contracts/app.cfg'

def sendEmail(title, message):
    to = to_list
    gmail_user = sender
    gmail_pwd = pw
    smtpserver = smtplib.SMTP('smtp.gmail.com', 587)
    smtpserver.ehlo()
    smtpserver.starttls()
    smtpserver.ehlo
    smtpserver.login(gmail_user, gmail_pwd)
    header = 'To:' + to + '\n' + 'From: ' + gmail_user + '\n' \
        + 'Subject:' + title + '\n'
    msg = header + message
    smtpserver.sendmail(gmail_user, to, msg)
    smtpserver.close()


def processPurchaseOrder(soup):
    if isSystemError(soup):
        print 'error: system error from cityofno ' + filename
        return   # to do:
    metadata = extractMetaData(soup)
    output += '''
metadata
'''
    output += ', \n'.join('%s=%r' % (key, val) for (key, val) in
                          metadata.iteritems())
    if len(metadata.get('contract number')) < 1:
        print 'no contract number='
        dest = '/data/errors/nocontractno/' + os.path.basename(filename)
        print filename
        print dest
        os.rename(filename, dest)  # the summary has been processed
        output += '\nError: no contract number ' + filename
        return output
    if not DocumentCloud.hasContract(metadata):
        print 'New contract'
        metadata = getAttachments(metadata)
        new_id = DocumentCloud.uploadContract(metadata)
        newURL = new_id.canonical_url
        title = new_id.title
        output = title + '\n' + newURL + '\n' + output
        dest = "/data/purchaseorders/processed" + '/' + os.path.basename(filename)
        os.rename(filename, dest)  # the summary has been processed
        output += '''Successful upload: ''' + filename
    else:
        if DocumentCloud.hasContract(metadata):
            print 'update metadata'
            DocumentCloud.uploadMetadata(metadata)
            dest = "/data/purchaseorders/processed" + '/' \
                + os.path.basename(filename)
            if not os.path.exists(dest):
                os.rename(filename, dest)  # the summary has been processed
            else:
                os.remove(filename)
            output += \
                '\nUpdated meta data only. Contract already exists on Document Cloud: ' \
                + filename
    return output


def isSystemError(soup):
    if len(soup.find_all('td', text='System problem')) > 0:
        return True
    return False


def getVendor(soup):
    vendorrow = soup(text=re.compile(r'Vendor:'))[0].parent.parent
    vendorlinktext = vendorrow.findChildren(['td'])[1].findChildren(['a'
            ])[0].contents.pop().strip()
    vendor = vendorlinktext.split('-')[1].strip()
    return vendor

def getVendorId(soup):


def getDepartment(soup):
    mainTable = soup.select('.table-01').pop()
    metadatarow = mainTable.findChildren(['tr'])[2].findChildren(['td'])[0].findChildren(['table'])[0].findChildren(['tr'])
    department = metadatarow[5].findChildren(['td'])[1].contents.pop().strip()
    return department

def extractMetaData(soup):
    mainTable = soup.select('.table-01').pop()
    metadatarow = mainTable.findChildren(['tr'])[2].findChildren(['td'
            ])[0].findChildren(['table'])[0].findChildren(['tr'])
    purchaseOrder = metadatarow[1].findChildren(['td'
            ])[1].contents.pop().strip()
    department = metadatarow[5].findChildren(['td'
            ])[1].contents.pop().strip()

    try:
        knumber = metadatarow[6].findChildren(['td'])[1].contents.pop().replace('k', '').replace("m", '').strip()
    except:
        knumber = purchaseOrder
        tracking = "k=pw"

    if len(knumber)==0:
        knumber=purchaseOrder
    vendor = getVendor(soup)
    description = metadatarow[1].findChildren(['td'
            ])[5].contents.pop().strip()

    todownload = metadatarow[16].findChildren(['td'
            ])[1].findChildren(['a'])

    if knumber == 'n/a':  # on occasions they list the k number as "n/a". if so, just use the p number as a the k number
        knumber = purchaseOrder
    return {
        'purchaseOrder': purchaseOrder,
        'department': department,
        'contract number': knumber.strip('M').strip('k').strip('M'
                ).strip('K'),
        'vendor': vendor,
        'description': description,
        'attachments': todownload,
        'LensTracking': tracking
        }


def getAttachments(metadata):
    attachments = []
    for a in metadata['attachments']:
        downloadFileName = metadata['purchaseOrder'] + '_' \
            + metadata['contract number'].replace('/', '') + '_' \
            + a.contents.pop().strip()
        downloadFileName = ATTACHMENTSPATH + '/' + downloadFileName.replace("/", "").replace(" ", "-")
        attachments.append(downloadFileName)
        bidnumber = re.search('[0-9]+', a.get('href')).group()  # bid number is different from purchase order. used by javascript in city's system to ID a doc
        if not os.path.exists(downloadFileName):
            subprocess.call([
                'curl',
                '-o',
                downloadFileName,
                'http://www.purchasing.cityofno.com/bso/external/document/attachments/attachmentFileDetail.sdo'
                    ,
                '-H',
                'Pragma: no-cache',
                '-H',
                'Origin: null',
                '-H',
                'Accept-Encoding: gzip,deflate,sdch',
                '-H',
                'Accept-Language: en-US,en;q=0.8',
                '-H',
                'Content-Type: multipart/form-data; boundary=----WebKitFormBoundaryP4a4C1okQYkBGBSG'
                    ,
                '-H',
                'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
                    ,
                '-H',
                'Connection: keep-alive',
                '--data-binary',
                '''------WebKitFormBoundaryP4a4C1okQYkBGBSG\r
Content-Disposition: form-data; name="mode"\r
\r
download\r
------WebKitFormBoundaryP4a4C1okQYkBGBSG\r
Content-Disposition: form-data; name="parentUrl"\r
\r
/external/purchaseorder/poSummary.sdo\r
------WebKitFormBoundaryP4a4C1okQYkBGBSG\r
Content-Disposition: form-data; name="parentId"\r
\r
\r
------WebKitFormBoundaryP4a4C1okQYkBGBSG\r
Content-Disposition: form-data; name="fileNbr"\r
\r
'''
                    + bidnumber
                    + '''\r
------WebKitFormBoundaryP4a4C1okQYkBGBSG\r
Content-Disposition: form-data; name="workingDir"\r
\r
\r
------WebKitFormBoundaryP4a4C1okQYkBGBSG\r
Content-Disposition: form-data; name="docId"\r
\r
4051927411\r
------WebKitFormBoundaryP4a4C1okQYkBGBSG\r
Content-Disposition: form-data; name="docType"\r
\r
P\r
------WebKitFormBoundaryP4a4C1okQYkBGBSG\r
Content-Disposition: form-data; name="docSubType"\r
\r
\r
------WebKitFormBoundaryP4a4C1okQYkBGBSG\r
Content-Disposition: form-data; name="releaseNbr"\r
\r
0\r
------WebKitFormBoundaryP4a4C1okQYkBGBSG\r
Content-Disposition: form-data; name="downloadFileNbr"\r
\r
'''
                    + bidnumber
                    + '''\r
------WebKitFormBoundaryP4a4C1okQYkBGBSG\r
Content-Disposition: form-data; name="itemNbr"\r
\r
0\r
------WebKitFormBoundaryP4a4C1okQYkBGBSG\r
Content-Disposition: form-data; name="currentPage"\r
\r
1\r
------WebKitFormBoundaryP4a4C1okQYkBGBSG\r
Content-Disposition: form-data; name="querySql"\r
\r
\r
------WebKitFormBoundaryP4a4C1okQYkBGBSG\r
Content-Disposition: form-data; name="sortBy"\r
\r
\r
------WebKitFormBoundaryP4a4C1okQYkBGBSG\r
Content-Disposition: form-data; name="sortByIndex"\r
\r
0\r
------WebKitFormBoundaryP4a4C1okQYkBGBSG\r
Content-Disposition: form-data; name="sortByDescending"\r
\r
false\r
------WebKitFormBoundaryP4a4C1okQYkBGBSG\r
Content-Disposition: form-data; name="revisionNbr"\r
\r
0\r
------WebKitFormBoundaryP4a4C1okQYkBGBSG\r
Content-Disposition: form-data; name="receiptId"\r
\r
\r
------WebKitFormBoundaryP4a4C1okQYkBGBSG\r
Content-Disposition: form-data; name="vendorNbr"\r
\r
\r
------WebKitFormBoundaryP4a4C1okQYkBGBSG\r
Content-Disposition: form-data; name="vendorGrp"\r
\r
\r
------WebKitFormBoundaryP4a4C1okQYkBGBSG\r
Content-Disposition: form-data; name="invoiceNbr"\r
\r
\r
------WebKitFormBoundaryP4a4C1okQYkBGBSG\r
Content-Disposition: form-data; name="displayName"\r
\r
Grainger Inc. Februaryl 2008.pdf\r
------WebKitFormBoundaryP4a4C1okQYkBGBSG--\r
''',
                '--compressed',
                ])
    metadata['attachments'] = attachments
    return metadata



def get_from_config(field):
    config = ConfigParser.RawConfigParser()
    config.read(CONFIG_LOCATION)
    return config.get('Section1', field)

doc_cloud_user = get_from_config('doc_cloud_user')
doc_cloud_password = get_from_config('doc_cloud_password')
databasepassword = get_from_config('databasepassword')
server = get_from_config('server')
database = get_from_config('database')
user = get_from_config('user')

documentCloudClient = DocumentCloud(doc_cloud_user, doc_cloud_password)
Base = declarative_base()
engine = create_engine('postgresql://' + user + ':' + databasepassword + '@' + server + ':5432/' + database)
Session = sessionmaker(bind=engine)
session = Session()

def hasPurchaseOrder(purchaseOrder):
    searchterm = '\'purchase order\':' + "'" + purchaseOrder + "'"
    if len(documentCloudClient.documents.search(searchterm))<1:
        return False; #it is a new purchase order
    return True; #it is an existing purchase order.


def uploadContract(file, data, description, title):
	if len(data['contract number'])<1:
		return #do not upload. There is a problem
	newid = documentCloudClient.documents.upload(file, title.replace("/", ""), 'City of New Orleans', description, None,'http://vault.thelensnola.org/contracts', 'public', '1542-city-of-new-orleans-contracts', data, False)
	return newid


#refactor to take a type
def addVendor(vendor):
	indb = session.query(Vendor).filter(Vendor.name==vendor).count()
	if indb==0:
		vendor = Vendor(vendor)
		session.add(vendor)
		session.commit()


def addDepartment(department):
	indb = session.query(Department).filter(Department.name==department).count()
	if indb==0:
		department = Department(department)
		session.add(department)
		session.commit()
		

#refactor to take a type
def getVendorID(vendor):
	session.flush()
	vendors = session.query(Vendor).filter(Vendor.name==vendor).all()
	vendor = vendors.pop()


def getDepartmentID(department):
	return session.query(Department).filter(Department.name==department).first().id


def downloadFile(bidno):
        if not os.path.exists(bidno):
            p = subprocess.Popen([
                'curl',
                '-o',
                bidno,
                'http://www.purchasing.cityofno.com/bso/external/document/attachments/attachmentFileDetail.sdo'
                    ,
                '-H',
                'Pragma: no-cache',
                '-H',
                'Origin: null',
                '-H',
                'Accept-Encoding: gzip,deflate,sdch',
                '-H',
                'Accept-Language: en-US,en;q=0.8',
                '-H',
                'Content-Type: multipart/form-data; boundary=----WebKitFormBoundaryP4a4C1okQYkBGBSG'
                    ,
                '-H',
                'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
                    ,
                '-H',
                'Connection: keep-alive',
                '--data-binary',
                '''------WebKitFormBoundaryP4a4C1okQYkBGBSG\r
Content-Disposition: form-data; name="mode"\r
\r
download\r
------WebKitFormBoundaryP4a4C1okQYkBGBSG\r
Content-Disposition: form-data; name="parentUrl"\r
\r
/external/purchaseorder/poSummary.sdo\r
------WebKitFormBoundaryP4a4C1okQYkBGBSG\r
Content-Disposition: form-data; name="parentId"\r
\r
\r
------WebKitFormBoundaryP4a4C1okQYkBGBSG\r
Content-Disposition: form-data; name="fileNbr"\r
\r
'''
                    + bidno
                    + '''\r
------WebKitFormBoundaryP4a4C1okQYkBGBSG\r
Content-Disposition: form-data; name="workingDir"\r
\r
\r
------WebKitFormBoundaryP4a4C1okQYkBGBSG\r
Content-Disposition: form-data; name="docId"\r
\r
4051927411\r
------WebKitFormBoundaryP4a4C1okQYkBGBSG\r
Content-Disposition: form-data; name="docType"\r
\r
P\r
------WebKitFormBoundaryP4a4C1okQYkBGBSG\r
Content-Disposition: form-data; name="docSubType"\r
\r
\r
------WebKitFormBoundaryP4a4C1okQYkBGBSG\r
Content-Disposition: form-data; name="releaseNbr"\r
\r
0\r
------WebKitFormBoundaryP4a4C1okQYkBGBSG\r
Content-Disposition: form-data; name="downloadFileNbr"\r
\r
'''
                    + bidno
                    + '''\r
------WebKitFormBoundaryP4a4C1okQYkBGBSG\r
Content-Disposition: form-data; name="itemNbr"\r
\r
0\r
------WebKitFormBoundaryP4a4C1okQYkBGBSG\r
Content-Disposition: form-data; name="currentPage"\r
\r
1\r
------WebKitFormBoundaryP4a4C1okQYkBGBSG\r
Content-Disposition: form-data; name="querySql"\r
\r
\r
------WebKitFormBoundaryP4a4C1okQYkBGBSG\r
Content-Disposition: form-data; name="sortBy"\r
\r
\r
------WebKitFormBoundaryP4a4C1okQYkBGBSG\r
Content-Disposition: form-data; name="sortByIndex"\r
\r
0\r
------WebKitFormBoundaryP4a4C1okQYkBGBSG\r
Content-Disposition: form-data; name="sortByDescending"\r
\r
false\r
------WebKitFormBoundaryP4a4C1okQYkBGBSG\r
Content-Disposition: form-data; name="revisionNbr"\r
\r
0\r
------WebKitFormBoundaryP4a4C1okQYkBGBSG\r
Content-Disposition: form-data; name="receiptId"\r
\r
\r
------WebKitFormBoundaryP4a4C1okQYkBGBSG\r
Content-Disposition: form-data; name="vendorNbr"\r
\r
\r
------WebKitFormBoundaryP4a4C1okQYkBGBSG\r
Content-Disposition: form-data; name="vendorGrp"\r
\r
\r
------WebKitFormBoundaryP4a4C1okQYkBGBSG\r
Content-Disposition: form-data; name="invoiceNbr"\r
\r
\r
------WebKitFormBoundaryP4a4C1okQYkBGBSG\r
Content-Disposition: form-data; name="displayName"\r
\r
Grainger Inc. Februaryl 2008.pdf\r
------WebKitFormBoundaryP4a4C1okQYkBGBSG--\r
''',
                '--compressed',
                ])
            p.wait()


def getVendor(soup):
	vendorrow = soup(text=re.compile(r'Vendor:'))[0].parent.parent
	vendorlinktext = vendorrow.findChildren(['td'])[1].findChildren(['a'
			])[0].contents.pop().strip()
	vendor = vendorlinktext.split('-')[1].strip().replace(".", "") #no periods in vendor names
	return vendor

def getDepartment(soup):
	mainTable = soup.select('.table-01').pop()
	metadatarow = mainTable.findChildren(['tr'])[2].findChildren(['td'])[0].findChildren(['table'])[0].findChildren(['tr'])
	department = metadatarow[5].findChildren(['td'])[1].contents.pop().strip()
	return department


def getKnumber(soup):
	mainTable = soup.select('.table-01').pop()
	metadatarow = mainTable.findChildren(['tr'])[2].findChildren(['td'])[0].findChildren(['table'])[0].findChildren(['tr'])
	try:
		knumber = metadatarow[6].findChildren(['td'])[1].contents.pop().replace('k', '').replace("m", '').strip()
	except:
		knumber = "unknown"
	return knumber


def getAttachmentQueue(soup):
	try:
		mainTable = soup.select('.table-01').pop()
		metadatarow = mainTable.findChildren(['tr'])[2].findChildren(['td'])[0].findChildren(['table'])[0].findChildren(['tr'])
		todownload = metadatarow[16].findChildren(['td'])[1].findChildren(['a'])
	except IndexError:
		return []
	return todownload

#python lensDocCloudSych; #if it runs, good to go

def getMetaData(knumber, purchaseorder, vendor,department):
	data = {}
	data['contract number'] = knumber.strip()
	data['vendor'] = vendor.strip()
	data['department'] = department.strip()
	data['purchase order'] = purchaseorder.strip()
	return data

def getDescription(soup):
	try:
		mainTable = soup.select('.table-01').pop()
		metadatarow = mainTable.findChildren(['tr'])[2].findChildren(['td'])[0].findChildren(['table'])[0].findChildren(['tr'])
		description = metadatarow[1].findChildren(['td'])[5].contents.pop().strip()
		return description
	except:
		return ""

def getTitle(vendor, description):
	title = ""
	title = vendor + " : " + description
	return title


def getVendorID(html):
    p = "(?<=ExternalVendorProfile\(')\d+"
    vendorids = re.findall(p,lines)
    if len(vendorids) == 0:
        return ""
    else:
        return vendorids.pop()

def addEmpty(purchaseordernumber):
	if not hasPurchaseOrder(purchaseordernumber):
		e = Contract(purchaseordernumber)
		response = urllib2.urlopen('http://www.purchasing.cityofno.com/bso/external/purchaseorder/poSummary.sdo?docId='+ e.purchaseordernumber + '&releaseNbr=0&parentUrl=contract')
		html = response.read()
		soup = BeautifulSoup(html)
        vendorid = getVendorID(html)
		knumber = getKnumber(soup).replace("M", "")
		department = getDepartment(soup)
		vendor = getVendor(soup)
		addVendor(vendor)
		addDepartment(department)
		description = getDescription(soup)
		attachmentQueue = getAttachmentQueue(soup)
		counter = 1
		for a in attachmentQueue:
			if counter > 1:
				e.purchaseordernumber = e.purchaseordernumber + "_" + str(counter)
			title = getTitle(vendor, description)
			counter += 1 
			bidno = re.findall("[0-9]+", a.attrs['href']).pop()
			downloadFile(bidno)
			data = getMetaData(knumber, e.purchaseordernumber, vendor,department)
            doc_cloud_id = uploadContract(bidno, data, description, title)
			e.doc_cloud_id = doc_cloud_id
			os.rename(bidno, str(e.doc_cloud_id) + ".pdf")
			e.vendorid = getVendorID(vendor)
			e.departmentid = getDepartmentID(department)
			e.title = title
			e.description = description
			e.contractnumber = knumber
			e.dateadded = datetime.datetime.now()
			session.commit()

def uploadMetadata(metadata):
    data = dict()
    data['contract number'] = metadata['contract number']
    data['vendor'] = metadata['vendor'].strip()
    data['department'] = metadata['department'].strip()
    data['purchase order'] = metadata['purchaseOrder'].strip()
    searchterm = '\'contract number\':' + "'" + data['contract number'] + "'"
    doc = documentCloudClient.documents.search(searchterm).pop()
    doc.data=data
    doc.put()

def hasContract(metadata):
    searchterm = '\'contract number\':' + "'" + metadata.get("contract number") + "'"
    if len(documentCloudClient.documents.search(searchterm))<1:
        return False; #it is a new contract
    return True; #it is an existing contract. We know the k-number

def hasPurchaseOrder(purchaseOrder):
    searchterm = '\'purchase order\':' + "'" + purchaseOrder + "'"
    if len(documentCloudClient.documents.search(searchterm))<1:
        return False; #it is a new purchase order
    return True; #it is an existing purchase order.

def getContract(purchaseOrder):
    searchterm = '\'purchase order\':' + "'" + purchaseOrder + "'"
    return documentCloudClient.documents.search(searchterm).pop()

def uploadMetadata(metadata):
    searchterm = '\'contract number\':' + "'" + str(metadata['contract number']) + "'"
    document = documentCloudClient.documents.search(searchterm).pop()
    data = dict()
    data['vendor'] = metadata['vendor']
    data['department'] = metadata['department']
    data['purchase order'] = metadata['purchaseOrder']
    data['contract number'] = str(metadata['contract number'])
    document.data = data
    document.put()

def getMissingPurchaseOrders(purchaseOrders):
    output = []
    for purchaseOrder in purchaseOrders:
        searchterm = '\'purchase order\':' + purchaseOrder
        if len(documentCloudClient.documents.search(searchterm))<1:
            output.append(purchaseOrder)
    return output

if __name__ == "__main__":
	for line in sys.stdin:
		purchaseorder = line.replace("\n", "").split("=")[1].replace("&","")
		if session.query(Contract).filter(Contract.purchaseordernumber==purchaseorder).count()==0:
			#print "need to add {}".format(purchaseorder)
			addEmpty(purchaseorder)