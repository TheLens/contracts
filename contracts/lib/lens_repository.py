# -*- coding: utf-8 -*-

'''
Keeping the local contracts collection in sync with our DocumentCloud project.
'''

import os
import urllib2
from contracts.lib.utilities import Utilities
from contracts import PURCHASE_ORDER_LOCATION, log


class LensRepository(object):

    '''
    Methods for keeping the local contracts archive in sync with our
    DocumentCloud project.
    '''

    @staticmethod
    def check_if_need_to_download(purchase_order_number):
        '''
        Checks local directory to determine whether a local copy is needed.

        :param purchase_order_number: The contract's purchase order number.
        :type purchase_order_number: string.
        :returns: boolean. True if need to download, False if don't need to.
        '''

        # Check if contract has valid format and is public
        validity = Utilities().check_that_contract_is_valid_and_public(
            purchase_order_number)

        file_location = (
            '%s/%s' % (PURCHASE_ORDER_LOCATION, purchase_order_number))
        local_copy_exists = os.path.isfile(file_location)

        if validity is False or local_copy_exists:
            log.debug("Don't need to download %s", purchase_order_number)
            print (
                "\xF0\x9F\x9A\xAB  " +  # Do not enter
                "Don't download. Contract is invalid, private or we " +
                "already have it.")
            return False  # Don't download
        else:
            log.debug('Need to download %s', purchase_order_number)
            return True

    def download_purchase_order(self, purchase_order_number):
        '''
        Download the contract matching this purchase order number, but first
        check if it is valid, not in the skip list and not already downloaded.

        :param purchase_order_number: The contract's unique ID for \
                                      DocumentCloud.
        :type purchase_order_number: string.
        '''

        log.debug('Downloading purchase order %s', purchase_order_number)
        print (
            '\xE2\x9C\x85  ' +
            'Downloading purchase order %s...' % purchase_order_number)

        file_location = (
            '%s/%s' % (PURCHASE_ORDER_LOCATION, purchase_order_number)
        )

        response = urllib2.urlopen(
            'http://www.purchasing.cityofno.com/bso/external/' +
            'purchaseorder/poSummary.sdo?docId=%s' % purchase_order_number +
            '&releaseNbr=0&parentUrl=contract')
        html = response.read()

        self._write_purchase_order(html, file_location)

    @staticmethod
    def _write_purchase_order(html, file_location):
        '''
        This takes an individual contract page's HTML and writes it out to an
        HTML file in the proper location.

        :param html: The individual contract page's HTML.
        :type html: string.
        :param file_location: The path to where the file should be created.
        :type file_location: string.
        '''

        with open(file_location, 'w') as filename:
            log.info('Saving file %s', file_location)
            filename.write(html)
