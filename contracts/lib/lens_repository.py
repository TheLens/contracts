# -*- coding: utf-8 -*-

'''
Keeping the local contracts collection in sync with our DocumentCloud project.
'''

import os
import urllib2
from contracts.lib.utilities import Utilities
from contracts import PURCHASE_ORDER_DIR, scrape_log as log


class LensRepository(object):

    '''
    Methods for keeping the local contracts archive in sync with our
    DocumentCloud project.
    '''

    def __init__(self, purchase_order_number):
        self.purchase_order_number = purchase_order_number

    def __str__(self):
        return '{0} -- {1.purchase_order_number!s}'.format(self.__class__.__name__, self)

    def __repr__(self):
        return '{0}({1.purchase_order_number!r})'.format(self.__class__.__name__, self)

    def check_if_need_to_download(self):
        '''
        Checks local directory to determine whether a local copy is needed.

        :returns: boolean. True if need to download, False if don't need to.
        '''

        # Check if contract has valid format and is public
        validity = Utilities().check_that_contract_is_valid_and_public(
            self.purchase_order_number)

        file_location = (
            '%s/%s.html' % (PURCHASE_ORDER_DIR, self.purchase_order_number))
        local_copy_exists = os.path.isfile(file_location)

        if validity is False or local_copy_exists:
            log.debug(
                "Don't download. Contract is invalid, private or we " +
                "already the HTML")
            return False  # Don't download
        else:
            return True

    def download_purchase_order(self):
        '''
        Download the contract matching this purchase order number, but first
        check if it is valid, not in the skip list and not already downloaded.
        '''
        file_location = '%s/%s.html' % (PURCHASE_ORDER_DIR, self.purchase_order_number)

        response = urllib2.urlopen(
            'http://www.purchasing.cityofno.com/bso/external/purchaseorder/' +
            'poSummary.sdo?docId=%s' % self.purchase_order_number +
            '&releaseNbr=0&parentUrl=contract')
        html = response.read()

        self._write_purchase_order(html, file_location)

    def _write_purchase_order(self, html, file_location):
        '''
        This takes an individual contract page's HTML and writes it out to an
        HTML file in the proper location.

        :param html: The individual contract page's HTML.
        :type html: string.
        :param file_location: The path to where the file should be created.
        :type file_location: string.
        '''

        if not os.path.exists(os.path.dirname(file_location)):
            os.makedirs(os.path.dirname(file_location))

        with open(file_location, 'w') as filename:
            log.info('Saving HTML for purchase order %s',
                     self.purchase_order_number)

            filename.write(html)
