
'''
Represents a purchase order object.
'''

import os
import re
import urllib2
import uuid
# import subprocess
from bs4 import BeautifulSoup
from contracts.lib.utilities import Utilities
from contracts import (
    VENDORS_LOCATION,
    PURCHASE_ORDER_LOCATION,
    # BIDS_LOCATION,
    log
)


class PurchaseOrder(object):
    '''
    A purchase order number is assigned when the order is authorized to
    purchase a service or good. The numbers gets associated with a city
    contract. This number is used to track a contract in the city's
    purchasing system.

    All contracts have purchase orders, but not all purchase orders are for
    contracts.
    '''

    def __init__(self, purchase_order_number):  # , download_attachments=True):
        # this is a uuid that is unique to a given run of the program.
        # Grep for it in the log file to see a certain run
        self.run_id = " " + str(uuid.uuid1())

        output = Utilities().check_if_valid_purchase_order_format(
            purchase_order_number)
        if output is False:
            return

        html = self.get_html(purchase_order_number)
        soup = BeautifulSoup(html)
        self.vendor_id_city = self.get_vendor_id(html)
        self.download_vendor_profile(self.vendor_id_city)
        self.description = self.get_description(soup)
        try:
            self.vendor_name = self.get_vendor_name(soup)
        except IOError:
            self.vendor_name = "unknown"
            # log.info(
            #     '{} | Skipping. No associated vendor info | {}'.format(
            #         run_id, get_timestamp(), purchaseorderno, purchaseorderno
            #     )
            # )
            return
        self.department = self.get_department(soup)
        self.k_number = self.get_knumber(soup)
        self.purchaseorder = self.get_purchase_order(soup)

        self.attachments = self.get_attachments(soup)

        # TODO: Remove from __init__. Downloading a file should be explicit,
        # not implicit.
        # if download_attachments:
        #     for attachment in self.attachments:
        #         self.download_attachment(attachment)
        self.data = self.get_data()
        self.title = self.vendor_name + " : " + self.description

    def get_data(self):
        '''
        Return metadata, which is scraped and parsed from the HTML.

        :returns: dict. The metadata for this contract, such as title, date \
                        added, description, purchase order number and more.
        '''

        output = {}
        output['vendor_id'] = self.vendor_id_city
        output['purchase order'] = self.purchaseorder
        output['contract number'] = self.k_number
        output['department'] = self.department
        output['vendor'] = self.vendor_name

        return output

    # def download_attachment(self, attachment):
    #     '''
    #     Download an attachment associated with a purchase order.

    #     :param attachment: ???
    #     :type attachment: ???
    #     '''

    #     bidnumber = re.search('[0-9]+', attachment.get('href')).group()
    #     bid_file_location = BIDS_LOCATION + bidnumber + ".pdf"
    #     if not os.path.isfile(bid_file_location):
    #         self.download_attachment_file(bidnumber, bid_file_location)
    #         # log.info(
    #         #     '{} | {} | Downloaded bid {} associated with purchase ' +
    #         #     'order {} | {}'.format(
    #         #         run_id, get_timestamp(), bidnumber,
    #         #         self.purchaseorder, self.purchaseorder
    #         #     )
    #         # )
    #     # else:
    #         # pass
    #         # log.info(
    #         #     '{} | {} | Already have bid {} for purchase ' +
    #         #     'order {} | {}'.format(
    #         #         run_id, get_timestamp(), bidnumber,
    #         #         self.purchaseorder, self.purchaseorder
    #         #     )
    #         # )

    def get_html(self, purchase_order_number):
        '''
        Check to see if the purchase order should be downloaded.
        If so, then download it.

        :param purchase_order_number: The contract's unique ID on \
        DocumentCloud.
        :type purchase_order_number: string
        :returns: ???
        '''

        file_location = PURCHASE_ORDER_LOCATION + '/' + purchase_order_number

        if os.path.isfile(file_location):
            # log.info(
            #     '{} | {} | Already have purchase order | {}'.format(
            #         run_id, get_timestamp(), purchase_order_number
            #     )
            # )
            return "".join([i.replace("\n", "") for i in open(file_location)])
        else:
            self.download_purchase_order(purchase_order_number)

    def download_purchase_order(self, purchase_order_number):
        '''
        Download the HTML associated with a purchase order.

        :param purchase_order_number: The contract's unique ID on \
        DocumentCloud.
        :type purchase_order_number: string
        :returns: ???
        '''

        output = Utilities().check_if_valid_purchase_order_format(
            purchase_order_number)
        if output is False:
            return

        path_check = os.path.exists(
            PURCHASE_ORDER_LOCATION + '/' + purchase_order_number)
        if not path_check:
            url = (
                'http://www.purchasing.cityofno.com/bso/external/' +
                'purchaseorder/poSummary.sdo?docId=' + purchase_order_number +
                '&releaseNbr=0&parentUrl=contract')
            # log.info(
            #     '{} | {} | Attempting to download url | {}'.format(
            #         run_id, get_timestamp(), url
            #     )
            # )
            response = urllib2.urlopen(url)
            html = response.read()

            filepath = PURCHASE_ORDER_LOCATION + '/' + purchase_order_number
            with open(filepath, 'w') as filename:
                filename.write(html)
                # log.info(
                #     '{} | {} | Downloaded purchase order | {}'.format(
                #         run_id, get_timestamp(), purchase_order_number
                #     )
                # )

    @staticmethod
    def download_vendor_profile(vendor_id_city):
        '''
        Download the vendor page associated with a purchase order, if we don't
        have the vendor page already.

        :param vendor_id_city: ???.
        :type vendor_id_city: ???
        '''

        vendor_file_location = VENDORS_LOCATION + '/' + vendor_id_city
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
        # else:
            # log.info(
            #     '{} | {} | Skipped vendor file. Already present | {}'.format(
            #         run_id, get_timestamp(), vendor_id_city
            #     )
            # )

    @staticmethod
    def get_attachments(soup):
        '''
        Find the attachments to download from the HTML.

        :param soup: A BeautifulSoup object for the contract page's HTML.
        :type soup: BeautifulSoup object
        :returns: ???
        '''

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
        except Exception, error:
            log.exception(error, exc_info=True)
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
        except Exception, error:
            log.exception(error, exc_info=True)
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

    # @staticmethod
    # def download_attachment_file(bid_no, bid_file_location):
    #     '''
    #     Download the attachment file found on contract page.

    #     :param bid_no: ???
    #     :type bid_no: ???
    #     :param bid_file_location: ???
    #     :type bid_file_location: ???
    #     :returns: ???
    #     '''

    #     if not os.path.exists(bid_no):
    #         process = subprocess.Popen([
    #             'curl',
    #             '-o',
    #             bid_file_location,
    #             'http://www.purchasing.cityofno.com/bso/external/document/' +
    #             'attachments/attachmentFileDetail.sdo',
    #             '-H',
    #             'Pragma: no-cache',
    #             '-H',
    #             'Origin: null',
    #             '-H',
    #             'Accept-Encoding: gzip,deflate,sdch',
    #             '-H',
    #             'Accept-Language: en-US,en;q=0.8',
    #             '-H',
    #             'Content-Type: multipart/form-data; ' +
    #             'boundary=----WebKitFormBoundaryP4a4C1okQYkBGBSG',
    #             '-H',
    #             'Accept: text/html,application/xhtml+xml,' +
    #             'application/xml;q=0.9,image/webp,*/*;q=0.8',
    #             '-H',
    #             'Connection: keep-alive',
    #             '--data-binary',
    #             '''------WebKitFormBoundaryP4a4C1okQYkBGBSG\r
    # Content-Disposition: form-data; name="mode"\r
    # \r
    # download\r
    # ------WebKitFormBoundaryP4a4C1okQYkBGBSG\r
    # Content-Disposition: form-data; name="parentUrl"\r
    # \r
    # /external/purchaseorder/poSummary.sdo\r
    # ------WebKitFormBoundaryP4a4C1okQYkBGBSG\r
    # Content-Disposition: form-data; name="parentId"\r
    # \r
    # \r
    # ------WebKitFormBoundaryP4a4C1okQYkBGBSG\r
    # Content-Disposition: form-data; name="fileNbr"\r
    # \r
    # ''' + bid_no + '''\r
    # ------WebKitFormBoundaryP4a4C1okQYkBGBSG\r
    # Content-Disposition: form-data; name="workingDir"\r
    # \r
    # \r
    # ------WebKitFormBoundaryP4a4C1okQYkBGBSG\r
    # Content-Disposition: form-data; name="docId"\r
    # \r
    # 4051927411\r
    # ------WebKitFormBoundaryP4a4C1okQYkBGBSG\r
    # Content-Disposition: form-data; name="docType"\r
    # \r
    # P\r
    # ------WebKitFormBoundaryP4a4C1okQYkBGBSG\r
    # Content-Disposition: form-data; name="docSubType"\r
    # \r
    # \r
    # ------WebKitFormBoundaryP4a4C1okQYkBGBSG\r
    # Content-Disposition: form-data; name="releaseNbr"\r
    # \r
    # 0\r
    # ------WebKitFormBoundaryP4a4C1okQYkBGBSG\r
    # Content-Disposition: form-data; name="downloadFileNbr"\r
    # \r
    # ''' + bid_no + '''\r
    # ------WebKitFormBoundaryP4a4C1okQYkBGBSG\r
    # Content-Disposition: form-data; name="itemNbr"\r
    # \r
    # 0\r
    # ------WebKitFormBoundaryP4a4C1okQYkBGBSG\r
    # Content-Disposition: form-data; name="currentPage"\r
    # \r
    # 1\r
    # ------WebKitFormBoundaryP4a4C1okQYkBGBSG\r
    # Content-Disposition: form-data; name="querySql"\r
    # \r
    # \r
    # ------WebKitFormBoundaryP4a4C1okQYkBGBSG\r
    # Content-Disposition: form-data; name="sortBy"\r
    # \r
    # \r
    # ------WebKitFormBoundaryP4a4C1okQYkBGBSG\r
    # Content-Disposition: form-data; name="sortByIndex"\r
    # \r
    # 0\r
    # ------WebKitFormBoundaryP4a4C1okQYkBGBSG\r
    # Content-Disposition: form-data; name="sortByDescending"\r
    # \r
    # false\r
    # ------WebKitFormBoundaryP4a4C1okQYkBGBSG\r
    # Content-Disposition: form-data; name="revisionNbr"\r
    # \r
    # 0\r
    # ------WebKitFormBoundaryP4a4C1okQYkBGBSG\r
    # Content-Disposition: form-data; name="receiptId"\r
    # \r
    # \r
    # ------WebKitFormBoundaryP4a4C1okQYkBGBSG\r
    # Content-Disposition: form-data; name="vendorNbr"\r
    # \r
    # \r
    # ------WebKitFormBoundaryP4a4C1okQYkBGBSG\r
    # Content-Disposition: form-data; name="vendorGrp"\r
    # \r
    # \r
    # ------WebKitFormBoundaryP4a4C1okQYkBGBSG\r
    # Content-Disposition: form-data; name="invoiceNbr"\r
    # \r
    # \r
    # ------WebKitFormBoundaryP4a4C1okQYkBGBSG\r
    # Content-Disposition: form-data; name="displayName"\r
    # \r
    # Grainger Inc. Februaryl 2008.pdf\r
    # ------WebKitFormBoundaryP4a4C1okQYkBGBSG--\r
    # ''',
    #             '--compressed'
    #         ])
    #         process.wait()
