import os
import re
import urllib2
import datetime
import ConfigParser
import logging
import sys

from documentcloud import DocumentCloud
from contracts.settings import Settings
from bs4 import BeautifulSoup
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Date, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine


Base = declarative_base()

settings = Settings()

LEVELS = { 'debug':logging.DEBUG,
            'info':logging.INFO,
            'warning':logging.WARNING,
            'error':logging.ERROR,
            'critical':logging.CRITICAL
            }

if len(sys.argv) > 1:
    level_name = sys.argv[1]
    level = LEVELS.get(level_name, logging.NOTSET)
    logging.basicConfig(level=level, filename=settings.log)
else:
    logging.basicConfig(level=logging.DEBUG, filename=settings.log)


logging.warning('This message should go to the log file')


class PurchaseOrder(object):


    def __init__(self, html):
        self.html = html
        self.soup = BeautifulSoup(html)
        self.vendor_id_city = self.get_vendor_id(html)
        self.description = self.get_description(self.soup)
        self.vendor_name = self.get_vendor_name(self.soup)
        self.department = self.get_department(self.soup)
        self.k_number = self.getKnumber(self.soup)
        self.purchaseorder = self.get_purchase_order(self.soup)
        self.attachments = self.get_attachments(self.soup)


    def get_attachments(self, soup):
        try:
            mainTable = soup.select('.table-01').pop()
            metadatarow = mainTable.findChildren(['tr'])[2].findChildren(['td'])[0].findChildren(['table'])[0].findChildren(['tr'])
            todownload = metadatarow[16].findChildren(['td'])[1].findChildren(['a'])
        except IndexError:
            return []      
        return todownload


    def get_vendor_id(self, html):
        p = "(?<=ExternalVendorProfile\(')\d+"
        vendorids = re.findall(p,html)
        if len(vendorids) == 0:
            return ""
        else:
            return vendorids.pop()


    def get_description(self, soup):
     try:
        mainTable = soup.select('.table-01').pop()
        metadatarow = mainTable.findChildren(['tr'])[2].findChildren(['td'])[0].findChildren(['table'])[0].findChildren(['tr'])
        description = metadatarow[1].findChildren(['td'])[5].contents.pop().strip()
        return description
     except:
        return ""


    def get_vendor_name(self, soup):
     vendorrow = soup(text=re.compile(r'Vendor:'))[0].parent.parent
     vendorlinktext = vendorrow.findChildren(['td'])[1].findChildren(['a'])[0].contents.pop().strip()
     vendor = vendorlinktext.split('-')[1].strip().replace(".", "") #no periods in vendor names
     return vendor

    
    def getKnumber(self, soup):
        mainTable = soup.select('.table-01').pop()
        metadatarow = mainTable.findChildren(['tr'])[2].findChildren(['td'])[0].findChildren(['table'])[0].findChildren(['tr'])
        try:
            knumber = metadatarow[6].findChildren(['td'])[1].contents.pop().replace('k', '').replace("m", '').strip().replace("M", "")
        except:
           knumber = "unknown"
        return knumber


    def get_purchase_order(self, soup):
        mainTable = soup.select('.table-01').pop()
        po = mainTable.findChildren(['tr'])[2].findChildren(['td'])[0].findChildren(['table'])[0].findChildren(['tr'])[1].findChildren(['td'])[1].contents.pop().strip()
        return po


    def get_department(self, soup):
        mainTable = soup.select('.table-01').pop()
        metadatarow = mainTable.findChildren(['tr'])[2].findChildren(['td'])[0].findChildren(['table'])[0].findChildren(['tr'])
        department = metadatarow[5].findChildren(['td'])[1].contents.pop().strip()
        return department


    def getMetaData(knumber, purchaseorder, vendor,department, vendorid):
        data = {}
        data['contract number'] = self.k_number
        data['vendor'] = self.vendor_name
        data['department'] = self.department
        data['purchase order'] = purchaseorder.strip()
        data['vendor_id'] = self.vendor_id_city
        return data

    def __str__(self):
        return "<PurchaseOrder {}>".format(self.vendor_id_city)


class EthicsRecord(Base):
    __tablename__ = 'ethics_records'

    id = Column(Integer, primary_key=True)
    last = Column(String)
    first = Column(String)
    reportno = Column(String)
    form = Column(String)
    schedule = Column(String)
    contributiontype = Column(String)
    contributorname = Column(String)
    address1 = Column(String)
    address2 = Column(String)
    city = Column(String)
    state = Column(String)
    zipcode = Column(String)
    receiptdate = Column(String)
    receiptamount = Column(String)
    description = Column(String)

    def __init__(self, name):
        self.last = last
        self.first = first
        self.reportno = reportno
        self.form = form
        self.schedule = schedule
        self.contributiontype = contributiontype
        self.contributorname = contributorname
        self.address1 = address1
        self.address2 = address2
        self.city = city
        self.state = state
        self.zipcode = zipcode
        self.receiptdate = receiptdate
        self.receiptamount = receiptamount
        self.description = description


    def __str__(self):
        return "${} to {} {} on {}".format(self.receiptamount, self.first, self.last, self.receiptdate)


    def __repr__(self):
        return "${} to {} {} on {}".format(self.receiptamount, self.first, self.last, self.receiptdate)


