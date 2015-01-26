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
from vaultclasses import Contract
from bs4 import BeautifulSoup
from vaultclasses import Contract, Vendor, Department
import datetime
import subprocess
import os
import re
from bs4 import BeautifulSoup
import ConfigParser
import traceback
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
to_list =  getFromFile('to_list').split()

def sendEmail(title, message):
    to = to_list.pop()
    gmail_user = sender
    gmail_pwd = pw
    smtpserver = smtplib.SMTP('smtp.gmail.com', 587)
    smtpserver.ehlo()
    smtpserver.starttls()
    smtpserver.ehlo
    smtpserver.login(gmail_user, gmail_pwd)
    header = 'To:' + to + '\n' + 'From: ' + gmail_user + '\n' \
        + 'Subject:' + title + '\n'
    msg = header + message
    smtpserver.sendmail(gmail_user, to, msg)
    smtpserver.close()

sendEmail('hiyo silver', 'send via automagicx')