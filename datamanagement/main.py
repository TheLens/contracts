#!/usr/bin/python
"""
This script runs the daily downloader
"""
import logging
from contracts.settings import Settings

SETTINGS = Settings()
logging.basicConfig(level=logging.DEBUG, filename=SETTINGS.log)

try:
    from contracts.datamanagement.lib.models import DailyScraper
    daily_scraper = DailyScraper()
    daily_scraper.run()
except Exception, error:
    print str(error)
 