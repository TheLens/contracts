
'''Utility functions for use by multiple classes.'''

import csv
from contracts import PROJECT_DIR


class Utilities(object):

    '''Methods used by multiple classes.'''

    def check_that_contract_is_public(self, purchase_order_number):
        '''
        Runs checks against purchase order number before adding it to our
        DocumentCloud project. If any of the checks fail, this will return
        False.

        :param purchase_order_number: The contract's purchase order number.
        :type purchase_order_number: string.
        :returns: boolean. True if valid and okay to add, False if not.
        '''

        in_skip_list = self._check_if_in_skip_list(purchase_order_number)

        if in_skip_list:  # Not public
            return False

        return True

    def _check_if_in_skip_list(self, purchase_order_number):
        '''Returns True if in skip list, False if not in skip list.'''

        skip_list = self._get_skip_list()

        if purchase_order_number in skip_list:
            return True

        return False

    @staticmethod
    def _get_skip_list():
        '''
        Some contracts are not posted on the city's site even though they are
        included in the city's contract inventory. We put these contracts on a
        skip list so we can compare purchase order numbers to make sure they
        are ignored and not published.

        Skipped contracts include things that are sensitive in nature, such as
        security plans for the airport.

        :returns: list. A list of the purchase order numbers of contracts to \
        skip.
        '''

        skip_list_location = PROJECT_DIR + '/data/skip-list.csv'

        with open(skip_list_location, "r") as csv_file:
            reader = csv.reader(csv_file)
            next(reader, None)  # Skip header row
            skip_list = list(row[0] for row in reader)

            return skip_list
