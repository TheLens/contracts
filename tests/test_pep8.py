# -*- coding: utf-8 -*-

'''Tests that all Python files in project meet PEP8 coding style standards.'''

from unittest import TestCase
import pep8
import os
import fnmatch
from contracts import PROJECT_DIR

# ignore stuff in virtualenvs or version control directories
patterns = ('logs')


def ignore(directory):
    '''Check if this directory should be ignored.'''

    for pattern in patterns:
        if pattern in directory:
            return True
    return False


class TestPep8(TestCase):

    '''Test that all Python files conform to PEP8 standards.'''

    def test_pep8(self):
        '''Test that all Python files conform to PEP8 standards.'''

        pep8style = pep8.StyleGuide(quiet=False)

        # Find all .py files
        files_list = []
        for root, dirnames, filenames in os.walk(PROJECT_DIR):
            # print root
            # print dirnames
            # print filenames
            # if ignore(root):
            #     continue

            for filename in fnmatch.filter(filenames, '*.py'):
                # print filename
                files_list.append(os.path.join(root, filename))

        errors = pep8style.check_files(files_list).total_errors

        self.assertEqual(
            errors, 0, 'Found %s PEP8 errors (and warnings).' % errors)
