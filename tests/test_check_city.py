
'''Test cases for contracts.lib.purchase_order.py.'''

from unittest import TestCase
from contracts.lib.check_city import CheckCity
from contracts import PROJECT_DIR


class TestPurchaseOrder(TestCase):

    def test_check_if_invalid(self):
        '''Checks'''

        html1 = "Test"
        html2 = "blahThere are no vendor distributors found " + \
            "for this master blanket/contractblah"

        output1 = CheckCity()._check_if_invalid(html1)
        output2 = CheckCity()._check_if_invalid(html2)

        self.assertFalse(output1)
        self.assertTrue(output2)

    def test_get_purchase_order_numbers_from_index_page(self):
        '''Checks'''

        with open('%s/tests/data/index.html' % PROJECT_DIR, 'r') as filename:
            html = filename.read()

        output = CheckCity()._get_purchase_order_numbers_from_index_page(html)

        expected_output = [
            'LW596485',
            'LW596484',
            'LW596483',
            'LW596482',
            'RD596320',
            'PW596311',
            'RD596000',
            'PM596028',
            'RD595958',
            'HL595865',
            'HL595817',
            'AV595827',
            'RD595744',
            'PW595790',
            'AV595738',
            'RD595611',
            'CI595601',
            'BC595608',
            'RD595596',
            'RD595595',
            'NS595584',
            'CI595599',
            'PW595434',
            'HL595407',
            'CI595383'
        ]

        self.assertEquals(output, expected_output)
