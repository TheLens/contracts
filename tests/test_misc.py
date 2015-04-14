from os.path import dirname, join
from unittest import TestCase
from contracts.lib.models import QueryBuilder
import unittest

class TestMisc(TestCase):

    def test_name_parsing(self):
        qb = QueryBuilder()
        qb.add_term("projectid", "1542-city-of-new-orleans-contracts")
        qb.add_term("vendor", "ALAN BRICKMAN")
        query = qb.get_query()
        self.assertEqual('projectid:"1542-city-of-new-orleans-contracts" vendor:"ALAN BRICKMAN"', query)


    def test_name_parsing_with_term(self):
        qb = QueryBuilder()
        qb.add_term("projectid", "1542-city-of-new-orleans-contracts")
        qb.add_term("vendor", "ALAN BRICKMAN")
        qb.add_text("New")
        query = qb.get_query()
        self.assertEqual('projectid:"1542-city-of-new-orleans-contracts" vendor:"ALAN BRICKMAN" New', query)

if __name__ == '__main__':
    unittest.main()