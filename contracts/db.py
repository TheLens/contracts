'''Database tables.'''

from sqlalchemy import Column, Integer, String, ForeignKey, Date, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine

from contracts import CAMPAIGN_CONNECTION_STRING, CONNECTION_STRING

BASE = declarative_base()


class ScrapeLog(BASE):
    '''Track when each index page on the city's purchasing site was scraped.'''
    __tablename__ = 'scrape_log'

    pid = Column(Integer, primary_key=True)
    page = Column(Integer, nullable=False)
    last_scraped = Column(Date, nullable=False)

    def __init__(self, page, last_scraped):
        self.page = page
        self.last_scraped = last_scraped

    def __str__(self):
        return '{0} -- {1.page!s} -- {1.last_scraped!s}'.format(self.__class__.__name__, self)

    def __repr__(self):
        return '{0}({1.page!r}, {1.last_scraped!r})'.format(self.__class__.__name__, self)


class Vendor(BASE):
    '''A company that sells goods or services to the city.

    :param id: The table's primary key, which is also our internal vendor ID.
    :type id: int
    :param name: The vendor's name.
    :type name: string
    :param vendor_id_city: The city purchasing site's vendor ID.
    :type vendor_id_city: string
    '''
    __tablename__ = 'vendors'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    vendor_id_city = Column(String)

    def __init__(self, name, vendor_id_city):
        self.name = name
        self.vendor_id_city = vendor_id_city

    def __str__(self):
        return '{0} -- {1.name!s} -- {1.vendor_id_city!s}'.format(self.__class__.__name__, self)

    def __repr__(self):
        return '{0}({1.name!r}, {1.vendor_id_city!r})'.format(self.__class__.__name__, self)


class Department(BASE):
    '''A city government department. Ex: Blight, sanitation, etc.

    :param id: The table's primary key.
    :type id: int
    :param name: The department name.
    :type name: string
    '''

    __tablename__ = 'departments'

    id = Column(Integer, primary_key=True)
    name = Column(String)

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return '{0} -- {1.name!s}'.format(self.__class__.__name__, self)

    def __repr__(self):
        return '{0}({1.name!r})'.format(self.__class__.__name__, self)


class Person(BASE):
    '''
    A person is a human officer of a company in the Secretary of State's
    business database. Some of those businesses list a business as their
    officer (`companies` table), but this is rare.

    :param id: The table's primary key.
    :type id: int
    :param name: The company officer's name.
    :type name: string
    '''

    __tablename__ = 'people'

    id = Column(Integer, primary_key=True)
    name = Column(String)

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return '{0} -- {1.name!s}'.format(self.__class__.__name__, self)

    def __repr__(self):
        return '{0}({1.name!r})'.format(self.__class__.__name__, self)


class Company(BASE):
    '''
    A business that is the officer of a business
    that listed in the Secretary of State's business system. Most businesses in
    the Secretary of State's business system have human officers (`people`
    table).

    :param id: The table's primary key.
    :type id: int
    :param name: The company name.
    :type name: string
    '''

    __tablename__ = 'companies'

    id = Column(Integer, primary_key=True)
    name = Column(String)

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return '{0} -- {1.name!s}'.format(self.__class__.__name__, self)

    def __repr__(self):
        return '{0}({1.name!r})'.format(self.__class__.__name__, self)


class Address(BASE):
    '''
    The addresses for companies or people.

    :param id: The table's primary key.
    :type id: int
    :param street: The street address.
    :type street: string
    :param city: The city.
    :type city: string
    :param state: The state.
    :type state: string
    :param zipcode: The ZIP code.
    :type zipcode: int
    :param sourcefile: ???
    :type sourcefile: string
    '''

    __tablename__ = 'addresses'

    id = Column(Integer, primary_key=True)
    street = Column(String)
    city = Column(String)
    state = Column(String)
    zipcode = Column(Integer)
    sourcefile = Column(String)

    def __init__(self, street, city, state, zipcode, sourcefile):
        self.street = street
        self.city = city
        self.state = state
        self.zipcode = zipcode
        self.sourcefile = sourcefile

    def __str__(self):
        return '{0} -- {1.street!s} -- {1.city!s} -- {1.sourcefile!s}'.format(self.__class__.__name__, self)

    def __repr__(self):
        return '{0}({1.street!r}, ' \
               '{1.city!r}, ' \
               '{1.state!r}, ' \
               '{1.zipcode!r}, ' \
               '{1.sourcefile!r})'.format(self.__class__.__name__, self)


