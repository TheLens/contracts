
'''
Utility functions for use by multiple classes.
'''

import re
import csv
from contracts import PROJECT_DIR


class Utilities(object):
    '''Methods used by multiple classes.'''

    @staticmethod
    def get_skip_list():
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
        # TODO: os.path
        skip_list_location = '{}/data/skip-list.csv'.format(PROJECT_DIR)

        with open(skip_list_location, "r") as fname:
            reader = csv.reader(fname)
            next(reader, None)  # Skip header row
            skip_list = list(row[0] for row in reader)

            return skip_list

    @staticmethod
    def check_if_valid_purchase_order_format(purchase_order_number):
        '''
        Determine if this is a valid purchase order format, using regular
        expressions. It does not check whether the purchase order exists.

        This is necessary because the city occassionally posts permits or
        memoranda of understanding to the purchasing site, so this will filter
        those out.

        :param purchase_order_number: The purchase order number to check.
        :type purchase_order_number: string.
        :returns: boolean. True if a valid format, False if invalid format.
        '''

        # TODO: Remove this? Why is this necessary?
        # It caused scraper to miss "JOB123123".
        # If only downside is adding too much, while upside is getting
        # everything, then we should remove this filter.
        purchase_order_regex = r'[A-Z]{2}\d{3,}'
        # TODO: Other file had r'[A-Z]{2}\d+'. Determine which is correct.
        purchase_order_pattern = re.compile(purchase_order_regex)

        if purchase_order_pattern.match(purchase_order_number):
            return True
        else:
            # Not a valid format
            # log.warning(
            #  '{} | {} | Invalid purchase order | {}'.format(
            #      run_id, get_timestamp(), purchase_order_number)
            # )
            return False

    def check_if_not_in_skip_list(self, purchase_order_number):
        '''

        :returns: boolean. True if not in skip list, False if in skip list.
        '''

        skip_list = self.get_skip_list()

        if purchase_order_number in skip_list:
            log.info('Purchase order {} is in skip list'.format(
                purchase_order_number))

            return False
        else:
            return True

    def check_that_contract_is_valid_and_public(self, purchase_order_number):
        '''
        Runs checks against purchase order number before adding it to our
        DocumentCloud project. If any of the checks fail, this will return
        False.

        :param purchase_order_number: The contract's purchase order number.
        :type purchase_order_number: string.
        :returns: boolean. True if valid and okay to add, False if not.
        '''

        checks = [
            self.check_if_valid_purchase_order_format(purchase_order_number),
            self.check_if_not_in_skip_list(purchase_order_number),
        ]

        return any(checks)

        # if any(checks) is False:
        #     return False
        # else:
        #     return True
