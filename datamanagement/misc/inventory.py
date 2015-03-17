#what do we have? What are we missing? This script answers

from contracts.datamanagement.lib.models import DocumentCloudProject, PurchaseOrder
from contracts.settings import Settings


skiplist = ["AV157123", "AV260408", "AV265701", "AV368931", "AV370951", "AV484558", "AV485159", "AV485392", "AV485393", "AV485394", "AV486592", "AV486594", "AV487176", "AV488387", "AV488631", "AV488632", "AV489081", "AV489714", "AV489803", "AV490794", "AV491382"]

log = [f.replace("\n", "") for f in open("/home/abe/lens/contracts/datamanagement/misc/raw_contract_log_processed.csv")]

log = [l for l in log if l not in skiplist] #aviation contracts are not included on the public site. so we won't have them in our repo.

proj = DocumentCloudProject()

for l in log:
    if not proj.has_contract("purchase order", l):
        print l