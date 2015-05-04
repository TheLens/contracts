#!/usr/bin/python
"""
These models gather and organize 
published contracts from the city
"""
import os
import re
import urllib2
import datetime
import logging
import datetime
import uuid
import subprocess

from sqlalchemy.orm import sessionmaker
from contracts.datamanagement.lib.utilities import download_attachment_file
from documentcloud import DocumentCloud
from contracts.lib.models import get_contract_index_page
from contracts.lib.models import get_po_numbers_from_index_page
from contracts.settings import Settings
from bs4 import BeautifulSoup
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from contracts.lib.models import valid_po
from sqlalchemy import create_engine
from contracts.lib.vaultclasses import Vendor, Department, Contract

Base = declarative_base()

SETTINGS = Settings()

logging.basicConfig(level=logging.DEBUG, filename=SETTINGS.log)

#this is a uuid that is unique to a given run of the program. Grep for it in the log file to see a certain run 
run_id = " " + str(uuid.uuid1())


class PurchaseOrder(object):
    """
    A purchase order has a PO number. A PO number is
    an authorization to purchase. It gets associated with
    a city contract once the authorization goes thru. 

    A PO number is used to track a contract in the city's
    purchasing system.
    """
    def __init__(self, tt, download_attachments=True):
        purchaseorderno = tt
        if not valid_po(purchaseorderno):
            logging.info('{} | {} | Skipping. Not a valid purchaseorder | {}'.format(run_id, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), purchaseorderno))
            return
        html = self.get_html(purchaseorderno)
        self.soup = BeautifulSoup(html)
        self.vendor_id_city = self.get_vendor_id(html)
        self.download_vendor_profile(self.vendor_id_city)
        self.description = self.get_description(self.soup)
        try:
            self.vendor_name = self.get_vendor_name(self.soup)
        except IOError:
            self.vendor_name = "unknown"
            logging.info('{} | Skipping. No associated vendor info | {}'.format(run_id, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), purchaseorderno, purchaseorderno))
            return
        self.department = self.get_department(self.soup)
        self.k_number = self.getKnumber(self.soup)
        self.purchaseorder = self.get_purchase_order(self.soup)
        
        self.attachments = self.get_attachments(self.soup)
        if download_attachments:
            for a in self.attachments:
                self.download_attachment(a)
        self.data = self.get_data()
        self.title = self.vendor_name + " : " + self.description


    def get_vendor_id_city(self):
        return self.vendor_id_city


    def check_invalid(self, html):
        """
        Sometimes invalid POs are posted
        """
        if "There are no vendor distributors found for this master blanket/contract" in html:
            return True
        else:
            return False


    def get_data(self):
        """
        Return metadata as a dictionary (for document cloud)
        """
        output = {}
        output['vendor_id'] = self.vendor_id_city
        output['purchase order'] = self.purchaseorder
        output['contract number'] = self.k_number
        output['department'] = self.department
        output['vendor'] = self.vendor_name
        return output


    def download_attachment(self, attachment):
        """
        Download an attachemnt associated with a purchase order
        """
        bidnumber = re.search('[0-9]+', attachment.get('href')).group()
        bidfilelocation = SETTINGS.bids_location + bidnumber + ".pdf"
        if not os.path.isfile(bidfilelocation):
            download_attachment_file(bidnumber, bidfilelocation)
            logging.info('{} | {} | Downloaded bid {} associated with purchase order {} | {}'.format(run_id, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), bidnumber, self.purchaseorder, self.purchaseorder))
        else:
            logging.info('{} | {} | Already have bid {} for purchase order {} | {}'.format(run_id, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), bidnumber, self.purchaseorder, self.purchaseorder))


    def get_html(self, purchaseorderno):
        """
        Check to see if the purchase order should be downloaded.
        Then download it
        """
        if os.path.isfile(SETTINGS.purchase_order_location + purchaseorderno):
            logging.info('{} | {} | Already have purchase order | {}'.format(run_id, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), purchaseorderno))
            return "".join([i.replace("\n", "") for i in open(SETTINGS.purchase_order_location + purchaseorderno)])
        else:
            self.download_purchaseorder(purchaseorderno)


    def download_purchaseorder(self, purchaseorderno):
        """
        Download the html associated with a purchase order
        """
        if not valid_po(purchaseorderno):
            logging.info("not a valid po {}".format(purchaseorderno))
            return
        if not os.path.exists(SETTINGS.purchase_order_location + purchaseorderno):
            logging.info('{} | {} | Attempting to download url | {}'.format(run_id, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), url))
            url = 'http://www.purchasing.cityofno.com/bso/external/purchaseorder/poSummary.sdo?docId=' + purchaseorderno + '&releaseNbr=0&parentUrl=contract'
            response = urllib2.urlopen(url)
            html = response.read()
            with open(SETTINGS.purchase_order_location + purchaseorderno, 'w') as f:
                f.write(html)
                logging.info('{} | {} | Downloaded purchase order | {}'.format(run_id, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), purchaseorderno))
   

    def download_vendor_profile(self, vendor_id_city):
        """
        Download the vendor page associated with a purchase order
        (If we don't have the vendor page already)
        """
        vendor_file_location = SETTINGS.vendors_location + vendor_id_city
        if not os.path.isfile(vendor_file_location):
            try:
                response = urllib2.urlopen('http://www.purchasing.cityofno.com/bso/external/vendor/vendorProfileOrgInfo.sdo?external=true&vendorId=' + vendor_id_city)
                html = response.read()
                with open(vendor_file_location,'w') as f:
                    f.write(html)
                logging.info('{} | {} | Downloaded vendor file | {}'.format(run_id, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), vendor_id_city))
            except urllib2.HTTPError:
                logging.info('{} | {} | Could not download vendor file | {}'.format(run_id, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), vendor_id_city))
        else:
            logging.info('{} | {} | Skipped vendor file. Already present | {}'.format(run_id, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), vendor_id_city))


    def get_attachments(self, soup):
        """
        Find the attachements to download from the html
        """
        try:
            mainTable = soup.select('.table-01').pop()
            metadatarow = mainTable.findChildren(['tr'])[2].findChildren(['td'])[0].findChildren(['table'])[0].findChildren(['tr'])
            todownload = metadatarow[16].findChildren(['td'])[1].findChildren(['a'])
        except IndexError:
            return [] # sometimes the city does not include them   
        return todownload


    def get_vendor_id(self, html):
        '''
        Find the vendor id in the HTML
        '''
        p = "(?<=ExternalVendorProfile\(')\d+"
        vendorids = re.findall(p,html)
        if len(vendorids) == 0:
            return ""
        else:
            return vendorids[0]   #you need to take the first one for this list or you'll sometimes end up w/ the vendor_id for a subcontractor, which will sometimes wash up on the vendor page
                                  #view-source:http://www.purchasing.cityofno.com/bso/external/purchaseorder/poSummary.sdo?docId=FC154683&releaseNbr=0&parentUrl=contract 

    def get_description(self, soup):
        '''
        Find the description in the html
        '''
        try:
            mainTable = soup.select('.table-01').pop()
            metadatarow = mainTable.findChildren(['tr'])[2].findChildren(['td'])[0].findChildren(['table'])[0].findChildren(['tr'])
            description = metadatarow[1].findChildren(['td'])[5].contents.pop().strip()
            return description
        except:
            return ""


    def get_vendor_name(self, soup):
        '''
        Find the vendor name in the html
        '''
        try:
            vendorrow = soup(text=re.compile(r'Vendor:'))[0].parent.parent
            vendorlinktext = vendorrow.findChildren(['td'])[1].findChildren(['a'])[0].contents.pop().strip()
            vendor = vendorlinktext.split('-')[1].strip().replace(".", "") #no periods in vendor names
            return vendor
        except IndexError:      #in cases of index error, go ahead and downlaod the vendor page
            vendor_file_location = SETTINGS.vendors_location + self.vendor_id_city
            html = "".join([l.replace("\n", "") for l in open(vendor_file_location)])
            new_soup = BeautifulSoup(html)
            header = new_soup.select(".sectionheader-01")[0]
            vendor_name = str(header).replace("Vendor Profile - ", "")
            return vendor_name

    def getKnumber(self, soup):
        '''
        Find the k number in the html
        '''
        mainTable = soup.select('.table-01').pop()
        metadatarow = mainTable.findChildren(['tr'])[2].findChildren(['td'])[0].findChildren(['table'])[0].findChildren(['tr'])
        try:
            knumber = metadatarow[6].findChildren(['td'])[1].contents.pop().replace('k', '').replace("m", '').strip().replace("M", "")
        except:
            knumber = "unknown"
        if len(knumber) == 0:
            knumber = "unknown"
        return knumber


    def get_purchase_order(self, soup):
        '''
        Find the purchase order in the html
        '''
        mainTable = soup.select('.table-01').pop()
        po = mainTable.findChildren(['tr'])[2].findChildren(['td'])[0].findChildren(['table'])[0].findChildren(['tr'])[1].findChildren(['td'])[1].contents.pop().strip()
        return po


    def get_department(self, soup):
        '''
        Find the department in the html
        '''
        mainTable = soup.select('.table-01').pop()
        metadatarow = mainTable.findChildren(['tr'])[2].findChildren(['td'])[0].findChildren(['table'])[0].findChildren(['tr'])
        department = metadatarow[5].findChildren(['td'])[1].contents.pop().strip()
        return department

    def __str__(self):
        return "<PurchaseOrder {}>".format(self.purchaseorder)


