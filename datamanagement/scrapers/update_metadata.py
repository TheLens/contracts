import os
import glob

from contracts.settings import Settings
from contracts.datamanagement.lib.models import PurchaseOrder
from contracts.datamanagement.lib.models import DocumentCloudProject

s = Settings()
project = DocumentCloudProject()

purchaseorders = glob.glob(s.corpus_loc + "/purchaseorders/*")

counter = 0
for p in purchaseorders:
    if counter % 100 == 0:
        print counter
    html = "".join([f for f in open(p)])
    try:
        po = PurchaseOrder(html)
        if project.has_contract("purchase order", po.purchaseorder):
                contract = project.get_contract("purchase order", po.purchaseorder)
                project.update_metadata(contract.id, "vendor_id", po.vendor_id_city)
    except IndexError:
        print p
    counter += 1