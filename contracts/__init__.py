'''
Holds the settings so that they are accessible to other classes.
All private information is stored in environment variables and should never
be written into files in this repo.
'''

from constants import *  # TODO: Fix by updating all files to use constants.* imports

from logger import (
    # logger as log,
    app_logger as app_log,
    scrape_logger as scrape_log)

# Initialize new sessions
for l in [app_log, scrape_log]:
    l.info("***** New session *****")
    l.info("Attachments output directory: %s", ATTACHMENTS_DIR)
    l.info("Documents output directory: %s", DOCUMENTS_DIR)
    l.info("DocumentCloud output directory: %s", DOCUMENT_CLOUD_DIR)
    l.info("Purchase orders output directory: %s", PURCHASE_ORDER_DIR)
    l.info("Vendors output directory: %s", VENDORS_DIR)
