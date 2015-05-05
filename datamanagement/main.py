#!/usr/bin/python
"""
This script runs the daily downloader
"""
import logging
import argparse

from contracts.settings import Settings
from contracts.datamanagement.lensDocCloudSynch import matchLensDBtoDocumentCloud
from contracts.datamanagement.lib.models import check_page

parser = argparse.ArgumentParser(description='Scrape a page from the contract index, adding contracts')
parser.add_argument('pages', metavar='N', type=int, nargs='+')
parser.set_defaults(pages=[1])
args = parser.parse_args()
pages = args.pages

SETTINGS = Settings()
logging.basicConfig(level=logging.DEBUG, filename=SETTINGS.log)

matchLensDBtoDocumentCloud()

for page in pages:
    check_page(page)
