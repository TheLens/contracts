# -*- coding: utf-8 -*-

# todo: everything

'''Tests that all Python files in project pass pylint tests without errors.'''

from unittest import TestCase
import os
import fnmatch
from subprocess import call
from contracts import PROJECT_DIR

# ignore stuff in virtualenvs or version control directories
patterns = ('logs', 'backup', 'pythondocumentcloud', 'misc')


def ignore(directory):
    '''Check if this directory should be ignored.'''

    for pattern in patterns:
        if pattern in directory:
            return True
    return False


class TestPylint(TestCase):

    '''Test that all Python files pass pylint tests.'''

    @staticmethod
    def test_pep8():
        '''Test that all Python files pass pylint tests.'''

        # pep8style = pep8.StyleGuide(quiet=False)

        # Find all .py files
        files_list = []
        for root, dirnames, filenames in os.walk(PROJECT_DIR):
            if ignore(root):
                continue

            for filename in fnmatch.filter(filenames, '*.py'):
                files_list.append(os.path.join(root, filename))

        for filename in files_list:
            call([
                'pylint',
                '--errors-only',
                # '--ignore=check_assessor_urls.py',  # todo: not working
                # --disable=invalid-name,
                filename
            ])
