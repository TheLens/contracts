from os.path import dirname, join
from unittest import TestCase

class TestParser(TestCase):

    def test_name_parsing(self):
        self.assertEqual('Smith', 'Smith')