class EthicsRecord(Base):
    """
    This class simply represents a single row of 
    campaign finance contributions (from the Louisiana Ethics Board). 

    It goes in datamanagement instead of lib/models because it doesn't 
    really concern the public web app
    """
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

    def __init__(self, 
                 last, first, reportno,
                  form, schedule, contributiontype, 
                  contributorname, address1, 
                  address2, city, state, zipcode,
                  receiptdate, receiptamount, description):
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


class LensRepository(object):
    """
    A purchase order has a PO number. A PO number is
    an authorization to purchase. It gets associated with
    a city contract once the authorization goes thru. 

    A PO number is used to track a contract in the city's
    purchasing system.
    """
    def download_purchaseorder(self, purchaseorderno):
        if purchaseorderno in self.skiplist:
            logging.warning('{} | {} | Contract is in the skiplist | {}'.format(run_id, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), purchaseorderno))
            return  
        if not valid_po(purchaseorderno):
            logging.warning('{} | {} | Invalid purchase order | {}'.format(run_id, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), purchaseorderno))
            return  
        file_loc = self.purchaseorders_location + purchaseorderno
        if not os.path.isfile(file_loc):
            response = urllib2.urlopen('http://www.purchasing.cityofno.com/bso/external/purchaseorder/poSummary.sdo?docId=' + purchaseorderno + '&releaseNbr=0&parentUrl=contract')
            html = response.read()
            self.write_pos(html, file_loc)


    def write_pos(self, html, file_loc):
        with open(file_loc,'w') as f:
            logging.warning('{} | {} | Writing purchaseorderno to file | {}'.format(run_id, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), file_loc))
            f.write(html) # python will convert \n to os.linesep


    def sync(self, purchaseorderno):
        if purchaseorderno in self.skiplist:
            logging.warning('{} | {} | Contract is in the skiplist | {}'.format(run_id, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), purchaseorderno))
            return
        file_loc = self.purchaseorders_location + purchaseorderno
        if not os.path.isfile(file_loc):
            self.download_purchaseorder(purchaseorderno)
        else:
            logging.warning('{} | {} | The Lens repo already has this purchaseorderno | {}'.format(run_id, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), purchaseorderno))


    def get_skip_list(self):
        """
        Some contracts are not posted on the city's site 
        -- even though they are included in the city's
        contract inventory. We put these contracts on a
        "skip list" so they are ignored in code
        """
        #To Do: skip list should not be hard coded
        skiplist_loc = SETTINGS.root_folder + "/contracts/datamanagement/scrapers/skiplist.txt"
        skiplist = open(skiplist_loc)
        skiplist = [l.replace("\n", "") for l in skiplist]
        return skiplist


    def __init__(self):
        #do not include these aviation contracts. They are not posted on the city's public purchasing site (but are included in the city's contract logs.)
        self.skiplist = self.get_skip_list()
        self.purchaseorders_location = SETTINGS.corpus_loc + "/purchaseorders/" 


