# -*- coding: utf-8 -*-

'''
Represents a purchase order object.
'''

import os
import re
import urllib2
from subprocess import call
from bs4 import BeautifulSoup
from contracts.lib.utilities import Utilities
from contracts import (
    VENDORS_LOCATION,
    PURCHASE_ORDER_LOCATION,
    ATTACHMENTS_LOCATION,
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

    def __str__(self):
        return "<PurchaseOrder {}>".format(self.purchaseorder)

    def __init__(self, purchase_order_number):
        log.debug(
            'Building PurchaseOrder object for %s', purchase_order_number)

        validity = Utilities().check_if_valid_purchase_order_format(
            purchase_order_number)
        if validity is False:
            print (
                '\xF0\x9F\x9A\xAB  ' +
                'Purchase order %s is invalid.' % purchase_order_number)
            log.debug(
                'Purchase order %s format is invalid', purchase_order_number)
            return

        self.purchase_order_number = purchase_order_number

        html = self.get_html(purchase_order_number)
        self.vendor_id_city = self.get_city_vendor_id(html)
        self.download_vendor_profile(self.vendor_id_city)

        soup = BeautifulSoup(html)
        self.description = self.get_description(soup)

        try:
            self.vendor_name = self.get_vendor_name(soup)
        except IOError, error:
            log.exception(error, exc_info=True)

            self.vendor_name = "unknown"
            print (
                '\xF0\x9F\x9A\xAB  ' +
                'No vendor info for purchase order %s.' % (
                    purchase_order_number))
            log.info(
                'No associated vendor info for %s', self.purchase_order_number)
            return

        self.department = self.get_department(soup)
        self.k_number = self.get_knumber(soup)
        self.purchaseorder = self.purchase_order_number
        self.attachments = self.get_attachments(soup)
        self.data = self.get_data()
        self.title = "%s : %s" % (self.vendor_name, self.description)

    @staticmethod
    def get_html(purchase_order_number):
        '''
        Reads the HTML contents of this purchase order file.

        :param purchase_order_number: The contract's unique ID on \
                                      DocumentCloud.
        :type purchase_order_number: string
        :returns: string. The HTML contains for this purchase order file.
        '''

        file_location = (
            '%s/%s' % (PURCHASE_ORDER_LOCATION, purchase_order_number)
        )

        with open(file_location, 'r') as html_file:
            html = html_file.read()
            return html

    @staticmethod
    def get_city_vendor_id(html):
        '''
        Parses the contract page's HTML to find the vendor ID.

        :param html: The contract page's HTML.
        :type html: string
        :returns: string. The vendor ID, or an empty string if none is found.
        '''

        pattern = r"(?<=ExternalVendorProfile\(')\d+"
        vendor_ids = re.findall(pattern, html)

        if len(vendor_ids) == 0:
            return ""
        else:
            # You need to take the first one for this list or you'll sometimes
            # end up w/ the vendor_id for a subcontractor, which will sometimes
            # wash up on the vendor page
            # view-source:http://www.purchasing.cityofno.
            # com/bso/external/purchaseorder/poSummary.
            # sdo?docId=FC154683&releaseNbr=0&parentUrl=contract
            return vendor_ids[0]

    @staticmethod
    def download_vendor_profile(city_vendor_id):
        '''
        Download the vendor page associated with a purchase order, if we don't
        have the vendor page already.

        :param city_vendor_id: The vendor ID on the city's purchasing site.
        :type city_vendor_id: string.
        '''

        vendor_file_location = '%s/%s' % (VENDORS_LOCATION, city_vendor_id)

        if os.path.isfile(vendor_file_location):
            log.info('Vendor file for %s already present', city_vendor_id)
        else:
            try:
                response = urllib2.urlopen(
                    'http://www.purchasing.cityofno.com/bso/external/vendor/' +
                    'vendorProfileOrgInfo.sdo?external=true&vendorId=' +
                    city_vendor_id
                )
                html = response.read()
                with open(vendor_file_location, 'w') as filename:
                    filename.write(html)

                log.info('Downloaded vendor file %s', city_vendor_id)
            except urllib2.HTTPError:
                log.info('Could not download vendor file %s', city_vendor_id)

    @staticmethod
    def get_description(soup):
        '''
        Find the description in the HTML.

        :param soup: A BeautifulSoup object for the contract page HTML.
        :type soup: BeautifulSoup object.
        :returns: string. The description ____.
        '''

        try:
            main_table = soup.select('.table-01').pop()
            metadata_row = main_table.findChildren(
                ['tr']
            )[2].findChildren(  # Why not [1]?
                ['td']
            )[0].findChildren(
                ['table']
            )[0].findChildren(
                ['tr']
            )

            description = metadata_row[1].findChildren(
                ['td']
            )[5].contents.pop().strip()  # pop() pulls out from list

            return str(description)
        except Exception, error:
            log.exception(error, exc_info=True)
            return ""

    def get_vendor_name(self, soup):
        '''
        Find the vendor name in the contract HTML. If that fails, then

        :param soup: A BeautifulSoup object for the contract page HTML.
        :type soup: BeautifulSoup object.
        :returns: string. The contract vendor's name.
        '''

        try:
            # regex_string = re.compile(r'Vendor:')
            vendor_row = soup(text='Vendor:')[0].parent.parent
            vendor_link_text = vendor_row.findChildren(
                ['td']
            )[1].findChildren(
                ['a']
            )[0].contents.pop().strip()  # pop() pulls out from list

            # Extract only the name, then remove periods.
            vendor = vendor_link_text.split('-')[1].strip().replace(".", "")

            # Convert to uppercase for DocumentCloud project metadata.
            # Search queries are also converted to uppercase
            # so we can find matches.
            vendor = vendor.upper()

            return str(vendor)
        except IndexError, error:
            # In cases of index error, go ahead and download the vendor page.
            log.exception(error, exc_info=True)

            vendor_file_location = (
                '%s/%s' % (VENDORS_LOCATION, self.vendor_id_city)  # + '.html'?
            )

            # Downloaded this file in download_vendor_profile()
            with open(vendor_file_location, 'r') as myfile:
                html = myfile.read()

            new_soup = BeautifulSoup(html)
            header = new_soup.select(".sectionheader-01")[0]
            vendor_name = str(header).replace("Vendor Profile - ", "").strip()

            # Convert to uppercase for DocumentCloud. Search queries are also
            # converted to uppercase so we can find matches.
            vendor_name = vendor_name.upper()

            return vendor_name

    @staticmethod
    def get_department(soup):
        '''
        Find the department in the contract page HTML. Ex. LW - LAW.

        :param soup: A BeautifulSoup object for the contract page HTML.
        :type soup: BeautifulSoup object.
        :returns: string. The contract's department.
        '''

        main_table = soup.select('.table-01').pop()

        metadata_row = main_table.findChildren(
            ['tr']
        )[2].findChildren(  # Why not [1]?
            ['td']
        )[0].findChildren(
            ['table']
        )[0].findChildren(['tr'])

        department = metadata_row[5].findChildren(
            ['td']
        )[1].contents.pop().strip()  # pop() pulls out from list

        # Convert to uppercase for DocumentCloud. Search queries are also
        # converted to uppercase so we can find matches.
        department = department.upper()

        return department

    @staticmethod
    def get_knumber(soup):
        '''
        Find the k number in the contract page HTML, under "Alternate ID."

        :param soup: A BeautifulSoup object for the contract page HTML.
        :type soup: BeautifulSoup object.
        :returns: string. The contract's K number.
        '''

        main_table = soup.select('.table-01').pop()

        metadata_row = main_table.findChildren(
            ['tr']
        )[2].findChildren(  # Why not [1]?
            ['td']
        )[0].findChildren(
            ['table']
        )[0].findChildren(
            ['tr']
        )

        try:
            knumber = metadata_row[6].findChildren(
                ['td']
            )[1].contents.pop()

            # Remove extra characters:
            knumber = knumber.replace('k', '').replace('K', '').replace(
                'm', '').replace('M', '').strip()
        except Exception, error:
            log.exception(error, exc_info=True)
            knumber = "unknown"

        if len(knumber) == 0:  # Empty string
            knumber = "unknown"

        return knumber

    @staticmethod
    def get_purchase_order(soup):
        '''
        Find the purchase order in the contract page HTML.

        :param soup: A BeautifulSoup object for the contract page HTML.
        :type soup: BeautifulSoup object.
        :returns: string. The contract's purchase order number.
        '''

        main_table = soup.select('.table-01').pop()

        purchase_order = main_table.findChildren(
            ['tr']
        )[2].findChildren(  # Why not [1]?
            ['td']
        )[0].findChildren(
            ['table']
        )[0].findChildren(
            ['tr']
        )[1].findChildren(
            ['td']
        )[1].contents.pop().strip()  # pop() pulls out from list

        return purchase_order

    @staticmethod
    def get_attachments(soup):
        '''
        Find the attachments to download from the contract page HTML.

        :param soup: A BeautifulSoup object for the contract page's HTML.
        :type soup: BeautifulSoup object
        :returns: ???
        '''

        try:
            main_table = soup.select('.table-01').pop()

            metadatarow = main_table.findChildren(
                ['tr']
            )[2].findChildren(  # Why not [1]?
                ['td']
            )[0].findChildren(
                ['table']
            )[0].findChildren(
                ['tr']
            )

            attachment_filenames_list = metadatarow[16].findChildren(
                ['td']
            )[1].findChildren(
                ['a']
            )

            return attachment_filenames_list
        except IndexError, error:
            log.exception(error, exc_info=True)
            return []  # Sometimes the city does not include attachment files.

    def get_data(self):
        '''
        Returns metadata dictionary fields, which were scraped and parsed from
        the contract page HTML.

        :returns: dict. The metadata for this contract, such as title, date \
                        added, description, attachments, purchase order number.
        '''

        output = {}
        output['vendor_id'] = self.vendor_id_city
        output['purchase order'] = self.purchaseorder
        output['contract number'] = self.k_number
        output['department'] = self.department
        output['vendor'] = self.vendor_name

        return output

    def download_attachments(self):
        '''
        Cycles through all the found attachments and calls on download method.
        '''

        for attachment in self.attachments:
            self.download_attachment(attachment)

    def download_attachment(self, attachment):
        '''
        Download an attachment associated with a purchase order.

        :param attachment: The name of the attachment file to download.
        :type attachment: string
        '''

        # The city's purchasing site has an internal ID for each attachment.
        # Here we use it to download the attachment files, and also to store
        # locally so we can have a list of the attachments we have on hand.
        city_attachment_id = re.search(
            '[0-9]+', attachment.get('href')).group()
        log.debug('Gathering data for attachment %s', city_attachment_id)

        attachment_id_path = '%s/%s.pdf' % (
            ATTACHMENTS_LOCATION, city_attachment_id)

        display_name = self._get_attachment_display_name(city_attachment_id)

        if os.path.isfile(attachment_id_path):  # Have already downloaded
            print (
                '\xF0\x9F\x9A\xAB  ' +
                'Already have attachment %s. Skipping.' % city_attachment_id)
            log.info(
                'Already have attachment ID %s for purchase order %s',
                city_attachment_id,
                self.purchaseorder)
        else:
            log.debug('Start downloading attachments')

            self.download_attachment_file(
                city_attachment_id,
                display_name,
                attachment_id_path
            )
            log.info(
                'Downloaded attachment ID %s for purchase order %s',
                city_attachment_id,
                self.purchaseorder
            )

    def _get_attachment_display_name(self, city_attachment_id):
        '''docstring'''

        response = urllib2.urlopen(
            'http://www.purchasing.cityofno.com/bso/external/document/' +
            'attachments/attachmentFileDetail.sdo?' +
            'fileNbr=%s' % city_attachment_id +
            '&docId=%s' % self.purchase_order_number +
            '&docType=P&releaseNbr=0&parentUrl=/external/purchaseorder/' +
            'poSummary.sdo&external=true'
        )
        html = response.read()

        soup = BeautifulSoup(html)
        header = soup.select(".sectionheader-01")[0].contents.pop()
        header = ' '.join(header.split())

        attachment_file_name = str(header).replace(
            "Attachment File Detail:", "").strip()

        return attachment_file_name

    def download_attachment_file(self,
                                 attachment_id,
                                 display_name,
                                 attachment_file_location):
        '''
        Download the attachment file found on contract page.

        :param attachment_id: The city's internal attachment ID.
        :type attachment_id: string
        :param attachment_file_location: The path for where to save the \
                                         attachment file.
        :type attachment_file_location: string
        '''

        print (
            '\xE2\x9C\x85  ' +
            'Downloading "%s" with city ID %s...' % (
                display_name, attachment_id))
        log.debug(
            'Downloading attachment %s with city ID %s',
            display_name,
            attachment_id
        )

        if not os.path.exists(attachment_id):
            call([
                'curl',
                '-o',
                attachment_file_location,
                'http://www.purchasing.cityofno.com/bso/external/document/' +
                'attachments/attachmentFileDetail.sdo',
                '-H',
                'Pragma: no-cache',
                '-H',
                'Origin: http://www.purchasing.cityofno.com',
                '-H',
                'Accept-Encoding: gzip, deflate',
                '-H',
                'Accept-Language: en-US,en;q=0.8',
                '-H',
                'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X ' +
                '10_10_3) AppleWebKit/537.36 (KHTML, like Gecko) ' +
                'Chrome/43.0.2357.81 Safari/537.36',
                '-H',
                'Content-Type: multipart/form-data; boundary=----' +
                'WebKitFormBoundaryGAY56ngXMDvs6qDP',
                '-H',
                'Accept: text/html,application/xhtml+xml,application/' +
                'xml;q=0.9,image/webp,*/*;q=0.8',
                '-H',
                'Cache-Control: no-cache',
                '-H',
                'Referer: http://www.purchasing.cityofno.com/bso/external/' +
                'document/attachments/attachmentFileDetail.sdo?fileNbr=' +
                '%s&docId=%s' % (attachment_id, self.purchase_order_number) +
                '&docType=P&releaseNbr=0&parentUrl=/external/purchaseorder/' +
                'poSummary.sdo&external=true',
                '-H',
                'Cookie: JSESSIONID=5FC84DA3EC020E1FC19700761C0EBEB3',
                '-H',
                'Connection: keep-alive',
                '--data-binary',
                '$\'------WebKitFormBoundaryGAY56ngXMDvs6qDP\r\nContent-' +
                'Disposition: form-data; name="mode"\r\n\r\ndownload\r\n' +
                '------WebKitFormBoundaryGAY56ngXMDvs6qDP\r\nContent-' +
                'Disposition: form-data; name="parentUrl"\r\n\r\n/external/' +
                'purchaseorder/poSummary.sdo\r\n------WebKitFormBoundary' +
                'GAY56ngXMDvs6qDP\r\nContent-Disposition: form-data; ' +
                'name="parentId"\r\n\r\n\r\n------' +
                'WebKitFormBoundaryGAY56ngXMDvs6qDP\r\nContent-Disposition: ' +
                'form-data; name="fileNbr"\r\n\r\n' +
                '%s' % attachment_id +
                '\r\n------WebKitFormBoundaryGAY56ngXMDvs6qDP\r\nContent-' +
                'Disposition: form-data; name="workingDir"\r\n\r\n\r\n------' +
                'WebKitFormBoundaryGAY56ngXMDvs6qDP\r\nContent-Disposition: ' +
                'form-data; name="docId"\r\n\r\n' +
                '%s' % self.purchase_order_number +
                '\r\n------WebKitFormBoundaryGAY56ngXMDvs6qDP\r\nContent-' +
                'Disposition: form-data; name="docType"\r\n\r\nP\r\n------' +
                'WebKitFormBoundaryGAY56ngXMDvs6qDP\r\nContent-Disposition: ' +
                'form-data; name="docSubType"\r\n\r\n\r\n------' +
                'WebKitFormBoundaryGAY56ngXMDvs6qDP\r\nContent-Disposition: ' +
                'form-data; name="releaseNbr"\r\n\r\n0\r\n------' +
                'WebKitFormBoundaryGAY56ngXMDvs6qDP\r\nContent-Disposition: ' +
                'form-data; name="downloadFileNbr"\r\n\r\n' +
                '%s' % attachment_id +
                '\r\n------WebKitFormBoundaryGAY56ngXMDvs6qDP\r\nContent-' +
                'Disposition: form-data; name="itemNbr"\r\n\r\n0\r\n------' +
                'WebKitFormBoundaryGAY56ngXMDvs6qDP\r\nContent-Disposition: ' +
                'form-data; name="currentPage"\r\n\r\n1\r\n------' +
                'WebKitFormBoundaryGAY56ngXMDvs6qDP\r\nContent-Disposition: ' +
                'form-data; name="querySql"\r\n\r\n\r\n------' +
                'WebKitFormBoundaryGAY56ngXMDvs6qDP\r\nContent-Disposition: ' +
                'form-data; name="sortBy"\r\n\r\n\r\n------' +
                'WebKitFormBoundaryGAY56ngXMDvs6qDP\r\nContent-Disposition: ' +
                'form-data; name="sortByIndex"\r\n\r\n0\r\n------' +
                'WebKitFormBoundaryGAY56ngXMDvs6qDP\r\nContent-Disposition: ' +
                'form-data; name="sortByDescending"\r\n\r\nfalse\r\n------' +
                'WebKitFormBoundaryGAY56ngXMDvs6qDP\r\nContent-Disposition: ' +
                'form-data; name="revisionNbr"\r\n\r\n0\r\n------' +
                'WebKitFormBoundaryGAY56ngXMDvs6qDP\r\nContent-Disposition: ' +
                'form-data; name="receiptId"\r\n\r\n\r\n------' +
                'WebKitFormBoundaryGAY56ngXMDvs6qDP\r\nContent-Disposition: ' +
                'form-data; name="vendorNbr"\r\n\r\n\r\n------' +
                'WebKitFormBoundaryGAY56ngXMDvs6qDP\r\nContent-Disposition: ' +
                'form-data; name="vendorGrp"\r\n\r\n\r\n------' +
                'WebKitFormBoundaryGAY56ngXMDvs6qDP\r\nContent-Disposition: ' +
                'form-data; name="invoiceNbr"\r\n\r\n\r\n------' +
                'WebKitFormBoundaryGAY56ngXMDvs6qDP\r\nContent-Disposition: ' +
                'form-data; name="displayName"\r\n\r\n' +
                '%s' % display_name +
                '\r\n------WebKitFormBoundaryGAY56ngXMDvs6qDP--\r\n\'',
                '--compressed'
            ])
