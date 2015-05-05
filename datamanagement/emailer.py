#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import csv
import pprint
import sys
import sqlalchemy.exc
import urllib2
import re
import dateutil.parser
import os
import subprocess
import sqlalchemy.exc
import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from contracts.datamanagement.lib.ethics_record import EthicsRecord
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from vaultclasses import Contract
from bs4 import BeautifulSoup
from vaultclasses import Vendor, Department, Contract, Person, VendorOfficer, VendorOfficerCompany, Company
import datetime
import subprocess
import os
import re
from bs4 import BeautifulSoup
import ConfigParser
import traceback
import time
import smtplib
from documentcloud import DocumentCloud


CONFIG_LOCATION = '/apps/contracts/app.cfg'


def getFromFile(field):
    config = ConfigParser.RawConfigParser()
    #print config_location
    config.read(CONFIG_LOCATION)
    return config.get('Section1', field)


databasepassword = getFromFile('databasepassword')
server = getFromFile('server')
database = getFromFile('database')
sender = getFromFile('sender')
pw = getFromFile('email_pw')
gmail_user = getFromFile('gmail_user')
to_list =  getFromFile('to_list').split(",")
engine = create_engine('postgresql://abe:' + databasepassword + '@' + server + ':5432/thevault')


Session = sessionmaker(bind=engine)
Session.configure(bind=engine)
session = Session()


def sendEmail(title, message):
    for to in to_list:
        print to
        gmail_user = sender
        smtpserver = smtplib.SMTP('smtp.gmail.com', 587)
        smtpserver.ehlo()
        smtpserver.starttls()
        smtpserver.ehlo
        smtpserver.login(gmail_user, pw)
        msg = MIMEMultipart('alternative')
        msg['Subject'] = title
        msg['From'] = gmail_user
        msg['To'] = to
        text = "Alert from The Lens"
        html = '<html><head></head><body>' + message + '</body></html>'

        part1 = MIMEText(text, 'plain')
        part2 = MIMEText(html, 'html')

        # Attach parts into message container.
        # According to RFC 2046, the last part of a multipart message, in this case
        # the HTML message, is best and preferred.
        msg.attach(part1)
        msg.attach(part2)

        smtpserver.sendmail(gmail_user, to, msg.as_string())
        smtpserver.close()


def get_daily_contracts(today_string = datetime.datetime.today().strftime('%Y-%m-%d')):  #defaults to today
    contracts = session.query(Contract.doc_cloud_id, Vendor.name).filter(Contract.dateadded==today_string).filter(Contract.vendorid==Vendor.id).all()
    return contracts


def get_state_contributions(name):
    recccs = session.query(EthicsRecord).filter(EthicsRecord.contributorname==name).all()
    recccs.sort(key = lambda x: dateutil.parser.parse(x.receiptdate))
    return recccs


def get_names_from_vendor(name):
    recccs = session.query(Person.name).filter(Vendor.id==VendorOfficer.vendorid).filter(Person.id==VendorOfficer.personid).filter(Vendor.name==name).all()
    return [str(i[0]) for i in recccs]



def get_message():
    contracts = get_daily_contracts() #no parameter means that it gets today's contracts
    output = "<h2>Contract report</h2>" + "<h3>" + "Total of " + str(len(contracts)) + " contracts today</h3>"
    output += '<table border="1" style="background-color:#f0d5d0;border-collapse:collapse;border:1px solid grey;color:#000000;width:100%" cellpadding="3" cellspacing="3">'
    output +=  '<td WIDTH="20%">Company</td><td WIDTH="20%">Link</td><td WIDTH="60%">Donations</td>' 
    for c in contracts:
        output +=  '<tr>'
        cid = c[0]
        vendor = c[1]
        output += '<td WIDTH="20%">' + vendor + '</td>'
        output += '<td WIDTH="20%">' + "https://www.documentcloud.org/documents/" + cid + '</td>'
        output += '<td WIDTH="60%">' 
        names = get_names_from_vendor(vendor)
        for name in names:
            contributions = get_state_contributions(name)
            if len(contributions) > 0:
                output += "<br><br>" + name + "<br><br>" 
                for c in contributions:
                    output += "<br>" + str(c)
        output += '</td>' 
        output += '</tr>'
    output += '</table>'
    return output


sendEmail('Contracts from The Vault: ' + time.strftime("%x"), get_message())


session.close()