#get the data and copy locally
#copy (select distinct(purchaseordernumber) from contracts where not purchaseordernumber like '%unknown%') TO '/tmp/pos.csv' DELIMITER ',' CSV;
#scp abe@projects.thelensnola.org:/tmp/pos.csv .

import urllib2
import os
from time import sleep
from random import randint

vendor_loc = "/Volumes/bigone/lensdata/contracts/purchase_orders/"


def download_purchaseorder(vendor_no):
    response = urllib2.urlopen('http://www.purchasing.cityofno.com/bso/external/purchaseorder/poSummary.sdo?docId=' + vendor_no + '&releaseNbr=0&parentUrl=contract')
    html = response.read()
    return html


def write_pos (vendor_no, html):
    f = open(vendor_no,'w')
    f.write(html) # python will convert \n to os.linesep
    f.close() # you can omit in most cases as the destructor will call if


purchaseordernos = [purchaseorderno.replace("\n", "").strip() for purchaseorderno in open("pos.csv")]

for purchaseorderno in purchaseordernos:
    file_loc = vendor_loc + purchaseorderno
    if not os.path.isfile(file_loc):
        print "getting {}".format(file_loc)
        html = download_purchaseorder(purchaseorderno)
        write_pos (file_loc, html)
        sleep_number = randint(10,10000)
        print "sleeping for {}".format(sleep_number)
        sleep(sleep_number) #sleep between 10 and 1000 seconds
    else:
        print "skipping {}".format(file_loc)