class LensRepository():


    def valid_po(self, purchaseorderno):
        po_re = '[A-Z]{2}\d+'
        po_regex = re.compile(po_re)
        if po_regex.match(purchaseorderno):
            return True
        else:
            return False


    def download_purchaseorder(self, purchaseorderno):
        if purchaseorderno in self.skiplist:
            raise PermissionError("Contract not posted to public website")
        if not self.valid_po(purchaseorderno):
            raise ValueError("not a valid po")
        if not self.has_pos(purchaseorderno):
            response = urllib2.urlopen('http://www.purchasing.cityofno.com/bso/external/purchaseorder/poSummary.sdo?docId=' + purchaseorderno + '&releaseNbr=0&parentUrl=contract')
            html = response.read()
            self.write_pos(html)


    def write_pos(self, html):
        file_loc = self.purchaseorders_location + purchaseorderno
        f = open(file_loc,'w')
        f.write(html) # python will convert \n to os.linesep
        f.close() # you can omit in most cases as the destructor will call if


    def sync(self, purchaseorderno):
        if not self.has_pos(purchaseorderno):
            self.download_purchaseorder(purchaseorderno)

    
    def has_pos(self, purchaseorderno):
        file_loc = self.purchaseorders_location + purchaseorderno
        if os.path.isfile(file_loc):
            return True
        else:
            return False


    def get_skip_list(self):
        skiplist_loc = Settings().root_folder + "/contracts/datamanagement/scrapers/skiplist.txt"
        skiplist = open(skiplist_loc)
        skiplist = [l.replace("\n", "") for l in skiplist]
        return skiplist


    def __init__(self):
        #do not include these aviation contracts. They are not posted on the city's public purchasing site (but are included in the city's contract logs.)
        self.skiplist = self.get_skip_list()
        self.purchaseorders_location = Settings().corpus_loc + "/purchaseorders/" 


'''
Abstracts from Lens contracts project
'''
class DocumentCloudProject():
   
 
    def __init__(self):
        settings = Settings()
        doc_cloud_user = settings.doc_cloud_user
        doc_cloud_password = settings.doc_cloud_password
        self.client = DocumentCloud(doc_cloud_user, doc_cloud_password)
        self.docs = None #sometimes won't need all the docs, so dont do the search on init


    #searchterm = '\'purchase order\':' + "'" + po + "'"
    #searchterm = '\'contract number\':' + "'" + k_no + "'"
    def get_contract(self, field, value):
        searchterm = '\'' + field + '\':' + "'" + value + "'"
        doc = self.client.documents.search(searchterm).pop()
        return doc


    def has_contract(self, field, value):
        searchterm = '\'' + field + '\':' + "'" + value + "'"
        if len(self.client.documents.search(searchterm))<1:
            return False; #it is a new contract
        return True; #it is an existing contract. We know the k-number


    def add_contract(self, ponumber):
        po_re = '[A-Z]{2}\d+'
        po_regex = re.compile(po_re)
        if not po_regex.match(ponumber):
            raise ValueError("{} doesn't look like a valid purchase order").format(ponumber)
        #TODO

    def get_all_docs(self):
        if self.docs is None:
            self.docs = self.client.documents.search('projectid: 1542-city-of-new-orleans-contracts')
        else:
            return self.docs


    def uploadContract(self, file, data, description, title):
        if len(data['contract number'])<1:
            return #do not upload. There is a problem
        newid = documentCloudClient.documents.upload(file, title.replace("/", ""), 'City of New Orleans', description, None,'http://vault.thelensnola.org/contracts', 'public', '1542-city-of-new-orleans-contracts', data, False)
        return newid


    def update_metadata(self, doc_cloud_id, meta_field, new_meta_data_value):
        contract = self.client.documents.get(doc_cloud_id)
        contract.data[meta_field] = new_meta_data_value
        contract.put()


class LensDatabase():

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
    def getVendorID_Lens(vendor):
        session.flush()
        vendors = session.query(Vendor).filter(Vendor.name==vendor).all()
        vendor = vendors.pop()


    def getDepartmentID(department):
        return session.query(Department).filter(Department.name==department).first().id


class SummaryProcessor():


    #refactor to take a type
    def process(self, purchaseorderno):
        doc_cloud_project = DocumentCloudProject()
        lens_repo = LensRepository()
        if not doc_cloud_project.has_contract("purchase order", purchaseorderno): #if Document cloud does not have this already
            lens_repo.sync(purchaseorderno)                     #add it to the repo, if needed   
        else:
            print "Document cloud aready has {}".format(purchaseorderno)


def remakeDB():
    engine = create_engine('postgresql://' + user + ':' + databasepassword + '@' + server + ':5432/' + database)
    Base.metadata.create_all(engine)


if __name__ == "__main__":
    remakeDB()