class Contract(BASE):
    '''
    The city uses two ID numbers to track contracts: K numbers and purchase
    order numbers.

    To buy anything, the city must go through an internal approval process that
    generates a purchase order. This purchase order number gets associated with
    the final contract.

    Each contract that goes to the law department also gets assigned a
    sequential K number. But some contracts are rejected by the law department
    and are later resubmitted. If this happens, the K number is retired.
    Therefore, there can be gaps in the K numbers.

    :param id: The table's primary key.
    :type id: int
    :param departmentid: ???, foreign key points to departments.id.
    :type departmentid: int
    :param vendorid: ???, foreign key points to vendors.id.
    :type vendorid: int
    :param contractnumber: The contract number.
    :type contractnumber: string
    :param purchaseordernumber: The contract's purchase order number.
    :type purchaseordernumber: string
    :param doc_cloud_id: The unique ID for this contract on our DocumentCloud \
                         project. The URL for the contract on DocumentCloud \
                         will be https://www.documentcloud.org/documents/\
                         {{doc_cloud_id}}}.html
    :type doc_cloud_id: string
    :param description: The contract's description?
    :type description: string
    :param title: The contract's title?
    :type title: string
    :param dateadded: ???
    :type dateadded: date
    '''

    __tablename__ = 'contracts'

    id = Column(Integer, primary_key=True)
    departmentid = Column(Integer, ForeignKey("departments.id"))
    vendorid = Column(Integer, ForeignKey("vendors.id"))  # DB vendor ID
    contractnumber = Column(String)
    purchaseordernumber = Column(String)
    doc_cloud_id = Column(String, nullable=False)  # DocumentCloud's vendor ID
    description = Column(String)
    title = Column(String)
    dateadded = Column(Date)

    def __init__(self, ponumber=None, contractnumber=None, vendor_id=None,
                 department_id=None, dcid=None, descript=None, name=None,
                 added=None):
        self.purchaseordernumber = ponumber
        self.contractnumber = contractnumber
        self.vendorid = vendor_id
        self.departmentid = department_id
        self.doc_cloud_id = dcid
        self.description = descript
        self.title = name
        self.dateadded = added

    def __str__(self):
        return '{0} -- {1.purchaseordernumber!s} -- ' \
               '{1.contractnumber!s} -- ' \
               '{1.vendorid!s} -- ' \
               '{1.departmentid!s} -- ' \
               '{1.doc_cloud_id!s} -- ' \
               '{1.description!s} -- ' \
               '{1.title!s} -- ' \
               '{1.dateadded!s}'.format(self.__class__.__name__, self)

    def __repr__(self):
        return '{0}(ponumber={1.purchaseordernumber!r}, ' \
               'contractnumber={1.contractnumber!r}, ' \
               'vendor_id={1.vendorid!r}, ' \
               'department_id={1.departmentid!r}, ' \
               'dcid={1.doc_cloud_id!r}, ' \
               'descript={1.description!r}, ' \
               'name={1.title!r}, ' \
               'added={1.dateadded!r})'.format(self.__class__.__name__, self)


class CompanyAddress(BASE):
    '''
    A link table between addresses and companies.

    :param id: The table's primary key.
    :type id: int
    :param personID: ???, foreign key points to companies.id.
    :type personID: int
    :param companyID: ???, foreign key points to addresses.id.
    :type companyID: int
    :param primaryaddress: ???
    :type primaryaddress: boolean
    '''

    __tablename__ = 'companiesaddresses'

    id = Column(Integer, primary_key=True)
    personID = Column(Integer, ForeignKey("companies.id"), nullable=False)
    companyID = Column(Integer, ForeignKey("addresses.id"), nullable=False)
    primaryaddress = Column(Boolean)

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return '{0} -- {1.name!s}'.format(self.__class__.__name__, self)

    def __repr__(self):
        return '{0}({1.name!r})'.format(self.__class__.__name__, self)


class PersonAddress(BASE):
    '''
    A link table between people to addresses.

    :param id: The table's primary key.
    :type id: int
    :param personID: ???, foreign key points to people.id.
    :type personID: int
    :param companyID: ???, foreign key points to address.id.
    :type companyID: int
    :param primaryaddress: ???
    :type primaryaddress: boolean
    '''

    __tablename__ = 'peopleaddresses'

    id = Column(Integer, primary_key=True)
    personID = Column(Integer, ForeignKey("people.id"), nullable=False)
    companyID = Column(Integer, ForeignKey("addresses.id"), nullable=False)
    primaryaddress = Column(Boolean)

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return '{0} -- {1.name!s}'.format(self.__class__.__name__, self)

    def __repr__(self):
        return '{0}({1.name!r})'.format(self.__class__.__name__, self)


