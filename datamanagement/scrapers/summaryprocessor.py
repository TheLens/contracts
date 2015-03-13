#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import csv
import pprint
import sys
import sqlalchemy.exc
import urllib2
import re
import os
import subprocess
import sqlalchemy.exc
import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from bs4 import BeautifulSoup
from contracts.lib.vaultclasses import Contract, Vendor, Department
import datetime
import subprocess
from bs4 import BeautifulSoup
import traceback
import smtplib



def getTitle(vendor, description):
     title = ""
     title = vendor + " : " + description
     return title


def addEmpty(purchaseordernumber):
    if not hasPurchaseOrder(purchaseordernumber):
        e = Contract(purchaseordernumber)
        response = urllib2.urlopen('http://www.purchasing.cityofno.com/bso/external/purchaseorder/poSummary.sdo?docId='+ e.purchaseordernumber + '&releaseNbr=0&parentUrl=contract')
        html = response.read()
        soup = BeautifulSoup(html)
        vendorid = getVendorID(html)
        knumber = getKnumber(soup).replace("M", "")
        department = getDepartment(soup)
        vendor = getVendor(soup)
        addVendor(vendor)
        addDepartment(department)
        description = getDescription(soup)
        attachmentQueue = getAttachmentQueue(soup)
        counter = 1
        for a in attachmentQueue:
            if counter > 1:
                e.purchaseordernumber = e.purchaseordernumber + "_" + str(counter)
            title = getTitle(vendor, description)
            counter += 1 
            bidno = re.findall("[0-9]+", a.attrs['href']).pop()
            downloadFile(bidno)
            data = getMetaData(knumber, e.purchaseordernumber, vendor,department, vendorid)
            doc_cloud_id = uploadContract(bidno, data, description, title)
            e.doc_cloud_id = doc_cloud_id
            os.rename(bidno, str(e.doc_cloud_id) + ".pdf")
            e.vendorid = getVendorID_Lens(vendor)
            e.departmentid = getDepartmentID(department)
            e.title = title
            e.description = description
            e.contractnumber = knumber
            e.dateadded = datetime.datetime.now()
            session.commit()

if __name__ == "__main__":
     for line in sys.stdin:
        purchaseorder = line.replace("\n", "").split("=")[1].replace("&","")
        if session.query(Contract).filter(Contract.purchaseordernumber==purchaseorder).count()==0:
             #print "need to add {}".format(purchaseorder)
             addEmpty(purchaseorder)