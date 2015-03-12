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