#!/usr/bin/python
"""
This script runs the daily downloader
"""

from contracts.datamanagement.lib.models import DailyScraper

ds = DailyScraper()

ds.run()