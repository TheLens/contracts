
"""
These models gather and organize published contracts from the city.
"""

import os
import subprocess
import re
import urllib2
import datetime
import uuid
import dateutil
from bs4 import BeautifulSoup
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker

from pythondocumentcloud import DocumentCloud
from contracts.db import (
    Vendor,
    Contract,
    Person,
    Department,
    VendorOfficer,
    EthicsRecord
)
from contracts import (
    log,
    PROJECT_DIR,
    VENDORS_LOCATION,
    CORPUS_LOC,
    DOC_CLOUD_USERNAME,
    DOC_CLOUD_PASSWORD,
    PURCHASE_ORDER_LOCATION,
    CONNECTION_STRING,
    BIDS_LOCATION
)


class PurchaseOrder(object):
    """
    A purchase order has a PO number. A PO number is an authorization to
    purchase. It gets associated with a city contract once the authorization
    goes through.

    A PO number is used to track a contract in the city's purchasing system.
    """

    def __init__(self, purchase_order_no, download_attachments=True):
        '''
        A purchase order number.
        '''

        # this is a uuid that is unique to a given run of the program.
        # Grep for it in the log file to see a certain run
        self.run_id = " " + str(uuid.uuid1())

        if not valid_purchase_order(purchase_order_no):
            # log.info(
            #     '{} | {} | Skipping. Not a valid purchaseorder | {}'.format(
            #         run_id, get_timestamp(), purchaseorderno
            #     )
            # )
            return
        html = self.get_html(purchase_order_no)
        self.soup = BeautifulSoup(html)
        self.vendor_id_city = self.get_vendor_id(html)
        self.download_vendor_profile(self.vendor_id_city)
        self.description = self.get_description(self.soup)
        try:
            self.vendor_name = self.get_vendor_name(self.soup)
        except IOError:
            self.vendor_name = "unknown"
            # log.info(
            #     '{} | Skipping. No associated vendor info | {}'.format(
            #         run_id, get_timestamp(), purchaseorderno, purchaseorderno
            #     )
            # )
            return
        self.department = self.get_department(self.soup)
        self.k_number = self.get_knumber(self.soup)
        self.purchaseorder = self.get_purchase_order(self.soup)

        self.attachments = self.get_attachments(self.soup)
        if download_attachments:
            for attachment in self.attachments:
                self.download_attachment(attachment)
        self.data = self.get_data()
        self.title = self.vendor_name + " : " + self.description

    @staticmethod
    def check_invalid(html):
        """
        Sometimes invalid purchase orders are posted. Check if this is one of
        those.

        :param html: The (contract page's) HTML.
        :type html: string
        :returns: boolean. True if an invalid contract page, False if valid.
        """

        no_vendor_string = "There are no vendor distributors found " + \
            "for this master blanket/contract"

        if no_vendor_string in html:
            return True
        else:
            return False

    def get_data(self):
        """
        Return metadata (from DocumentCloud).

        :returns: dict. The metadata for this contract page's HTML.
        """

        output = {}
        output['vendor_id'] = self.vendor_id_city
        output['purchase order'] = self.purchaseorder
        output['contract number'] = self.k_number
        output['department'] = self.department
        output['vendor'] = self.vendor_name

        return output

    @staticmethod
    def download_attachment(attachment):
        """
        Download an attachment associated with a purchase order.

        :param attachment: ???
        :type attachment: ???
        """

        bidnumber = re.search('[0-9]+', attachment.get('href')).group()
        bid_file_location = BIDS_LOCATION + bidnumber + ".pdf"
        if not os.path.isfile(bid_file_location):
            download_attachment_file(bidnumber, bid_file_location)
            # log.info(
            #     '{} | {} | Downloaded bid {} associated with purchase ' +
            #     'order {} | {}'.format(
            #         run_id, get_timestamp(), bidnumber,
            #         self.purchaseorder, self.purchaseorder
            #     )
            # )
        else:
            pass
            # log.info(
            #     '{} | {} | Already have bid {} for purchase ' +
            #     'order {} | {}'.format(
            #         run_id, get_timestamp(), bidnumber,
            #         self.purchaseorder, self.purchaseorder
            #     )
            # )

    def get_html(self, purchase_order_no):
        """
        Check to see if the purchase order should be downloaded.
        If so, then download it.

        :param purchase_order_no: The contract's unique ID on DocumentCloud.
        :type purchase_order_no: string
        :returns: ???
        """

        if os.path.isfile(PURCHASE_ORDER_LOCATION + purchase_order_no):
            # log.info(
            #     '{} | {} | Already have purchase order | {}'.format(
            #         run_id, get_timestamp(), purchase_order_no
            #     )
            # )
            return "".join([i.replace("\n", "") for i in open(
                PURCHASE_ORDER_LOCATION + purchase_order_no)])
        else:
            self.download_purchaseorder(purchase_order_no)

    @staticmethod
    def download_purchaseorder(purchaseorderno):
        """
        Download the HTML associated with a purchase order.

        :param purchaseorderno: The contract's unique ID on DocumentCloud.
        :type purchaseorderno: string
        :returns: ???
        """

        if not valid_purchase_order(purchaseorderno):
            # log.info("not a valid po {}".format(purchaseorderno))
            return
        if not os.path.exists(PURCHASE_ORDER_LOCATION + purchaseorderno):
            url = (
                'http://www.purchasing.cityofno.com/bso/external/' +
                'purchaseorder/poSummary.sdo?docId=' + purchaseorderno +
                '&releaseNbr=0&parentUrl=contract')
            # log.info(
            #     '{} | {} | Attempting to download url | {}'.format(
            #         run_id, get_timestamp(), url
            #     )
            # )
            response = urllib2.urlopen(url)
            html = response.read()
            with open(PURCHASE_ORDER_LOCATION + purchaseorderno, 'w') as fname:
                fname.write(html)
                # log.info(
                #     '{} | {} | Downloaded purchase order | {}'.format(
                #         run_id, get_timestamp(), purchaseorderno
                #     )
                # )

    @staticmethod
    def download_vendor_profile(vendor_id_city):
        """
        Download the vendor page associated with a purchase order, if we don't
        have the vendor page already.

        :param vendor_id_city: ???.
        :type vendor_id_city: ???
        """

        vendor_file_location = VENDORS_LOCATION + vendor_id_city
        if not os.path.isfile(vendor_file_location):
            try:
                response = urllib2.urlopen(
                    'http://www.purchasing.cityofno.com/bso/external/vendor/' +
                    'vendorProfileOrgInfo.sdo?external=true&vendorId=' +
                    'vendor_id_city')
                html = response.read()
                with open(vendor_file_location, 'w') as filename:
                    filename.write(html)
                # log.info(
                #     '{} | {} | Downloaded vendor file | {}'.format(
                #         run_id, get_timestamp(), vendor_id_city
                #     )
                # )
            except urllib2.HTTPError:
                pass
                # log.info(
                #     '{} | {} | Could not download vendor file | {}'.format(
                #         run_id, get_timestamp(), vendor_id_city
                #     )
                # )
        else:
            pass
            # log.info(
            #     '{} | {} | Skipped vendor file. Already present | {}'.format(
            #         run_id, get_timestamp(), vendor_id_city
            #     )
            # )

    @staticmethod
    def get_attachments(soup):
        """
        Find the attachments to download from the HTML.

        :param soup: A BeautifulSoup object for the contract page's HTML.
        :type soup: BeautifulSoup object
        :returns: ???
        """

        try:
            main_table = soup.select('.table-01').pop()
            metadatarow = main_table.findChildren(
                ['tr']
            )[2].findChildren(
                ['td']
            )[0].findChildren(
                ['table']
            )[0].findChildren(
                ['tr']
            )

            todownload = metadatarow[16].findChildren(
                ['td']
            )[1].findChildren(
                ['a']
            )
        except IndexError:
            return []  # sometimes the city does not include them
        return todownload

    @staticmethod
    def get_vendor_id(html):
        '''
        Find the vendor id in the HTML.

        :param html: The contract page HTML
        :type html: string
        :returns: string. The vendor ID, or an empty string if none found.
        '''

        pattern = r"(?<=ExternalVendorProfile\(')\d+"
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

    @staticmethod
    def get_description(soup):
        '''
        Find the description in the HTML.

        :param soup: A BeautifulSoup object for the contract page HTML.
        :type soup: BeautifulSoup object.
        :returns: string. The (contract) description.
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

        :param soup: A BeautifulSoup object for the contract page HTML.
        :type soup: BeautifulSoup object.
        :returns: string. The contract vendor's name.
        '''

        try:
            vendorrow = soup(text=re.compile(r'Vendor:'))[0].parent.parent
            vendorlinktext = vendorrow.findChildren(['td'])[1].findChildren(
                ['a'])[0].contents.pop().strip()
            # Vno periods in vendor names:
            vendor = vendorlinktext.split('-')[1].strip().replace(".", "")

            # Convert to uppercase for DocumentCloud. Search queries are also
            # converted to uppercase so we can find matches.
            vendor = vendor.upper()

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

            # Convert to uppercase for DocumentCloud. Search queries are also
            # converted to uppercase so we can find matches.
            vendor_name = vendor_name.upper()

            return vendor_name

    @staticmethod
    def get_knumber(soup):
        '''
        Find the k number in the HTML.

        :param soup: A BeautifulSoup object for the contract page HTML.
        :type soup: BeautifulSoup object.
        :returns: string. The contract's K number.
        '''

        main_table = soup.select('.table-01').pop()
        metadatarow = main_table.findChildren(
            ['tr']
        )[2].findChildren(
            ['td']
        )[0].findChildren(
            ['table']
        )[0].findChildren(
            ['tr']
        )

        try:
            knumber = metadatarow[6].findChildren(
                ['td']
            )[1].contents.pop().replace(
                'k',
                ''
            ).replace("m", '').strip().replace("M", "")
        except:
            knumber = "unknown"

        if len(knumber) == 0:
            knumber = "unknown"

        return knumber

    @staticmethod
    def get_purchase_order(soup):
        '''
        Find the purchase order in the HTML.

        :param soup: A BeautifulSoup object for the contract page HTML.
        :type soup: BeautifulSoup object.
        :returns: string. The contract's purchase order number.
        '''

        main_table = soup.select('.table-01').pop()
        purchase_order = main_table.findChildren(
            ['tr']
        )[2].findChildren(
            ['td']
        )[0].findChildren(
            ['table']
        )[0].findChildren(
            ['tr']
        )[1].findChildren(
            ['td']
        )[1].contents.pop().strip()

        return purchase_order

    @staticmethod
    def get_department(soup):
        '''
        Find the department in the HTML.

        :param soup: A BeautifulSoup object for the contract page HTML.
        :type soup: BeautifulSoup object.
        :returns: string. The contract's department.
        '''

        main_table = soup.select('.table-01').pop()
        metadatarow = main_table.findChildren(['tr'])[2].findChildren(
            ['td'])[0].findChildren(['table'])[0].findChildren(['tr'])
        department = metadatarow[5].findChildren(
            ['td'])[1].contents.pop().strip()

        # Convert to uppercase for DocumentCloud. Search queries are also
        # converted to uppercase so we can find matches.
        department = department.upper()

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

    def __init__(self):
        # do not include these aviation contracts. They are not posted on the
        # city's public purchasing site (but are included in the city's
        # contract logs.)
        self.skiplist = self.get_skip_list()
        self.purchaseorders_location = CORPUS_LOC + "/purchaseorders/"

    def download_purchaseorder(self, purchase_order_no):
        '''
        Download (the contract matching this purchase order number?).

        :param purchase_order_no: The contract's unique ID for DocumentCloud.
        :type purchase_order_no: string.
        :returns: ???
        '''

        if purchase_order_no in self.skiplist:
            # log.warning(
            #     '{} | {} | Contract is in the skiplist | {}'.format(
            #         run_id, get_timestamp(), purchase_order_no)
            # )
            return
        if not valid_purchase_order(purchase_order_no):
            # log.warning(
            #     '{} | {} | Invalid purchase order | {}'.format(
            #         run_id, get_timestamp(), purchase_order_no)
            # )
            return
        file_loc = self.purchaseorders_location + purchase_order_no
        if not os.path.isfile(file_loc):
            response = urllib2.urlopen(
                'http://www.purchasing.cityofno.com/bso/external/' +
                'purchaseorder/poSummary.sdo?docId=' + purchase_order_no +
                '&releaseNbr=0&parentUrl=contract')
            html = response.read()
            self.write_pos(html, file_loc)

    @staticmethod
    def write_pos(html, file_location):
        '''
        docstring

        :param html: The contract's unique ID for DocumentCloud.
        :type html: string.
        :param file_location: The contract's unique ID for DocumentCloud.
        :type file_location: string.
        :returns: ???
        '''

        with open(file_location, 'w') as f:
            # log.warning(
            #     '{} | {} | Writing purchase_order_no to file | {}'.format(
            #         run_id, get_timestamp(), file_location)
            # )
            f.write(html)  # python will convert \n to os.linesep

    def sync(self, purchase_order_no):
        '''
        docstring

        :param purchase_order_no: The contract's unique ID for DocumentCloud.
        :type purchase_order_no: string.
        :returns: ???
        '''

        if purchase_order_no in self.skiplist:
            # log.warning(
            #     '{} | {} | Contract is in the skiplist | {}'.format(
            #         run_id, get_timestamp(), purchase_order_no
            #     )
            # )
            return
        file_loc = self.purchaseorders_location + purchase_order_no
        if not os.path.isfile(file_loc):
            self.download_purchaseorder(purchase_order_no)
        else:
            pass
            # log.warning(
            #     '{} | {} | The Lens repo already has this ' +
            #     'purchase_order_no | {}'.format(
            #         run_id, get_timestamp(), purchase_order_no)
            # )

    @staticmethod
    def get_skip_list():
        """
        Some contracts are not posted on the city's site even though they are
        included in the city's contract inventory. We put these contracts on a
        skip list so they are ignored in code.

        :returns: list. Includes the contract codes to skip.
        """

        # TODO: skip list should not be hard coded
        skiplist_loc = PROJECT_DIR + '/data/skiplist.txt'
        skiplist = open(skiplist_loc)
        skiplist = [l.replace("\n", "") for l in skiplist]

        return skiplist


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
        '''
        Fetches the contract with the specified field and value.

        :param field: The key for searching through the DocumentCloud API.
        :type field: string.
        :param value: The key's value.
        :type value: string.
        :returns: ???. The matching contract(s).
        '''

        searchterm = "'" + field + "':" + "'" + value + "'"
        doc = self.client.documents.search(searchterm).pop()

        return doc

    def has_contract(self, field, value):
        '''
        Checks if there is a contract for this field and value.

        :param field: The key for searching through the DocumentCloud API.
        :type field: string.
        :param value: The key's value.
        :type value: string.
        :returns: boolean. True if there is a contract found, False if not.
        '''

        searchterm = "'" + field + "':" + "'" + value + "'"

        if len(self.client.documents.search(searchterm)) < 1:
            return False  # it is a new contract

        return True  # it is an existing contract. We know the k-number

    def add_contract(self, purchase_order_no):
        '''
        docstring

        :param purchase_order_no: The contract's unique ID in DocumentCloud.
        :type purchase_order_no: string.
        :returns: ???
        '''

        purchase_order_regex = re.compile(r'[A-Z]{2}\d+')
        # log.info(
        #     '{} | {} | Attempting to add {} to DocumentCloud | {}'.format(
        #         run_id, get_timestamp(), purchase_order_no, purchase_order_no
        #     )
        # )
        if not purchase_order_regex.match(purchase_order_no):
            # log.info(
            #     "{} doesn't look like a valid purchase order. " +
            #     "Skipping for now".format(purchase_order_no)
            # )
            return
        if purchase_order_no in self.skiplist:
            # log.info(
            #     '{} | {} | Not adding {} to DocumentCloud. In skiplist ' +
            #     '| {}'.format(
            #         run_id, get_timestamp(), purchase_order_no,
            #         purchase_order_no
            #     )
            # )
            return
        if not self.has_contract("purchase order", purchase_order_no):
            try:
                purchase_order = PurchaseOrder(purchase_order_no)
            except IndexError:
                # log.info(
                #     '{} | {} | Something looks wrong with the format on ' +
                #     'this one. Skipping for now | {}'.format(
                #         run_id, get_timestamp(),
                #         purchase_order_no, purchase_order_no
                #     )
                # )
                return
            # log.info(
            #     '{} | {} | Adding {} to DocumentCloud | {}'.format(
            #         run_id, get_timestamp(),
            #         purchase_order_no, purchase_order_no
            #     )
            # )
            if len(purchase_order.attachments) > 0:
                counter = 1
                for attachment in purchase_order.attachments:
                    bidnumber = re.search(
                        '[0-9]+', attachment.get('href')).group()
                    bid_file_location = BIDS_LOCATION + \
                        bidnumber + ".pdf"
                    extra_string = ""
                    if counter > 1:
                        extra_string = str(counter) + " of " + \
                            str(len(purchase_order.attachments))
                    self.upload_contract(
                        bid_file_location,
                        purchase_order.data,
                        purchase_order.description + extra_string,
                        purchase_order.title + extra_string
                    )
                    counter += 1
        else:
            pass
            # log.info(
            #     '{} | {} | Not adding {} to DocumentCloud. Already up ' +
            #     'there | {}'.format(
            #         run_id, get_timestamp(),
            #         purchase_order_no, purchase_order_no
            #     )
            # )

    def get_all_docs(self):
        '''
        Runs a query for all of the contracts in our DocumentCloud project.

        :returns: list. A list of all of the project's contracts.
        '''

        if self.docs is None:
            self.docs = self.client.documents.search(
                'projectid: 1542-city-of-new-orleans-contracts')

        return self.docs

    def upload_contract(self, fname, data, description, title):
        '''
        This uploads a contract onto DcoumentCloud.

        :param file: The contract PDF file?
        :type file: PDF
        :param data: The contract's (metadata).
        :type data: dict. ???
        :param description: The contract's description.
        :type description: string.
        :param title: The contract's title.
        :type title: string.
        :returns: ???
        '''

        if len(data['contract number']) < 1:
            # log.info(
            #     '{} | {} | Not adding {} to DocumentCloud. '
            #     'Contract number {} is null | {}'.format(
            #         run_id, get_timestamp(),
            #         data['purchase order'],
            #         data['contract number'],
            #         data['purchase order']
            #     )
            # )
            return  # do not upload. There is a problem
        newcontract = self.client.documents.upload(
            fname,
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

    def get_metadata(self, doc_cloud_id, meta_field):
        '''
        Fetches the metadata associated with a contract on DocumentCloud.
        Needs to get for departments and vendors, then uppercase them and
        then update them in DC.

        :param doc_cloud_id: The contract's unique ID in DocumentCloud.
        :type doc_cloud_id: string
        :param meta_field: The specific metadata field for this contract.
        :type meta_field: string
        :returns: ???
        '''

        contract = self.client.documents.get(doc_cloud_id)
        # contract.data[meta_field] = new_meta_data_value
        # contract.put()

        return contract

    def update_metadata(self, doc_cloud_id, meta_field, new_meta_data_value):
        '''
        Updates the metadata associated with the contracts on DocumentCloud.

        :param doc_cloud_id: The contract's unique ID in DocumentCloud.
        :type doc_cloud_id: string
        :param meta_field: The specific metadata field for this contract.
        :type meta_field: string
        :param new_meta_data_value: The new metadata value for this field.
        :type new_meta_data_value: string
        '''

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

        :returns: ???
        """

        pass
        # to do Tom Thoren

    # refactor to take a type
    def add_vendor(self, vendor):
        """
        Add vendor to the Lens database.

        :param vendor: The vendor to add to our database.
        :type vendor: string
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
        Add department to the Lens database.

        :param meta_field: The department to add to our database.
        :type meta_field: string
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
        Add a contract to the Lens database.

        :param meta_field: The contract to add to our database.
        :type meta_field: string
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
        '''
        Fetches a list of all of the contract IDs in DocumentCloud project.

        :returns: list. A list of all IDs in DocumentCloud project.
        '''

        doc_id_query = self.session.query(
            Contract.doc_cloud_id
        ).order_by(
            desc(Contract.dateadded)
        ).all()

        dcids = [i[0] for i in doc_id_query]

        return dcids

    def update_contract_from_doc_cloud_doc(self, doc_cloud_id, fields):
        """
        Update an existing contract in the Lens database.
        TODO: compare to add_contract()

        :param doc_cloud_id: The unique ID in DocumentCloud.
        :type doc_cloud_id: string
        :param fields: The metadata fields to add along with the contract?
        :type fields: dict
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

    def has_contract(self, purchase_order_no):
        """
        Checks if the database (?) already has this contract.

        :param purchase_order_no: The unique ID in the city's website.
        :type purchase_order_no: string
        :returns: boolean. True if the contract is present, False if not.
        """

        indb = self.session.query(
            Contract
        ).filter(
            Contract.purchaseordernumber == purchase_order_no
        ).count()

        if indb == 1:
            return True
        else:
            return False

    def get_contract(self, purchase_order_no):
        """
        Get a contract from the database.

        :param purchase_order_no: The unique ID in the city's website.
        :type purchase_order_no: string
        :returns: dict. A dict (?) for the matching contract.
        """

        query = self.session.query(
            Contract
        ).filter(
            Contract.purchaseordernumber == purchase_order_no
        ).first()

        return query

    def get_contract_doc_cloud_id(self, doc_cloud_id):
        """
        Get a contract from the DocumentCloud project.

        :param doc_cloud_id: The unique ID in the DocumentCloud project.
        :type doc_cloud_id: string
        :returns: dict. A dict (?) for the matching contract.
        """

        query = self.session.query(
            Contract
        ).filter(
            Contract.doc_cloud_id == doc_cloud_id
        ).first()

        return query

    def get_lens_vendor_id(self, vendor):
        """
        Get a vendor's ID from our database.
        TODO: refactor

        :param vendor: The vendor.
        :type vendor: string
        :returns: string. The ID for the vendor.
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
        Get the department's ID from our database.
        TODO: refactor

        :param department: The department.
        :type department: string
        :returns: string. The ID for the department.
        """

        department_id = self.session.query(
            Department
        ).filter(
            Department.name == department
        ).first().id

        return department_id

    def get_half_filled_contracts(self):
        """
        DocumentCloud doesn't give immediate access to all document properties.
        This pulls out the contracts in the database added during upload but
        that still need to have their details filled in.

        :returns: SQLAlchemy query result.
        """

        query = self.session.query(
            Contract
        ).filter(
            Contract.purchaseordernumber is None
        ).all()

        return query

    def get_daily_contracts(self):  # defaults to today
        """
        Get today's contracts (and the vendors) for the daily email.

        :returns: A list of dicts (?) for the daily contracts.
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
        Get a list of people associated with the vendor.

        :param name: The vendor name.
        :type name: string
        :returns: list. The people who are associated with this vendor.
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
        '''
        Find the state contributions for this contributor.

        :param name: The name.
        :type name: string
        :returns: list. The contributions associated with this name.
        '''

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

    :param page_no: The page to check (?).
    :type page_no: string
    '''

    html = get_contract_index_page(page_no)
    output = get_po_numbers_from_index_page(html)
    for purchaseorderno in output:
        log.info('Daily scraper found po %s', purchaseorderno)
        try:
            LensRepository().sync(purchaseorderno)
            DocumentCloudProject().add_contract(purchaseorderno)
        except urllib2.HTTPError, error:
            log.exception(error, exc_info=True)
            log.exception(
                'Contract not posted publically. ' +
                'Purchase order=%s', purchaseorderno
            )


def download_attachment_file(bid_no, bid_file_location):
    '''
    Download the attachment file found on contract page.

    :param bid_no: ???
    :type bid_no: ???
    :param bid_file_location: ???
    :type bid_file_location: ???
    :returns: ???
    '''

    if not os.path.exists(bid_no):
        process = subprocess.Popen([
            'curl',
            '-o',
            bid_file_location,
            'http://www.purchasing.cityofno.com/bso/external/document/' +
            'attachments/attachmentFileDetail.sdo',
            '-H',
            'Pragma: no-cache',
            '-H',
            'Origin: null',
            '-H',
            'Accept-Encoding: gzip,deflate,sdch',
            '-H',
            'Accept-Language: en-US,en;q=0.8',
            '-H',
            'Content-Type: multipart/form-data; ' +
            'boundary=----WebKitFormBoundaryP4a4C1okQYkBGBSG',
            '-H',
            'Accept: text/html,application/xhtml+xml,' +
            'application/xml;q=0.9,image/webp,*/*;q=0.8',
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
''' + bid_no + '''\r
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
''' + bid_no + '''\r
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
            '--compressed'
        ])
        process.wait()


def get_po_numbers_from_index_page(html):
    '''
    Take an index page of contracts. Return the contract numbers.
    '''

    pattern = '(?<=docId=)[A-Z][A-Z][0-9]+'
    return re.findall(pattern, html)


def valid_purchase_order(purchase_order_no):
    """
    A simple method to determine if this is a valid purchase order.
    """

    po_re = r'[A-Z]{2}\d{3,}'
    po_regex = re.compile(po_re)
    if po_regex.match(purchase_order_no):
        return True
    else:
        return False


def get_contract_index_page(pageno):
    '''
    Get a given page in the list of current contracts.
    '''

    data = (
        'mode=sort&letter=&currentPage=' + str(pageno) + '&querySql=%5B' +
        'PROCESSED%5D-75%3A1d%3A4a%3A-6d%3A34%3A14%3A-5c%3A47%3A-30%3A1b' +
        '%3A-74%3A16%3A-58%3A69%3A-1f%3A4c%3A13%3A50%3A-4%3A-12%3A24%3A6' +
        '0%3A-6e%3A-1b%3A49%3A2b%3A-6e%3A-11%3A-5f%3A7b%3A-a%3A-62%3A-30' +
        '%3A3%3A5%3A1f%3A-1%3A-25%3A-43%3A-19%3A-12%3A-1a%3A-71%3A6b%3A-' +
        '20%3A53%3A-11%3A50%3A-52%3A-46%3A-1a%3A69%3A5a%3A79%3A7d%3A45%3' +
        'A-44%3A72%3A1e%3A-46%3A3a%3A48%3A-60%3A-76%3A-76%3A57%3A-6%3A-4' +
        '0%3A0%3A7f%3A-3d%3A1e%3A-68%3A41%3A-80%3A-3d%3A-27%3A-44%3A6a%3' +
        'A-1e%3A-79%3A-68%3A58%3A-46%3A77%3A25%3A68%3A-53%3A7e%3A-15%3A1' +
        'c%3A-6b%3A6f%3A-2b%3A7d%3A41%3A10%3A-b%3Ab%3A23%3A32%3A-f%3A-62' +
        '%3A-48%3A3f%3A5f%3A-7d%3A2e%3A-7d%3A-62%3A41%3A-40%3A-6b%3A62%3' +
        'A4a%3A2c%3A1d%3A-1%3A29%3A-41%3A-60%3A5e%3A19%3A63%3A-55%3A-59%' +
        '3A39%3A61%3A54%3A-47%3A-31%3A-79%3A-6c%3A-1c%3Ab%3A-1b%3A-e%3A-' +
        '30%3A12%3A5%3A47%3A49%3A49%3A6c%3A-1e%3A57%3A52%3A-1b%3A-63%3A1' +
        'b%3A31%3A-9%3A6b%3A4f%3A30%3A-5%3A21%3A35%3A0%3A-4c%3A-20%3A67%' +
        '3A14%3A5a%3A3%3A57%3A-4c%3A-39%3A-1c%3A27%3A-1d%3A-38%3A19%3A-7' +
        '9%3A17%3A-78%3A-12%3A-71%3A-7b%3A46%3A-3e%3A20%3A3f%3A-2c%3A-7b' +
        '%3A69%3A-1b%3A6d%3A1c%3A-78%3A6b%3A7d%3A-68%3A-15%3A-6%3A0%3A49' +
        '%3A-31%3A25%3A-31%3A68%3A56%3A-7d%3A-2%3A-56%3A-5f%3A-20%3A60%3' +
        'A76%3A69%3A-9%3A2d%3A9%3A2c%3A50%3A2a%3A-65%3A7e%3A-66%3A-7f%3A' +
        '34%3A-5a%3A10%3A11%3A79%3A-50%3A-7b%3A-64%3A25%3A-7c%3A48%3A-40' +
        '%3A-7e%3A-e%3A-21%3A47%3A-5b%3A-5e%3A27%3A-4d%3A71%3A-f%3A-56%3' +
        'A1c%3A53%3A-5c%3A-61%3A0%3A-18%3A-40%3Ae%3A22%3A3c%3A-58%3A-55%' +
        '3A5e%3A-68%3Ac%3A-29%3A74%3A-2b%3A62%3A-1b%3A-2d%3A-33%3A48%3A-' +
        '37%3A-6%3Ad%3A6b%3A-22%3A4e%3A-44%3A10%3A45%3A-43%3A-2%3A-2b%3A' +
        '-17%3A13%3A7d%3A-1e%3A-56%3A-53%3A5d%3A44%3Ad%3A14%3A-20%3A71%3' +
        'A-1f%3A-59%3A-7b%3A-42%3A-5f%3A-10%3A-43%3A52%3A4e%3A-69%3A6e%3' +
        'A-75%3A7%3A-61%3A-4c%3A-62%3A6a%3A-37%3A23%3A3a%3A-5b%3A70%3A72' +
        '%3A1c%3A-14%3A63%3A71%3A33%3Aa%3A-20%3A-16%3A52%3A35%3A-10%3A-3' +
        '0%3A-42%3A-34%3A7%3A-49%3A-10%3A-63%3A-78%3A-13%3A-46%3A37%3A24' +
        '%3A2e%3A55%3A48%3A-18%3A-1c%3A-4b%3A-7c%3A-7d%3A10%3A5%3Aa%3A-1' +
        '4%3A-8%3A4a%3A1c%3A-34%3A47%3A-43%3A-4f%3A-45%3A-6b%3A-2a%3Aa%3' +
        'A-51%3A-72%3A5c%3A-66%3A33%3A-4e%3A18%3A4d%3A-27%3A3f%3A-d%3A23' +
        '%3A77%3A-2b%3A-41%3A-e%3A47%3A14%3A31%3A17%3A22%3A37%3A-39%3A66' +
        '%3A-3f%3A-1b%3A29%3A23%3A-5b%3A63%3A-54%3A15%3A-62%3A-76%3A-20%' +
        '3A58%3A-18%3A-7d%3A48%3A-57%3A-32%3A-1a%3A15%3A-10%3A79%3A68%3A' +
        '23%3A38%3A40%3A35%3A75%3A33%3A50%3A-2%3A-13%3A72%3A11%3A1a%3A35' +
        '%3A-3b%3A-80%3A-59%3A4e%3A-10%3A-3d%3A-9%3A6a%3A22%3A4c%3A-6d%3' +
        'A1e%3A5%3Ad%3A51%3A-78%3A-7a%3A-1d%3A44%3A3d%3A-1d%3A-36%3A-41%' +
        '3A-4d%3A15%3A23%3A5b%3A-7f%3A5b%3A-6c%3A-18%3A-2d%3A2%3A41%3A3d' +
        '%3A-3b%3A-40%3A22%3A14%3A-28%3A7%3A50%3A1c%3A28%3A-69%3A40%3A-1' +
        'f%3A3a%3A-7a%3A5%3A76%3A4%3A-6c%3A29%3A59%3A77%3A-34%3A-77%3A-7' +
        'c%3A-77%3A-2a%3A49%3A5a%3A-5e%3A4a%3A-7b%3A4d%3A-79%3A29%3A75%3' +
        'A52%3A57%3A6%3A52%3A33%3A23%3A-57%3A15%3A79%3A79%3A-8%3A-66%3A-' +
        '31%3A7f%3A-4c%3A35%3A26%3A-65%3A59%3A5f%3A3d%3A7c%3A-6c%3A-7f%3' +
        'A-1a%3A1b%3A49%3A-18%3A-75%3A-4f%3A2e%3A32%3A5d%3A-66%3A-37%3A3' +
        'b%3A-78%3A45%3A-6a%3A6f%3A-3e%3A-27%3A44%3A7f%3A40%3A-64%3A4c%3' +
        'A6%3A74%3A-53%3Ab%3A6b%3A-7d%3A28%3A62%3A-e%3A1d%3A-32%3A21%3A-' +
        '5%3A1a%3A35%3A61%3Ad%3Ac%3A-45%3A-33%3A24%3A66%3A30%3A65%3A2c%3' +
        'A-72%3A-78%3A-52%3A5a%3A-31%3A11%3A-15%3A4a%3Aa%3A-55%3A-31%3A-' +
        '9%3A20%3A-c%3A-46%3A-40%3A46%3Ad%3A7f%3A-34%3A57%3A-12%3A-7b%3A' +
        '55%3A-3f%3A-68%3A50%3A15%3A-21%3A-80%3A-41%3A-35%3A-70%3A-33%3A' +
        '-f%3A-42%3A-76%3A4f%3A33%3A-44%3A29%3A64%3A-45%3A12%3A1b%3A-1%3' +
        'A-7f%3Ac%3A-32%3A-1f%3A51%3A-29%3A-1c%3A24%3A6a%3A-80%3A1f%3A-2' +
        '8%3A-7d%3A-42%3Aa%3A11%3A77%3A-7a%3A-9%3Ab%3A-4c%3A-24%3A-5f%3A' +
        '2d%3A-e%3A-66%3A3c%3A-1%3A2d%3A-1a%3A65%3A-59%3A2a%3A-43%3A8%3A' +
        '-30%3A-3c%3A-6c%3A3%3A2f%3A7f%3A-4e%3A-5f%3Ab%3A44%3A60%3A-38%3' +
        'A-7a%3A68%3A-63%3A-7d%3A7d%3A-16%3A-a%3A2b%3A51%3A2e%3A5a%3A-6d' +
        '%3A-5d%3A-5b%3A-71%3A29%3A-6f%3A-26%3A-55%3A-56%3A-d%3A-10%3A65' +
        '%3A-2c%3A-41%3A5c%3A-2b%3A-49%3A-37%3A6%3Ae%3A6c%3A53%3A-62%3A-' +
        '6b%3A-34%3A3d%3A-74%3A-f%3A-47%3A9%3A-5a%3A-16%3A-1d%3A9%3A36%3' +
        'A-3%3A-3%3A-9%3A69%3A-3b%3A-24%3A3a%3A42%3A47%3A2a%3A-48%3A3a%3' +
        'Ae%3A7d%3A-4f%3A79%3A-b%3A-2d%3A-6%3A3%3A11%3A7%3A-7b%3A-1b%3A3' +
        '3%3A1c%3A-f%3A3c%3A24%3A-31%3A-4f%3A-56%3A-54%3A-74%3A5e%3A33%3' +
        'A39%3A-7c%3A76%3A-9%3A-e%3A-3a%3A-14%3A-1d%3A3d%3A-47%3A65%3A-3' +
        'f%3A3b%3A21%3A-79%3A-5b%3A-1%3A-4a%3A55%3A11%3A-f%3A-80%3A-6e%3' +
        'A6b%3A2c%3A10%3A-25%3A13%3A74%3A-2f%3A-9%3A63%3A11%3A-16%3A13%3' +
        'A-20%3A-4d%3A6c%3A-4e%3Ab%3A-3d%3Af%3A-1c%3A-73%3A16%3A-75%3A46' +
        '%3A-76%3A1b%3A38%3A-43%3A77%3A73%3A-7e%3A-66%3A-12%3A-45%3A29%3' +
        'A42%3A46%3A-6e%3A58%3A-3e%3A-26%3A-56%3A56%3A1c%3A6b%3A-71%3A-2' +
        '%3A33%3A-61%3A4%3A-1d%3A34%3A2d%3A54%3A68%3A1f%3A-14%3A48%3A-7f' +
        '%3A68%3A53%3A-26%3A-2d%3A3f%3A-71%3A0%3A7a%3A3b%3A34%3A-1b%3A-5' +
        '0%3A30%3A-35%3A62%3A56%3A-18%3A7%3A35%3A-6%3A69%3A-14%3A6f%3A35' +
        '%3A-7b%3A4b%3A-2c%3A-6d%3A76%3A-61%3A-20%3A-49%3A-13%3A42%3A4d%' +
        '3A46%3A-5a%3A-30%3A6d%3A14%3A4d%3A46%3A6a%3A77%3A2f%3A-26%3A44%' +
        '3A3%3A-3a%3A-26%3A-56%3A1d%3A-30%3A-e%3A-6a%3A-80%3A-28%3A-4a%3' +
        'A5a%3A-4c%3A1e%3A4f%3A44%3A50%3A3a%3A78%3A-16%3A8%3A-56%3A-47%3' +
        'A-20%3A4c%3A-39%3A-1%3A-d%3A4b%3A25%3A-70%3A-22%3A-44%3A-73%3A-' +
        '25%3A-1%3A-2%3A6e%3A-40%3A37%3A56%3A4b%3A25%3A42%3A-72%3Ad%3A48' +
        '%3A4e%3A51%3A54%3A-3a%3A67%3A-64%3A-7b%3A-51%3A7%3A-4f%3A-29%3A' +
        '-78%3A-1b%3A-78%3A-62%3A-6e%3A-1c%3A-7%3A-34%3A-39%3A6e%3A-62%3' +
        'A21%3A-75%3A58%3A-6d%3A-2b%3A-6e%3A-6d%3A66%3A0%3A-24%3A-73%3A7' +
        '7%3A36%3A-23%3A-76%3A-1e%3A1b%3A-15%3A-44%3A5a%3A-3%3A61%3A-6e%' +
        '3A-44%3A49%3A-11%3A38%3A-46%3A54%3A-37%3A-33%3A23%3A2d%3A-3f%3A' +
        '-37%3A-7e%3A50%3A6%3A4e%3A12%3A-6e%3A-2b%3A24%3A-5%3A7e%3A4%3A-' +
        '37%3A33%3A-18%3A29%3A1a%3Ac%3A18%3A-7d%3A-52%3A60%3A-5f%3A-5f%3' +
        'A-28%3A-62%3A74%3A0%3A52%3Ac%3A-24%3A7e%3A-43%3A60%3A-1c%3A55%3' +
        'A-a%3A1f%3A-3%3Ad%3A68%3A2b%3A58%3A2e%3A7e%3A7f%3A27%3A31%3A29%' +
        '3A55%3A2%3A-65%3A5%3A-5c%3A-55%3A-65%3A-5a%3A5e%3A51%3A7b%3A-59' +
        '%3A-4%3A-55%3A66%3A6c&sortBy=beginDate&sortByIndex=5&sortByDesc' +
        'ending=true&masterFlag=true&module=&searchFor=%2Fexternal%2Fadv' +
        'search%2FsearchContract&searchFor=%2Fadvsearch%2FbuyerSearchCon' +
        'tract&advancedSearchJspName=%2Fexternal%2Fadvsearch%2FadvancedS' +
        'earch.jsp&searchAny=false&poNbr=&poTypeParm=&desc=&buyer=&vendo' +
        'rName=&bidNbr=&typeCode=&catalogId=&expireFromDateStr=&expireTo' +
        'DateStr=&itemDesc=&orgId=&departmentPrefix=&classId=&classItemI' +
        'd=&commodityCode=&includeExpired=on')

    url = 'http://www.purchasing.cityofno.com/bso/' + \
        'external/advsearch/searchContract.sdo'

    req = urllib2.Request(url=url, data=data)
    req.add_header('Pragma', ' no-cache')
    req.add_header('Origin', 'http://www.purchasing.cityofno.com')
    req.add_header('Accept-Encoding', 'gzip, deflate')
    req.add_header('Content-Type', 'application/x-www-form-urlencoded')
    req.add_header(
        'Accept',
        'text/add_contracthtml,application/xhtml+xml,application/xml;' +
        'q=0.9,image/webp,*/*;q=0.8'
    )
    req.add_header('Cache-Control', 'no-cache')
    req.add_header(
        'Referer',
        'http://www.purchasing.cityofno.com/bso/external/advsearch/' +
        'searchContract.sdo'
    )
    req.add_header('Connection', 'keep-alive')
    req.add_header('DNT', '1')

    output = ""
    response = urllib2.urlopen(req)
    output = response.read()
    response.close()

    return output
