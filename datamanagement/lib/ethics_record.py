#!/usr/bin/python

"""
This class simply represents a single row of
campaign finance contributions (from the Louisiana Ethics Board).
"""

from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class EthicsRecord(Base):
    """
    It goes in datamanagement instead of lib/models because it doesn't
    really concern the public web app
    """
    __tablename__ = 'ethics_records'

    primary_key = Column(Integer, primary_key=True)
    last = Column(String)
    first = Column(String)
    reportno = Column(String)
    form = Column(String)
    schedule = Column(String)
    contributiontype = Column(String)
    contributorname = Column(String)
    address1 = Column(String)
    address2 = Column(String)
    city = Column(String)
    state = Column(String)
    zipcode = Column(String)
    receiptdate = Column(String)
    receiptamount = Column(String)
    description = Column(String)

    def __init__(self,
                 last,
                 first,
                 reportno,
                 form,
                 schedule,
                 contributiontype,
                 contributorname,
                 address1,
                 address2,
                 city,
                 state,
                 zipcode,
                 receiptdate,
                 receiptamount,
                 description):
        self.last = last
        self.first = first
        self.reportno = reportno
        self.form = form
        self.schedule = schedule
        self.contributiontype = contributiontype
        self.contributorname = contributorname
        self.address1 = address1
        self.address2 = address2
        self.city = city
        self.state = state
        self.zipcode = zipcode
        self.receiptdate = receiptdate
        self.receiptamount = receiptamount
        self.description = description


    def __str__(self):
        return "${} to {} {} on {}".format(self.receiptamount, self.first, self.last, self.receiptdate)


    def __repr__(self):
        return "${} to {} {} on {}".format(self.receiptamount, self.first, self.last, self.receiptdate)
