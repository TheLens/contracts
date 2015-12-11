# -*- coding: utf-8 -*-

'''Represents a purchase order object.'''

import os
import re
import urllib2
from subprocess import call
from bs4 import BeautifulSoup

from contracts import (
    ATTACHMENTS_DIR,
    DOCUMENTS_DIR,
    PURCHASE_ORDER_DIR,
    VENDORS_DIR,
    log
)

# Emoji
red_no_emoji = "\xF0\x9F\x9A\xAB"
green_check_emoji = "\xE2\x9C\x85"


class PurchaseOrder(object):
    '''
    A purchase order number is assigned when the order is authorized to
    purchase a service or good. The numbers gets associated with a city
    contract. This number is used to track a contract in the city's
    purchasing system.

    All contracts have purchase orders, but not all purchase orders are for
    contracts.
    '''

    def __init__(self, purchase_order_number):
        self.purchase_order_number = purchase_order_number

        html = self._get_html(purchase_order_number)
        self.vendor_id_city = self._get_city_vendor_id(html)
        self._download_vendor_profile(self.vendor_id_city)

        soup = BeautifulSoup(html)
        self.description = self._get_description(soup)

        try:
            self.vendor_name = self._get_vendor_name()
        except IOError, error:
            log.exception(error, exc_info=True)

            self.vendor_name = "unknown"

            print (
                '%s  ' % (red_no_emoji) +
                'No vendor info for purchase order %s.' % (
                    purchase_order_number))
            log.info(
                'No vendor info for purchase order %s.',
                self.purchase_order_number)

        self.department = self._get_department(soup)
        self.k_number = self._get_knumber(soup)
        self.purchaseorder = self.purchase_order_number
        self.attachments = self._get_attachments(soup)
        self.data = self._get_data()
        self.title = "%s : %s" % (self.vendor_name, self.description)

    def __str__(self):
        return "<PurchaseOrder %s>" % self.purchaseorder

    @staticmethod
    def _get_html(purchase_order_number):
        '''
        Reads the HTML contents of this purchase order file.

        :param purchase_order_number: The contract's unique ID on \
                                      DocumentCloud.
        :type purchase_order_number: string
        :returns: string. The HTML contains for this purchase order file.
        '''

        file_location = (
            '%s/%s.html' % (PURCHASE_ORDER_DIR, purchase_order_number)
        )

        # Purchase order HTML saved in PurchaseOrder class
        with open(file_location, 'r') as html_file:
            log.info(
                'Saving HTML for purchase order %s.',
                purchase_order_number)
            html = html_file.read()
            return html

    @staticmethod
    def _get_city_vendor_id(html):
        '''
        Parses the contract page's HTML to find the vendor ID.

        :param html: The contract page's HTML.
        :type html: string
        :returns: string. The vendor ID, or an empty string if none is found.
        '''

        pattern = r"(?<=ExternalVendorProfile\(')\d+"
        vendor_ids = re.findall(pattern, html)

        if len(vendor_ids) == 0:
            log.error('No vendor ID found.')
            vendor_id = ""
        else:
            # You need to take the first one for this list or you'll sometimes
            # end up w/ the vendor_id for a subcontractor, which will sometimes
            # end up on the vendor page.
            # http://www.purchasing.cityofno.com/bso/external/purchaseorder/
            # poSummary.sdo?docId=FC154683&releaseNbr=0&parentUrl=contract
            vendor_id = vendor_ids[0]
            log.debug('Vendor ID: %s.', vendor_id)

        return vendor_id

    @staticmethod
    def _download_vendor_profile(city_vendor_id):
        '''
        Download the vendor page associated with a purchase order, if we don't
        have the vendor page already.

        :param city_vendor_id: The vendor ID on the city's purchasing site.
        :type city_vendor_id: string.
        '''

        vendor_file_location = '%s/%s.html' % (
            VENDORS_DIR, city_vendor_id)

        if os.path.isfile(vendor_file_location):
            log.info('Already have HTML for vendor %s.', city_vendor_id)
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

                log.info('Saved HTML for vendor %s.', city_vendor_id)
            except urllib2.HTTPError:
                log.info(
                    'Could not save HTML for vendor "%s".', city_vendor_id)

    @staticmethod
    def _get_description(soup):
        '''
        Find the description in the HTML.

        :param soup: A BeautifulSoup object for the contract page HTML.
        :type soup: BeautifulSoup object.
        :returns: string. The contract description on the city purchasing site.
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

    def _get_vendor_name(self):  # , soup):
        '''
        Find the vendor name in the contract HTML. If that fails, then ___

        :param soup: A BeautifulSoup object for the contract page HTML.
        :type soup: BeautifulSoup object.
        :returns: string. The contract vendor's name.
        '''

        vendor_file_location = (
            '%s/%s.html' % (VENDORS_DIR, self.vendor_id_city)
        )

        # Downloaded this file in _download_vendor_profile()
        with open(vendor_file_location, 'r') as myfile:
            html = myfile.read()

        soup = BeautifulSoup(html)

        vendor_row = soup(text='Company Name:')[0].parent.parent

        vendor_name = vendor_row.findChildren(
            ['td']
        )[5].contents.pop().strip()  # pop() pulls out from list

        # Convert to uppercase for DocumentCloud project metadata.
        # Search queries are also converted to uppercase.
        vendor_name = vendor_name.upper()

        return vendor_name

    @staticmethod
    def _get_department(soup):
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
    def _get_knumber(soup):
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
    def _get_purchase_order(soup):
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
    def _get_attachments(soup):
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
        except IndexError:
            # log.exception(error, exc_info=True)
            print '%s  No attachments found.' % (red_no_emoji)
            log.info('No attachments found.')

            return []  # The city does not always include attachment files.

    def _get_data(self):
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

        if self.attachments == []:
            return

        for attachment in self.attachments:
            self._download_attachment(attachment)

    def _download_attachment(self, attachment):
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
        log.debug('Gathering data for attachment %s.', city_attachment_id)

        document_path = '%s/%s.pdf' % (
            DOCUMENTS_DIR, city_attachment_id)

        display_name = self._get_attachment_display_name(city_attachment_id)

        if os.path.isfile(document_path):  # Have already downloaded
            print (
                '%s  ' % (red_no_emoji) +
                'Already have PDF for attachment %s.' % city_attachment_id)
            log.info(
                '%s  ' % (red_no_emoji) +
                'Already have PDF for attachment %s.',
                city_attachment_id)
        else:
            self._download_attachment_file(
                city_attachment_id,
                display_name,
                document_path
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

        file_location = (
            '%s/%s.html' % (ATTACHMENTS_DIR, city_attachment_id))

        with open(file_location, 'w') as filename:
            log.info('Saving HTML for attachment %s.', city_attachment_id)
            filename.write(html)

        soup = BeautifulSoup(html)
        header = soup.select(".sectionheader-01")[0].contents.pop()
        header = ' '.join(header.split())

        attachment_file_name = str(header).replace(
            "Attachment File Detail:", "").strip()

        return attachment_file_name

    def _download_attachment_file(self,
                                  attachment_id,
                                  display_name,
                                  document_file_path):
        '''
        Download the attachment file found on contract page.

        TODO: This URL is excessive.

        :param attachment_id: The city's internal attachment ID.
        :type attachment_id: string
        :param document_file_path: The path for where to save the \
                                         attachment file.
        :type document_file_path: string
        '''

        print (
            '%s  ' % (green_check_emoji) +
            'Saving PDF for attachment "%s" with city ID %s...' % (
                display_name, attachment_id))
        log.debug(
            'Saving PDF for attachment "%s" with city ID %s.',
            display_name,
            attachment_id)

        if not os.path.exists(attachment_id):
            call([
                'curl',
                '-o',
                document_file_path,
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