class VendorOfficer(BASE):
    '''
    A link table between vendors and their officers.

    :param id: The table's primary key.
    :type id: int
    :param vendorid: ???, foreign key points to vendors.id.
    :type vendorid: int
    :param personid: ???, foreign key points to people.id.
    :type personid: int
    '''

    __tablename__ = 'vendorsofficers'

    id = Column(Integer, primary_key=True)
    vendorid = Column(Integer, ForeignKey("vendors.id"), nullable=False)
    personid = Column(Integer, ForeignKey("people.id"), nullable=False)

    def __init__(self, vendorid, personid):
        self.vendorid = vendorid
        self.personid = personid

    def __str__(self):
        return '{0} -- {1.vendorid!s} -- {1.personid!s}'.format(self.__class__.__name__, self)

    def __repr__(self):
        return '{0}({1.vendorid!r}, {1.personid!r})'.format(self.__class__.__name__, self)


class VendorOfficerCompany(BASE):
    '''
    A link table between vendors (from the city's system) and companies.

    :param id: The table's primary key.
    :type id: int
    :param vendorid: ???, foreign key points to vendors.id.
    :type vendorid: int
    :param companiesid: ???, foreign key points to companies.id.
    :type companiesid: int
    :param primaryaddress: ???
    :type primaryaddress: boolean
    '''

    __tablename__ = 'vendorsofficerscompanies'

    id = Column(Integer, primary_key=True)
    vendorid = Column(Integer, ForeignKey("vendors.id"), nullable=False)
    companiesid = Column(Integer, ForeignKey("companies.id"), nullable=False)
    primaryaddress = Column(Boolean)

    def __init__(self, vendor_id, company_id):
        self.vendorid = vendor_id
        self.companiesid = company_id

    def __str__(self):
        return '{0} -- {1.vendorid!s} -- {1.companiesid!s}'.format(self.__class__.__name__, self)

    def __repr__(self):
        return '{0}({1.vendorid!r}, {1.companiesid!r})'.format(self.__class__.__name__, self)


class EthicsRecord(BASE):
    '''
    A table with 1,856,193 rows of campaign contributions.

    :param primary_key: The table's primary key.
    :type primary_key: int
    :param last: ???
    :type last: string
    :param first: ???
    :type first: string
    :param reportno: ???
    :type reportno: string
    :param form: ???
    :type from: string
    :param schedule: ???
    :type schedule: string
    :param contributiontype: ???
    :type contributiontype: string
    :param contributorname: ???
    :type contributorname: string
    :param address1: ???
    :type address1: string
    :param address2: ???
    :type address2: string
    :param city: ???
    :type city: string
    :param state: ???
    :type state: string
    :param zipcode: ???
    :type zipcode: string
    :param receiptdate: ???
    :type receiptdate: string
    :param receiptamount: ???
    :type receiptamount: string
    :param description: ???
    :type description: string
    '''

    __tablename__ = 'ethics_records'

    id = Column(Integer, primary_key=True)
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
        return '{0} -- ' \
               '{1.last!s} -- ' \
               '{1.first!s} -- ' \
               '{1.reportno!s} -- ' \
               '{1.form!s} -- ' \
               '{1.schedule!s} -- ' \
               '{1.contributiontype!s} -- ' \
               '{1.contributorname!s} -- ' \
               '{1.address1!s} -- ' \
               '{1.address2!s} -- ' \
               '{1.city!s} -- ' \
               '{1.state!s} -- ' \
               '{1.zipcode!s} -- ' \
               '{1.receiptdate!s} -- ' \
               '{1.receiptamount!s} -- ' \
               '{1.description!s}'.format(self.__class__.__name__, self)

    def __repr__(self):
        return '{0}({1.last!r}, ' \
               '{1.first!r}, ' \
               '{1.reportno!r}, ' \
               '{1.form!r}, ' \
               '{1.schedule!r}, ' \
               '{1.contributiontype!r}, ' \
               '{1.contributorname!r}, ' \
               '{1.address1!r}, ' \
               '{1.address2!r}, ' \
               '{1.city!r}, ' \
               '{1.state!r}, ' \
               '{1.zipcode!r}, ' \
               '{1.receiptdate!r}, ' \
               '{1.receiptamount!r}, ' \
               '{1.description!r})'.format(self.__class__.__name__, self)


def remake_db():
    '''Create the database.'''
    engine = create_engine(CONNECTION_STRING)
    BASE.metadata.create_all(engine)

    campaign_engine = create_engine(CAMPAIGN_CONNECTION_STRING)
    BASE.metadata.create_all(campaign_engine)

if __name__ == "__main__":
    remake_db()
