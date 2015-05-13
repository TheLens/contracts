#!/usr/bin/python

"""
These models gather and organize published contracts from the city.
"""

import os
import re
import urllib2
import datetime
import uuid
import dateutil

from sqlalchemy import desc
from sqlalchemy.orm import sessionmaker
from contracts.datamanagement.lib.utilities import download_attachment_file
from pythondocumentcloud import DocumentCloud
from contracts.lib.models import get_contract_index_page
from contracts.lib.models import get_po_numbers_from_index_page
from bs4 import BeautifulSoup
from sqlalchemy.ext.declarative import declarative_base
from contracts.lib.models import valid_po
from sqlalchemy import create_engine
from contracts.lib.vaultclasses import (
    Vendor,
    Contract,
    Person,
    Department,
    VendorOfficer,
    EthicsRecord
)
from contracts import (
    log,
    VENDORS_LOCATION,
    CORPUS_LOC,
    ROOT_FOLDER,
    DOC_CLOUD_USERNAME,
    DOC_CLOUD_PASSWORD,
    PURCHASE_ORDER_LOCATION,
    CONNECTION_STRING,
    BIDS_LOCATION
)

Base = declarative_base()

# this is a uuid that is unique to a given run of the program.
# Grep for it in the log file to see a certain run
run_id = " " + str(uuid.uuid1())


