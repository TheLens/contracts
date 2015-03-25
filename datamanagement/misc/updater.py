import re
import logging
import sys
import uuid
import datetime
import urllib2
from time import sleep
from random import randint
from contracts.datamanagement.lib.models import PurchaseOrder, DocumentCloudProject, SummaryProcessor
from contracts.settings import Settings
from contracts.lib.models import Utilities

run_id = " " + str(uuid.uuid1())  #this is a uuid that is unique to a given run of the program. Grep for it in the log file to see a certain run 

utils = Utilities()

po_queue = sys.argv[1]

queue = [l.replace("\n", "").strip() for l in open(po_queue)]

queue = queue[1:] 

logging.info('{} | {} |About to process PO queue | {}'.format(run_id, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), sys.argv[1]))

skiplist = [l.replace("\n", "").strip() for l in open("skiplist.txt")] 

project = DocumentCloudProject()
sp = SummaryProcessor()
settings = Settings()


LEVELS = { 'debug':logging.DEBUG,
            'info':logging.INFO,
            'warning':logging.WARNING,
            'error':logging.ERROR,
            'critical':logging.CRITICAL
            }


if len(sys.argv) > 1:
    level_name = sys.argv[1]
    level = LEVELS.get(level_name, logging.NOTSET)
    logging.basicConfig(level=level, filename=settings.log)
else:
    logging.basicConfig(level=logging.DEBUG, filename=settings.log)


for q in queue:
    logging.info('{} | {} | Processing | {}'.format(run_id, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), q))
    if not q in skiplist and not q=="unknown" and utils.valid_po(q):
        try:
            po = PurchaseOrder(q, False)
            if not project.has_contract("purchase order", q):
                logging.info('{} | {} | Getting | {}'.format(run_id, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), q))
                project.add_contract(q)
            contract = project.get_contract("purchase order", q)
            project.update_metadata(contract.id, 'vendor_id', po.vendor_id_city)
        except urllib2.HTTPError:
            logging.info('{} | {} | Add to skiplist. Error. | {}'.format(run_id, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), q))