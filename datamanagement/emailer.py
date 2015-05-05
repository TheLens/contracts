#!/usr/bin/python
import dateutil.parser
import subprocess
import datetime
import subprocess
import time
import smtplib

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from contracts.datamanagement.lib.models import LensDatabase
from contracts.datamanagement.lib.ethics_record import EthicsRecord
from contracts.lib.vaultclasses import Contract
from contracts.settings import Settings
from jinja2 import Environment, FileSystemLoader

SETTINGS = Settings()
TEMPLATE_LOC = SETTINGS.templates
env = Environment(loader=FileSystemLoader(TEMPLATE_LOC))
template = env.get_template('email.html')


def sendEmail(title, message):
    for to in SETTINGS.to_list:
        gmail_user = SETTINGS.sender
        smtpserver = smtplib.SMTP('smtp.gmail.com', 587)
        smtpserver.ehlo()
        smtpserver.starttls()
        smtpserver.ehlo
        smtpserver.login(SETTINGS.gmail_user, SETTINGS.email_pw)
        msg = MIMEMultipart('alternative')
        msg['Subject'] = title
        msg['From'] = gmail_user
        msg['To'] = to
        text = "Alert from The Lens"
        html = '<html><head></head><body>' + message + '</body></html>'

        part1 = MIMEText(text, 'plain')
        part2 = MIMEText(html, 'html')

        msg.attach(part1)
        msg.attach(part2)

        smtpserver.sendmail(SETTINGS.gmail_user, to, msg.as_string())
        smtpserver.close()


def get_message():
    with LensDatabase() as lens_db:
        contracts = lens_db.get_daily_contracts()
        len_contracts = str(len(contracts))
        output = template.render(len_contracts=len_contracts)  
        for contract in contracts:
            output +=  '<tr>'
            cid = contract[0]
            vendor = contract[1]
            output += '<td WIDTH="20%">' + vendor + '</td>'
            output += '<td WIDTH="20%">' + "https://www.documentcloud.org/documents/" + cid + '</td>'
            output += '<td WIDTH="60%">' 
            names = lens_db.get_people_associated_with_vendor(vendor)
            for name in names:
                contributions = lens_db.get_state_contributions(name)
                if len(contributions) > 0:
                    output += "<br><br>" + name + "<br><br>" 
                    for contribution in contributions:
                        output += "<br>" + str(contribution)
            output += '</td>' 
            output += '</tr>'
        output += '</table>'
    return output

sendEmail('Contracts from The Vault: ' + time.strftime("%x"), get_message())

session.close()
