
'''Test cases for contracts.lib.models.'''

from unittest import TestCase
from contracts.models import Models


class TestAppModels(TestCase):

    def test_translate_query_vendor(self):
        output = Models().translate_to_vendor('ALDEN J MCDONALD')
        print output
        self.assertEquals(output.strip(), 'Liberty Bank')

    def test_translate_web_query_to_dc_query(self):
        data = {
            'search_input': '',
            'department': '',
            'vendor': '',
            'officer': 'ALDEN J MCDONALD',
            'current_page': ''
        }
        output = Models().translate_web_query_to_dc_query(data)
        print output
        self.assertEquals(
            output.strip(),
            'projectid:"1542-city-of-new-orleans-contracts" ' +
            'vendor:"Liberty Bank "')
