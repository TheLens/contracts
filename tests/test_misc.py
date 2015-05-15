
'''docstring'''

from unittest import TestCase
from contracts.lib.models import QueryBuilder
import unittest


class TestMisc(TestCase):

    '''docstring'''

    def test_name_parsing(self):
        '''docstring'''

        query_builder = QueryBuilder()
        query_builder.add_term(
            "projectid", "1542-city-of-new-orleans-contracts")
        query_builder.add_term("vendor", "ALAN BRICKMAN")
        query = query_builder.get_query()
        self.assertEqual(
            'projectid:"1542-city-of-new-orleans-contracts" ' +
            'vendor:"ALAN BRICKMAN"',
            query
        )

    def test_name_parsing_with_term(self):
        '''docstring'''

        query_builder = QueryBuilder()
        query_builder.add_term(
            "projectid", "1542-city-of-new-orleans-contracts")
        query_builder.add_term("vendor", "ALAN BRICKMAN")
        query_builder.add_text("New")
        query = query_builder.get_query()
        self.assertEqual(
            'projectid:"1542-city-of-new-orleans-contracts" ' +
            'vendor:"ALAN BRICKMAN" New',
            query
        )

if __name__ == '__main__':
    unittest.main()
