import os
import re
from bs4 import BeautifulSoup
from utilities import get_from_config

class PurchaseOrder(object):


    def __init__(self, html):
        self.html = html
        self.soup = BeautifulSoup(html)
        self.vendor_id_city = self.get_vendor_id(html)
        self.description = self.get_description(self.soup)
        self.vendor_name = self.get_vendor_name(self.soup)
        self.department = self.get_department(self.soup)


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
     vendorlinktext = vendorrow.findChildren(['td'])[1].findChildren(['a'
             ])[0].contents.pop().strip()
     vendor = vendorlinktext.split('-')[1].strip().replace(".", "") #no periods in vendor names
     return vendor

    
    def get_department(self, soup):
        mainTable = soup.select('.table-01').pop()
        metadatarow = mainTable.findChildren(['tr'])[2].findChildren(['td'])[0].findChildren(['table'])[0].findChildren(['tr'])
        department = metadatarow[5].findChildren(['td'])[1].contents.pop().strip()
        return department


    def __str__(self):
        return "<PurchaseOrder {}>".format(self.vendor_id_city)


class DocumentCloud(object):


    def __init__(self):
        self.user = get_from_config("doc_cloud_user")
        self.password = get_from_config("doc_cloud_password")


import datetime
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Date, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
import ConfigParser

Base = declarative_base()

CONFIG_LOCATION = '/apps/contracts/app.cfg'

def get_from_config(field):
    config = ConfigParser.RawConfigParser()
    config.read(CONFIG_LOCATION)
    return config.get('Section1', field)

server = get_from_config('server')
databasepassword = get_from_config('databasepassword')
user = get_from_config('user')


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

def remakeDB():
    engine = create_engine('postgresql://' + user + ':' + databasepassword + '@' + server + ':5432/thevault')
    Base.metadata.create_all(engine)

if __name__ == "__main__":
    remakeDB()