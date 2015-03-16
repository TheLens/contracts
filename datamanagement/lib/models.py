import os
import re
import datetime
import ConfigParser

from documentcloud import DocumentCloud

from bs4 import BeautifulSoup
<<<<<<< HEAD

=======
>>>>>>> cc7f20ee5d9e379d12a74b642e15acc92b853855
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Date, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine


Base = declarative_base()

from ... settings import Settings


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


'''
Abstracts from Lens contracts project
'''
class DocumentCloudProject():
   
 
    def __init__(self):
<<<<<<< HEAD
        settings = Settings()
        doc_cloud_user = settings.doc_cloud_user
        doc_cloud_password = settings.doc_cloud_password
=======
        s = Settings()
        doc_cloud_user = s.doc_cloud_user
        doc_cloud_password = s.doc_cloud_password
>>>>>>> cc7f20ee5d9e379d12a74b642e15acc92b853855
        self.client = DocumentCloud(doc_cloud_user, doc_cloud_password)
        self.docs = None #sometimes won't need all the docs, so dont do the search on init


    def get_contract(self, field, value):
        searchterm = '\'' + field + '\':' + "'" + value + "'"
        doc = self.client.documents.search(searchterm).pop()
        return doc


    def has_contract_with_purchase_order(self = None, po = None):
        searchterm = '\'purchase order\':' + "'" + po + "'"
        docs = self.client.documents.search(searchterm)
        if len(docs) > 0:
            return True
        else:
            return False


    def get_all_docs(self):
        if self.docs is None:
            self.docs = self.client.documents.search('projectid: 1542-city-of-new-orleans-contracts')
        else:
            return self.docs


    def has_contract_with_k_no(k_no):
        searchterm = '\'contract number\':' + "'" + k_no + "'"
        if len(documentCloudClient.documents.search(searchterm))<1:
            return False; #it is a new contract
        return True; #it is an existing contract. We know the k-number


    def uploadContract(file, data, description, title):
        if len(data['contract number'])<1:
            return #do not upload. There is a problem
        newid = documentCloudClient.documents.upload(file, title.replace("/", ""), 'City of New Orleans', description, None,'http://vault.thelensnola.org/contracts', 'public', '1542-city-of-new-orleans-contracts', data, False)
        return newid


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

def remakeDB():
    engine = create_engine('postgresql://' + user + ':' + databasepassword + '@' + server + ':5432/' + database)
    Base.metadata.create_all(engine)


if __name__ == "__main__":
    remakeDB()