class DocumentCloudProject(object):
    '''
    Represents the collection of contracts on DC
    '''
    def __init__(self):
        doc_cloud_user = SETTINGS.doc_cloud_user
        doc_cloud_password = SETTINGS.doc_cloud_password
        self.client = DocumentCloud(doc_cloud_user, doc_cloud_password)
        self.docs = None #sometimes won't need all the docs, so dont do the search on init
        self.skiplist = self.get_skip_list()


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
        logging.info('{} | {} | Attempting to add {} to DocumentCloud | {}'.format(run_id, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), ponumber, ponumber))
        if not po_regex.match(ponumber):
            logging.info("{} doesn't look like a valid purchase order. Skipping for now".format(ponumber))
            return
        if ponumber in self.skiplist:
            logging.info('{} | {} | Not adding {} to DocumentCloud. In the skiplist | {}'.format(run_id, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), ponumber, ponumber))
            return
        if not self.has_contract("purchase order", ponumber):
            try:
                po = PurchaseOrder(ponumber)
            except IndexError:
                logging.info('{} | {} | Something looks wrong with the format on this one. Skipping for now | {}'.format(run_id, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), ponumber, ponumber))
                return
            logging.info('{} | {} | Adding {} to DocumentCloud | {}'.format(run_id, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), ponumber, ponumber))
            if len(po.attachments) > 0:
                counter = 1
                for a in po.attachments:
                    bidnumber = re.search('[0-9]+', a.get('href')).group()
                    bidfilelocation = SETTINGS.bids_location + bidnumber + ".pdf"
                    extra_string = ""
                    if counter > 1:
                        extra_string = str(counter) + " of " + str(len(po.attachments))
                    self.upload_contract(bidfilelocation, po.data, po.description + extra_string, po.title + extra_string)
                    counter += 1             
        else:
            logging.info('{} | {} | Not adding {} to DocumentCloud. Already up there | {}'.format(run_id, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), ponumber, ponumber))


    def get_all_docs(self):
        if self.docs is None:
            self.docs = self.client.documents.search('projectid: 1542-city-of-new-orleans-contracts')
        else:
            return self.docs


    def upload_contract(self, file, data, description, title):
        if len(data['contract number'])<1:
            logging.info('{} | {} | Not adding {} to DocumentCloud. Contract number {} is null | {}'.format(run_id, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), data['purchase order'], data['contract number'], data['purchase order']))
            return #do not upload. There is a problem
        newcontract = self.client.documents.upload(file, title.replace("/", ""), 'City of New Orleans', description, None,'http://vault.thelensnola.org/contracts', 'public', '1542-city-of-new-orleans-contracts', data, False)
        logging.info('{} | {} | {} has doc_cloud_id {} | {}'.format(run_id, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), data['purchase order'], newcontract.id, data['purchase order']))
        c = Contract()
        c.doc_cloud_id = newcontract.id
        with LensDatabase() as db:
            db.add_contract(c)


    def update_metadata(self, doc_cloud_id, meta_field, new_meta_data_value):
        logging.info('{} | {} | updating {} on DocumentCloud. Changing {} to {}'.format(run_id, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), doc_cloud_id, meta_field, new_meta_data_value))
        contract = self.client.documents.get(doc_cloud_id)
        contract.data[meta_field] = new_meta_data_value
        contract.put()


    def get_skip_list(self):
        skiplist_loc = SETTINGS.root_folder + "/contracts/datamanagement/scrapers/skiplist.txt"
        skiplist = open(skiplist_loc)
        skiplist = [l.replace("\n", "") for l in skiplist]
        return skiplist


