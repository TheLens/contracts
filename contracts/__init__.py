'''
Holds the settings so that they are accessible to other classes.
All private information is stored in environment variables and should never
be written into files in this repo.
'''

from constants import *  # TODO: Fix by updating all files to use constants.* imports

from logger import logger as log

# Initialize new session
log.info("***** New session *****")

log.info("Attachments output directory: %s", ATTACHMENTS_DIR)
log.info("Documents output directory: %s", DOCUMENTS_DIR)
log.info("DocumentCloud output directory: %s", DOCUMENT_CLOUD_DIR)
log.info("Purchase orders output directory: %s", PURCHASE_ORDER_DIR)
log.info("Vendors output directory: %s", VENDORS_DIR)
