#!/usr/bin/python
"""
This script runs the daily downloader
"""
import logging
from contracts.settings import Settings

SETTINGS = Settings()
logging.basicConfig(level=logging.DEBUG, filename=settings.log)

try:
    from contracts.datamanagement.lib.models import DailyScraper
    ds = DailyScraper()
    ds.run()
except Exception, e:
    print str(e)
 