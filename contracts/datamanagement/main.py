#!/usr/bin/python

"""
This script runs the daily downloader.
"""

from contracts.datamanagement.lens_doc_cloud_sync import (
    matchLensDBtoDocumentCloud
)
from contracts.datamanagement.lib.models import check_page

pages = range(1, 11)  # A list for pages 1-10

matchLensDBtoDocumentCloud()

for page in pages:
    check_page(page)
