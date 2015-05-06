import urllib2
import os
from time import sleep
from random import randint

vendor_loc = "/Volumes/bigone/lensdata/contracts/vendors/"

def i_to_vendor_no(i):
    len_i = len(str(i))
    len_total = len("00000001")
    len_zeros = len_total - len_i
    zeros = ""
    for zero in range(0, len_zeros):
        zeros = zeros + "0"
    vendor_no = zeros + str(i)
    return vendor_no

def download_vendor(vendor_no):
    response = urllib2.urlopen('http://www.purchasing.cityofno.com/bso/external/vendor/vendorProfileOrgInfo.sdo?external=true&vendorId=' + vendor_no)
    html = response.read()
    return html


def write_vendor(vendor_no, html):
    f = open(vendor_no,'w')
    f.write(html) # python will convert \n to os.linesep
    f.close() # you can omit in most cases as the destructor will call if


for i in range(1,10000):
    vendor_no = i_to_vendor_no(i)
    file_loc = vendor_loc + vendor_no
    if not os.path.isfile(file_loc):
        print "getting {}".format(file_loc)
        html = download_vendor(vendor_no)
        write_vendor(file_loc, html)
        sleep_number = randint(10,10000)
        print "sleeping for {}".format(sleep_number)
        sleep(sleep_number) #sleep between 10 and 1000 seconds
    else:
        print "skipping {}".format(file_loc)