class LensDatabase(object):
    '''
    Represents the Lens database that tracks contracts
    '''
    def __init__(self):
        engine = create_engine(SETTINGS.connection_string)
        Session = sessionmaker(bind=engine)
        self.session = Session()


    def __enter__(self):
        '''
        This gets called when you do with LensDatabase() as db:"
        '''
        return self


    #refactor to take a type
    def get_officers(self):
        """
        Returns a list of all company officers in the database
        """
        pass
        # to do Tom Thoren

    #refactor to take a type
    def add_vendor(self, vendor):
        """
        Add vendor to the Lens db
        """
        indb = self.session.query(Vendor).filter(Vendor.name==vendor).count()
        if indb==0:
            vendor = Vendor(vendor)
            self.session.add(vendor)
            self.session.commit()


    def add_department(self, department):
        """
        Add department to the Lens db
        """
        indb = self.session.query(Department).filter(Department.name==department).count()
        if indb==0:
            department = Department(department)
            self.session.add(department)
            self.session.commit()
        

    def add_contract(self, contract):
        """
        Add a contract to the Lens db
        """
        if contract.doc_cloud_id is None:
            indb = 0
        else:
            indb = self.session.query(Contract).filter(Contract.doc_cloud_id==contract.doc_cloud_id).count()
        if indb == 0:
            self.session.add(contract)
            self.session.flush()
            self.session.commit()


    def has_contract(self, purchaseorderno):
        """
        Add department to the Lens db
        """
        indb = self.session.query(Contract).filter(Contract.purchaseordernumber==purchaseorderno).count()
        if indb==1:
            return True
        else:
            return False


    def get_contract(self, purchaseorderno):
        """
        Get a contract from the db
        """
        return self.session.query(Contract).\
                filter(Contract.purchaseordernumber==purchaseorderno).\
                first()


    def get_lens_vendor_id(self, vendor):
        """
        Get a vendor in the db. To do: refactor 
        """
        self.session.flush()
        vendors = self.session.query(Vendor).filter(Vendor.name==vendor).all()
        vendor = vendors.pop()


    def get_department_id(self, department):
        """
        Get a department in the db. To do: refactor 
        """
        return self.session.query(Department).filter(Department.name==department).first().id


    def __exit__(self, type, value, traceback):
        """
        Called when the database is closed
        """
        self.session.close()


