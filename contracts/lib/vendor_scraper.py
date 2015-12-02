
'''docstring'''

import urllib2
import os
from time import sleep
from random import randint
from contracts import VENDORS_LOCATION


def i_to_vendor_no(i):
    '''docstring'''

    len_i = len(str(i))
    len_total = len("00000001")
    len_zeros = len_total - len_i
    zeros = ""
    for zero in range(0, len_zeros):
        zeros = zeros + "0"
    vendor_number = zeros + str(i)

    return vendor_number


def download_vendor(vendor_no):
    '''docstring'''

    response = urllib2.urlopen(
        'http://www.purchasing.cityofno.com/bso/external/vendor/' +
        'vendorProfileOrgInfo.sdo?external=true&vendorId=' +
        vendor_no)
    html_out = response.read()

    return html_out


def write_vendor(file_loc, html):
    '''docstring'''

    open_file = open(file_loc, 'w')
    open_file.write(html)  # python will convert \n to os.linesep
    open_file.close()  # you can omit in most cases.The destructor will call if


if __name__ == '__main__':
    for i in range(1, 10000):
        vendor_no = i_to_vendor_no(i)
        file_loc = VENDORS_LOCATION + vendor_no
        if not os.path.isfile(file_loc):
            print "getting {}".format(file_loc)
            html = download_vendor(vendor_no)
            write_vendor(file_loc, html)
            sleep_number = randint(10, 10000)
            print "sleeping for {}".format(sleep_number)
            sleep(sleep_number)  # sleep between 10 and 1000 seconds
        else:
            print "skipping {}".format(file_loc)
