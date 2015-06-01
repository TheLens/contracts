
'''docstring'''

import os
import time
import smtplib

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from contracts.lib.lens_database import LensDatabase


def send_email(title, message):
    '''Sends the email.'''

    print os.environ.get('EMAIL_TO_LIST')
    for to in os.environ.get('EMAIL_TO_LIST').split(","):
        print to
        gmail_user = os.environ.get('EMAIL_FROM')
        smtpserver = smtplib.SMTP('smtp.gmail.com', 587)
        smtpserver.ehlo()
        smtpserver.starttls()
        smtpserver.ehlo
        smtpserver.login(
            os.environ.get('GMAIL_USERNAME'),
            os.environ.get('GMAIL_PASSWORD'))
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

        smtpserver.sendmail(
            os.environ.get('GMAIL_USERNAME'), to, msg.as_string())
        smtpserver.close()


def get_message():
    '''Includes the logic for what to show in the email.'''

    with LensDatabase() as lens_db:
        contracts = lens_db.get_daily_contracts()
        len_contracts = str(len(contracts))

        # output = template.render(len_contracts=len_contracts)
        output = (
            "<h2>Contract report</h2>\n" +
            "<h3>Total of %s contracts today</h3>\n" % len_contracts +
            "<table style='background-color: #F0D5D0; color: #000; " +
            "border-collapse: collapse; border: 1px solid grey; " +
            "width: 100%' border='1' cellpadding='3' cellspacing='3'>\n" +
            "<td width='20%'>Company</td>" +
            "<td width='20%'>Link</td>" +
            "<td width='60%'>Donations</td>"
        )

        # there are two loops here, so not sure how to put it into template
        # Not sure if it is worth the headache...
        for contract in contracts:
            output += '<tr>'
            cid = contract[0]
            vendor = contract[1]
            output += '<td width="20%">' + vendor + '</td>'
            output += '<td width="20%">' + \
                "https://www.documentcloud.org/documents/" + cid + '</td>'
            output += '<td width="60%">'
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


if __name__ == '__main__':
    send_email(
        'Contracts from The Vault: ' + time.strftime("%x"),
        get_message()
    )