class SummaryProcessor(object):


    def process(self, purchaseorderno):
        logging.warning('{} | {} | Processing | {}'.format(run_id, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), purchaseorderno))
        doc_cloud_project = DocumentCloudProject()
        lens_repo = LensRepository()
        try:
            lens_repo.sync(purchaseorderno)                     #add it to the repo, if needed   
            logging.info('{} | {} | Synched | {}'.format(run_id, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), purchaseorderno))
        except urllib2.HTTPError:
            logging.warning('{} | {} | Contract not posted publically | {}'.format(run_id, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), purchaseorderno))


class DailyScraper(object):
    '''
    Daily job that gets new contracts from the purchasing portal
    '''
    def run(self, page_no):
        logging.info('{} | {} | Daily scraper run '.format(run_id, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        doc_cloud_project = DocumentCloudProject()
        lens_repo = LensRepository()
        html = get_contract_index_page(page_no)
        output = get_po_numbers_from_index_page(html)
        for purchaseorderno in output:
            logging.info('{} | {} | Daily scraper found po {}'.format(run_id, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), purchaseorderno))
            try:
                lens_repo.sync(purchaseorderno)
                doc_cloud_project.add_contract(purchaseorderno)
            except urllib2.HTTPError:
                logging.warning('{} | {} | Contract not posted publically | {}'.format(run_id, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), purchaseorderno))