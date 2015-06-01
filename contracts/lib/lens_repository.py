
"""
Keeping local contracts collection in sync with DocumentCloud project.
"""

import os
import re
import csv
import urllib2
from contracts import (
    PROJECT_DIR,
    PURCHASE_ORDER_LOCATION
)


class LensRepository(object):
    """
    Methods for keeping local contracts archive in sync with DocumentCloud
    project.
    """

    def __init__(self):
        # Check for contracts to skip. Ex. airport contracts.
        # They are not posted on the city's public purchasing site,
        # but are included in the city's contract logs:
        self.skiplist = self.get_skip_list()
        self.purchase_orders_location = PURCHASE_ORDER_LOCATION

    @staticmethod
    def check_if_valid_purchase_order_number(purchase_order_no):
        """
        A method to determine if this is a valid purchase order using regular
        expressions.
        """

        purchase_order_regex = r'[A-Z]{2}\d{3,}'
        purchase_order_pattern = re.compile(purchase_order_regex)
        if purchase_order_pattern.match(purchase_order_no):
            return True
        else:
            return False

    def download_purchaseorder(self, purchase_order_no):
        '''
        Download (the contract matching this purchase order number?).

        :param purchase_order_no: The contract's unique ID for DocumentCloud.
        :type purchase_order_no: string.
        :returns: ???
        '''

        if purchase_order_no in self.skiplist:
            '''skip non-public contracts'''

            # log.warning(
            #     '{} | {} | Contract is in the skiplist | {}'.format(
            #         run_id, get_timestamp(), purchase_order_no)
            # )
            return

        output = self.check_if_valid_purchase_order_number(
            purchase_order_no)
        if not output:
            '''
            Checks regex to make sure that this is a feasible purchase order.
            '''
            # log.warning(
            #     '{} | {} | Invalid purchase order | {}'.format(
            #         run_id, get_timestamp(), purchase_order_no)
            # )
            return

        file_loc = self.purchase_orders_location + '/' + purchase_order_no
        if not os.path.isfile(file_loc):
            response = urllib2.urlopen(
                'http://www.purchasing.cityofno.com/bso/external/' +
                'purchaseorder/poSummary.sdo?docId=' + purchase_order_no +
                '&releaseNbr=0&parentUrl=contract')
            html = response.read()
            self.write_purchase_order(html, file_loc)

    @staticmethod
    def write_purchase_order(html, file_location):
        '''
        docstring

        :param html: The contract's unique ID for DocumentCloud.
        :type html: string.
        :param file_location: The contract's unique ID for DocumentCloud.
        :type file_location: string.
        :returns: ???
        '''

        with open(file_location, 'w') as f:
            '''
            Save the HTML for an individual purchase order page.
            '''

            # log.warning(
            #     '{} | {} | Writing purchase_order_no to file | {}'.format(
            #         run_id, get_timestamp(), file_location)
            # )
            f.write(html)  # python will convert \n to os.linesep

    def check_if_public_and_need_to_download(self, purchase_order_no):
        '''
        docstring

        :param purchase_order_no: The contract's unique ID for DocumentCloud.
        :type purchase_order_no: string.
        :returns: ???
        '''

        if purchase_order_no in self.skiplist:
            '''
            If this contract is not posted publicly, then skip it.
            The skip list stores the private contracts that we know about but
            are not posted online by the city.
            '''

            # log.warning(
            #     '{} | {} | Contract is in the skiplist | {}'.format(
            #         run_id, get_timestamp(), purchase_order_no
            #     )
            # )
            return

        file_loc = self.purchase_orders_location + purchase_order_no

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

        skip_list_location = PROJECT_DIR + '/data/skip-list.csv'

        with open(skip_list_location, "r") as fname:
            reader = csv.reader(fname)
            next(reader, None)  # Skip header row
            skip_list = list(row[0] for row in reader)

            return skip_list