def get_timestamp():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class PurchaseOrder(object):
    """
    A purchase order has a PO number. A PO number is an authorization to
    purchase. It gets associated with a city contract once the authorization
    goes through.

    A PO number is used to track a contract in the city's purchasing system.
    """

    def __init__(self, tt, download_attachments=True):
        '''
        A purchase order number
        '''
        purchaseorderno = tt
        if not valid_po(purchaseorderno):
            log.info(
                '{} | {} | Skipping. Not a valid purchaseorder | {}'.format(
                    run_id, get_timestamp(), purchaseorderno))
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
            log.info(
                '{} | Skipping. No associated vendor info | {}'.format(
                    run_id, get_timestamp(), purchaseorderno, purchaseorderno))
            return
        self.department = self.get_department(self.soup)
        self.k_number = self.get_knumber(self.soup)
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
        Sometimes invalid POs are posted.
        """

        no_vendor_string = "There are no vendor distributors found " + \
            "for this master blanket/contract"

        if no_vendor_string in html:
            return True
        else:
            return False

    def get_data(self):
        """
        Return metadata as a dictionary (for DocumentCloud).
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
        Download an attachemnt associated with a purchase order.
        """

        bidnumber = re.search('[0-9]+', attachment.get('href')).group()
        bidfilelocation = BIDS_LOCATION + bidnumber + ".pdf"
        if not os.path.isfile(bidfilelocation):
            download_attachment_file(bidnumber, bidfilelocation)
            log.info(
                '{} | {} | Downloaded bid {} associated with purchase ' +
                'order {} | {}'.format(
                    run_id, get_timestamp(), bidnumber,
                    self.purchaseorder, self.purchaseorder))
        else:
            log.info(
                '{} | {} | Already have bid {} for purchase ' +
                'order {} | {}'.format(
                    run_id, get_timestamp(), bidnumber,
                    self.purchaseorder, self.purchaseorder))

    def get_html(self, purchaseorderno):
        """
        Check to see if the purchase order should be downloaded; download it.
        """

        if os.path.isfile(PURCHASE_ORDER_LOCATION + purchaseorderno):
            log.info(
                '{} | {} | Already have purchase order | {}'.format(
                    run_id, get_timestamp(), purchaseorderno))
            return "".join([i.replace("\n", "") for i in open(
                PURCHASE_ORDER_LOCATION + purchaseorderno)])
        else:
            self.download_purchaseorder(purchaseorderno)

    def download_purchaseorder(self, purchaseorderno):
        """
        Download the HTML associated with a purchase order.
        """

        if not valid_po(purchaseorderno):
            log.info("not a valid po {}".format(purchaseorderno))
            return
        if not os.path.exists(
            PURCHASE_ORDER_LOCATION + purchaseorderno
        ):
            url = (
                'http://www.purchasing.cityofno.com/bso/external/' +
                'purchaseorder/poSummary.sdo?docId=' + purchaseorderno +
                '&releaseNbr=0&parentUrl=contract')
            log.info(
                '{} | {} | Attempting to download url | {}'.format(
                    run_id, get_timestamp(), url
                )
            )
            response = urllib2.urlopen(url)
            html = response.read()
            with open(
                PURCHASE_ORDER_LOCATION + purchaseorderno, 'w'
            ) as f:
                f.write(html)
                log.info(
                    '{} | {} | Downloaded purchase order | {}'.format(
                        run_id, get_timestamp(), purchaseorderno))

    def download_vendor_profile(self, vendor_id_city):
        """
        Download the vendor page associated with a purchase order, if we don't
        have the vendor page already.
        """

        vendor_file_location = VENDORS_LOCATION + vendor_id_city
        if not os.path.isfile(vendor_file_location):
            try:
                response = urllib2.urlopen(
                    'http://www.purchasing.cityofno.com/bso/external/vendor/' +
                    'vendorProfileOrgInfo.sdo?external=true&vendorId=' +
                    'vendor_id_city')
                html = response.read()
                with open(vendor_file_location, 'w') as f:
                    f.write(html)
                log.info(
                    '{} | {} | Downloaded vendor file | {}'.format(
                        run_id, get_timestamp(), vendor_id_city))
            except urllib2.HTTPError:
                log.info(
                    '{} | {} | Could not download vendor file | {}'.format(
                        run_id, get_timestamp(), vendor_id_city))
        else:
            log.info(
                '{} | {} | Skipped vendor file. Already present | {}'.format(
                    run_id, get_timestamp(), vendor_id_city))

    def get_attachments(self, soup):
        """
        Find the attachments to download from the HTML.
        """

        try:
            main_table = soup.select('.table-01').pop()
            metadatarow = main_table.findChildren(
                ['tr'])[2].findChildren(['td'])[0].findChildren(
                ['table'])[0].findChildren(['tr'])
            todownload = metadatarow[16].findChildren(
                ['td'])[1].findChildren(['a'])
        except IndexError:
            return []  # sometimes the city does not include them
        return todownload

    def get_vendor_id(self, html):
        '''
        Find the vendor id in the HTML.
        '''

        pattern = "(?<=ExternalVendorProfile\(')\d+"
        vendorids = re.findall(pattern, html)
        if len(vendorids) == 0:
            return ""
        else:
            # you need to take the first one for this list or you'll sometimes
            # end up w/ the vendor_id for a subcontractor, which will sometimes
            # wash up on the vendor page
            # view-source:http://www.purchasing.cityofno.
            # com/bso/external/purchaseorder/poSummary.
            # sdo?docId=FC154683&releaseNbr=0&parentUrl=contract
            return vendorids[0]

    def get_description(self, soup):
        '''
        Find the description in the HTML.
        '''

        try:
            main_table = soup.select('.table-01').pop()
            metadatarow = main_table.findChildren(['tr'])[2].findChildren(
                ['td'])[0].findChildren(['table'])[0].findChildren(['tr'])
            description = metadatarow[1].findChildren(
                ['td'])[5].contents.pop().strip()
            return description
        except:
            return ""

    def get_vendor_name(self, soup):
        '''
        Find the vendor name in the HTML.
        '''

        try:
            vendorrow = soup(text=re.compile(r'Vendor:'))[0].parent.parent
            vendorlinktext = vendorrow.findChildren(['td'])[1].findChildren(
                ['a'])[0].contents.pop().strip()
            # Vno periods in vendor names:
            vendor = vendorlinktext.split('-')[1].strip().replace(".", "")
            return vendor
        except IndexError:
            # in cases of index error, go ahead and downlaod the vendor page
            vendor_file_location = (
                VENDORS_LOCATION + self.vendor_id_city)
            html = "".join([l.replace("\n", "") for l in open(
                vendor_file_location)])
            new_soup = BeautifulSoup(html)
            header = new_soup.select(".sectionheader-01")[0]
            vendor_name = str(header).replace("Vendor Profile - ", "")
            return vendor_name

    def get_knumber(self, soup):
        '''
        Find the k number in the HTML.
        '''

        main_table = soup.select('.table-01').pop()
        metadatarow = main_table.findChildren(['tr'])[2].findChildren(
            ['td'])[0].findChildren(['table'])[0].findChildren(['tr'])
        try:
            knumber = metadatarow[6].findChildren(
                ['td'])[1].contents.pop().replace(
                'k', '').replace("m", '').strip().replace("M", "")
        except:
            knumber = "unknown"
        if len(knumber) == 0:
            knumber = "unknown"
        return knumber

    def get_purchase_order(self, soup):
        '''
        Find the purchase order in the HTML.
        '''

        main_table = soup.select('.table-01').pop()
        po = main_table.findChildren(['tr'])[2].findChildren(
            ['td'])[0].findChildren(['table'])[0].findChildren(
            ['tr'])[1].findChildren(['td'])[1].contents.pop().strip()
        return po

    def get_department(self, soup):
        '''
        Find the department in the HTML.
        '''

        main_table = soup.select('.table-01').pop()
        metadatarow = main_table.findChildren(['tr'])[2].findChildren(
            ['td'])[0].findChildren(['table'])[0].findChildren(['tr'])
        department = metadatarow[5].findChildren(
            ['td'])[1].contents.pop().strip()
        return department

    def __str__(self):
        return "<PurchaseOrder {}>".format(self.purchaseorder)


class LensRepository(object):
    """
    A purchase order has a PO number. A PO number is an authorization to
    purchase. It gets associated with a city contract once the authorization
    goes through.

    A PO number is used to track a contract in the city's purchasing system.
    """

    def download_purchaseorder(self, purchaseorderno):
        if purchaseorderno in self.skiplist:
            # log.warning(
            #     '{} | {} | Contract is in the skiplist | {}'.format(
            #         run_id, get_timestamp(), purchaseorderno)
            # )
            return
        if not valid_po(purchaseorderno):
            # log.warning(
            #     '{} | {} | Invalid purchase order | {}'.format(
            #         run_id, get_timestamp(), purchaseorderno)
            # )
            return
        file_loc = self.purchaseorders_location + purchaseorderno
        if not os.path.isfile(file_loc):
            response = urllib2.urlopen(
                'http://www.purchasing.cityofno.com/bso/external/' +
                'purchaseorder/poSummary.sdo?docId=' + purchaseorderno +
                '&releaseNbr=0&parentUrl=contract')
            html = response.read()
            self.write_pos(html, file_loc)

    def write_pos(self, html, file_loc):
        with open(file_loc, 'w') as f:
            # log.warning(
            #     '{} | {} | Writing purchaseorderno to file | {}'.format(
            #         run_id, get_timestamp(), file_loc)
            # )
            f.write(html)  # python will convert \n to os.linesep

    def sync(self, purchaseorderno):
        if purchaseorderno in self.skiplist:
            # log.warning(
            #     '{} | {} | Contract is in the skiplist | {}'.format(
            #         run_id, get_timestamp(), purchaseorderno
            #     )
            # )
            return
        file_loc = self.purchaseorders_location + purchaseorderno
        if not os.path.isfile(file_loc):
            self.download_purchaseorder(purchaseorderno)
        else:
            pass
            # log.warning(
            #     '{} | {} | The Lens repo already has this ' +
            #     'purchaseorderno | {}'.format(
            #         run_id, get_timestamp(), purchaseorderno)
            # )

    def get_skip_list(self):
        """
        Some contracts are not posted on the city's site even though they are
        included in the city's contract inventory. We put these contracts on a
        skip list so they are ignored in code.
        """

        # TODO: skip list should not be hard coded
        skiplist_loc = (
            ROOT_FOLDER +
            "/contracts/datamanagement/scrapers/skiplist.txt")
        skiplist = open(skiplist_loc)
        skiplist = [l.replace("\n", "") for l in skiplist]
        return skiplist

    def __init__(self):
        # do not include these aviation contracts. They are not posted on the
        # city's public purchasing site (but are included in the city's
        # contract logs.)
        self.skiplist = self.get_skip_list()
        self.purchaseorders_location = CORPUS_LOC + "/purchaseorders/"


class DocumentCloudProject(object):
    '''
    Represents the collection of contracts on DocumentCloud.
    '''

    def __init__(self):
        doc_cloud_user = DOC_CLOUD_USERNAME
        doc_cloud_password = DOC_CLOUD_PASSWORD
        self.client = DocumentCloud(doc_cloud_user, doc_cloud_password)
        # sometimes won't need all the docs, so dont do the search on init
        self.docs = None
        self.skiplist = self.get_skip_list()

    # searchterm = '\'purchase order\':' + "'" + po + "'"
    # searchterm = '\'contract number\':' + "'" + k_no + "'"
    def get_contract(self, field, value):
        searchterm = '\'' + field + '\':' + "'" + value + "'"
        doc = self.client.documents.search(searchterm).pop()
        return doc

    def has_contract(self, field, value):
        searchterm = '\'' + field + '\':' + "'" + value + "'"
        if len(self.client.documents.search(searchterm)) < 1:
            return False  # it is a new contract
        return True  # it is an existing contract. We know the k-number

    def add_contract(self, ponumber):
        po_re = '[A-Z]{2}\d+'
        po_regex = re.compile(po_re)
        # log.info(
        #     '{} | {} | Attempting to add {} to DocumentCloud | {}'.format(
        #         run_id, get_timestamp(), ponumber, ponumber
        #     )
        # )
        if not po_regex.match(ponumber):
            # log.info(
            #     "{} doesn't look like a valid purchase order. " +
            #     "Skipping for now".format(ponumber)
            # )
            return
        if ponumber in self.skiplist:
            # log.info(
            #     '{} | {} | Not adding {} to DocumentCloud. In skiplist ' +
            #     '| {}'.format(
            #         run_id, get_timestamp(), ponumber, ponumber
            #     )
            # )
            return
        if not self.has_contract("purchase order", ponumber):
            try:
                po = PurchaseOrder(ponumber)
            except IndexError:
                # log.info(
                #     '{} | {} | Something looks wrong with the format on ' +
                #     'this one. Skipping for now | {}'.format(
                #         run_id, get_timestamp(), ponumber, ponumber
                #     )
                # )
                return
            # log.info(
            #     '{} | {} | Adding {} to DocumentCloud | {}'.format(
            #         run_id, get_timestamp(), ponumber, ponumber
            #     )
            # )
            if len(po.attachments) > 0:
                counter = 1
                for a in po.attachments:
                    bidnumber = re.search('[0-9]+', a.get('href')).group()
                    bidfilelocation = BIDS_LOCATION + \
                        bidnumber + ".pdf"
                    extra_string = ""
                    if counter > 1:
                        extra_string = str(counter) + " of " + \
                            str(len(po.attachments))
                    self.upload_contract(
                        bidfilelocation,
                        po.data,
                        po.description + extra_string,
                        po.title + extra_string
                    )
                    counter += 1
        else:
            pass
            # log.info(
            #     '{} | {} | Not adding {} to DocumentCloud. Already up ' +
            #     'there | {}'.format(
            #         run_id, get_timestamp(), ponumber, ponumber
            #     )
            # )

    def get_all_docs(self):
        if self.docs is None:
            self.docs = self.client.documents.search(
                'projectid: 1542-city-of-new-orleans-contracts')
            return self.docs
        else:
            return self.docs

    def upload_contract(self, file, data, description, title):
        '''
        This uploads a contract onto DcoumentCloud.
        '''

        if len(data['contract number']) < 1:
            log.info(
                '{} | {} | Not adding {} to DocumentCloud. '
                'Contract number {} is null | {}'.format(
                    run_id, get_timestamp(),
                    data['purchase order'],
                    data['contract number'],
                    data['purchase order']
                )
            )
            return  # do not upload. There is a problem
        newcontract = self.client.documents.upload(
            file,
            title.replace("/", ""),
            'City of New Orleans',
            description,
            None,
            'http://vault.thelensnola.org/contracts',
            'public',
            '1542-city-of-new-orleans-contracts',
            data,
            False
        )
        # log.info('{} | {} | {} has doc_cloud_id {} | {}'.format(
        #     run_id, get_timestamp(),
        #     data['purchase order'],
        #     newcontract.id,
        #     data['purchase order']
        # ))
        c = Contract()
        c.doc_cloud_id = newcontract.id
        with LensDatabase() as db:
            db.add_contract(c)

    def update_metadata(self, doc_cloud_id, meta_field, new_meta_data_value):
        # log.info(
        #     '{} | {} | updating {} on DocumentCloud. ' +
        #     'Changing {} to {}'.format(
        #         run_id,
        #         get_timestamp(),
        #         doc_cloud_id,
        #         meta_field,
        #         new_meta_data_value
        #     )
        # )
        contract = self.client.documents.get(doc_cloud_id)
        contract.data[meta_field] = new_meta_data_value
        contract.put()

    def get_skip_list(self):
        skiplist_loc = ROOT_FOLDER + \
            "/contracts/datamanagement/scrapers/skiplist.txt"
        skiplist = open(skiplist_loc)
        skiplist = [l.replace("\n", "") for l in skiplist]
        return skiplist


class LensDatabase(object):
    '''
    Represents the Lens database that tracks contracts.
    '''

    def __init__(self):
        engine = create_engine(CONNECTION_STRING)
        sn = sessionmaker(bind=engine)
        self.session = sn()

    def __enter__(self):
        '''
        This gets called when you do with LensDatabase() as db:"
        '''
        return self

    # refactor to take a type
    def get_officers(self):
        """
        Returns a list of all company officers in the database
        """
        pass
        # to do Tom Thoren

    # refactor to take a type
    def add_vendor(self, vendor):
        """
        Add vendor to the Lens db
        """
        indb = self.session.query(
            Vendor
        ).filter(
            Vendor.name == vendor
        ).count()
        if indb == 0:
            vendor = Vendor(vendor)
            self.session.add(vendor)
            self.session.commit()

    def add_department(self, department):
        """
        Add department to the Lens db
        """
        indb = self.session.query(
            Department
        ).filter(
            Department.name == department
        ).count()
        if indb == 0:
            department = Department(department)
            self.session.add(department)
            self.session.commit()

    def add_contract(self, contract):
        """
        Add a contract to the Lens db
        """
        indb = self.session.query(
            Contract
        ).filter(
            Contract.doc_cloud_id == contract.doc_cloud_id
        ).count()
        if indb == 0:
            self.session.add(contract)
            self.session.flush()
            self.session.commit()

    def get_all_contract_ids(self):
        dcids = [i[0] for i in self.session.query(
            Contract.doc_cloud_id
        ).order_by(
            desc(Contract.dateadded)
        ).all()]
        return dcids

    def update_contract_from_doc_cloud_doc(self, doc_cloud_id, fields):
        """
        Add a contract to the Lens db
        """
        contract = self.session.query(
            Contract
        ).filter(
            Contract.doc_cloud_id == doc_cloud_id
        ).first()

        contract.contractnumber = fields['contractno']
        contract.vendorid = fields['vendor']
        contract.departmentid = fields['department']
        contract.dateadded = fields['dateadded']
        contract.title = fields['title']
        contract.purchaseordernumber = fields['purchaseno']
        contract.description = fields['description']
        self.session.add(contract)
        self.session.flush()
        self.session.commit()

    def has_contract(self, purchaseorderno):
        """
        Add department to the Lens database.
        """

        indb = self.session.query(
            Contract
        ).filter(
            Contract.purchaseordernumber == purchaseorderno
        ).count()
        if indb == 1:
            return True
        else:
            return False

    def get_contract(self, purchaseorderno):
        """
        Get a contract from the database.
        """

        return self.session.query(
            Contract
        ).filter(
            Contract.purchaseordernumber == purchaseorderno
        ).first()

    def get_contract_doc_cloud_id(self, doc_cloud_id):
        """
        Get a contract from the database.
        """

        return self.session.query(
            Contract
        ).filter(
            Contract.doc_cloud_id == doc_cloud_id
        ).first()

    def get_lens_vendor_id(self, vendor):
        """
        Get a vendor in the database. TODO: refactor
        """

        self.session.flush()
        vendor = self.session.query(
            Vendor
        ).filter(
            Vendor.name == vendor
        ).first()
        return vendor.id

    def get_department_id(self, department):
        """
        Get a department in the database. TODO: refactor
        """

        return self.session.query(
            Department
        ).filter(
            Department.name == department
        ).first().id

    def get_half_filled_contracts(self):
        """
        DocCloud doesn't give immediate access to all document properties.
        This pulls out the contracts in the database added during upload but
        that still need to have their details filled in.
        """

        return self.session.query(
            Contract
        ).filter(
            Contract.purchaseordernumber is None
        ).all()

    def get_daily_contracts(self):  # defaults to today
        """
        Get today's contracts (and the vendors) for the daily email.
        """

        today_string = datetime.datetime.today().strftime('%Y-%m-%d')
        contracts = self.session.query(
            Contract.doc_cloud_id,
            Vendor.name
        ).filter(
            Contract.dateadded == today_string
        ).filter(
            Contract.vendorid == Vendor.id
        ).all()
        return contracts

    def get_people_associated_with_vendor(self, name):
        """
        Get people assiciated with vendor.
        """

        recccs = self.session.query(
            Person.name
        ).filter(
            Vendor.id == VendorOfficer.vendorid
        ).filter(
            Person.id == VendorOfficer.personid
        ).filter(
            Vendor.name == name
        ).all()
        return [str(i[0]) for i in recccs]

    def get_state_contributions(self, name):
        recccs = self.session.query(
            EthicsRecord
        ).filter(
            EthicsRecord.contributorname == name
        ).all()
        recccs.sort(key=lambda x: dateutil.parser.parse(x.receiptdate))
        return recccs

    def __exit__(self, type, value, traceback):
        """
        Called when the database is closed.
        """

        self.session.close()


def check_page(page_no):
    '''
    Run the scraper. Need a class here? Just function?
    '''

    # log.info('{} | {} | Daily scraper run check_page: {}'.format(
    #     run_id,
    #     get_timestamp(),
    #     str(page_no))
    # )
    doc_cloud_project = DocumentCloudProject()
    lens_repo = LensRepository()
    html = get_contract_index_page(page_no)
    output = get_po_numbers_from_index_page(html)
    for purchaseorderno in output:
        # log.info('{} | {} | Daily scraper found po {}'.format(
        #     run_id, get_timestamp(), purchaseorderno))
        try:
            lens_repo.sync(purchaseorderno)
            doc_cloud_project.add_contract(purchaseorderno)
        except urllib2.HTTPError, error:
            log.exception(error, exc_info=True)
            # log.warning(
            #     '{} | {} | Contract not posted publically | {}'.format(
            #         run_id, get_timestamp(), purchaseorderno
            #     )
            # )
