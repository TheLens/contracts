
"""
These classes that map to tables in the underlying database.
"""

from sqlalchemy import Column, Integer, String, ForeignKey, Date, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from contracts import CONNECTION_STRING

Base = declarative_base()


class Vendor(Base):
    """
    A vendor sells goods or services to the city. [*] vendor_id_city is city's
    ID number for the vendor.
    """

    __tablename__ = 'vendors'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    vendor_id_city = Column(String)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "<Vendor(Name='%s'>" % self.name


class Department(Base):
    """
    A department is a part of city government. Ex: Blight or Sanitation.
    """

    __tablename__ = 'departments'

    id = Column(Integer, primary_key=True)
    name = Column(String)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "<Department(Name='%s')>" % self.name


class Person(Base):
    """
    A person is an officer of a company.
    """

    __tablename__ = 'people'

    id = Column(Integer, primary_key=True)
    name = Column(String)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "<Person(Name='%s')>" % self.name


class Company(Base):
    """
    A company does business with the city.
    """

    __tablename__ = 'companies'

    id = Column(Integer, primary_key=True)
    name = Column(String)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "<Company(Name='%s')>" % self.name


class Address(Base):
    """
    Companies or people can have addresses.
    """

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

    def __repr__(self):
        return (
            "<Address(street='%s', city='%s', state='%s', zipcode='%s')>" % (
                self.street, self.city, self.state, self.zipcode))


class Contract(Base):
    """
    A contract is any piece of paper that gets posted on the city's public
    purchasing portal. Sometimes the city posts "contracts" that are really
    film permits or MOUs. The doc_cloud_id links the contract to DocumentCloud.
    The URL for the contract on DocumentCloud will be
    https://www.documentcloud.org/documents/{{doc_cloud_id}}}.html

    The city uses two ID numbers to track contracts: k numbers and PO numbers.

    To buy anything, the city must go through an internal approval process that
    generates a purchase order. This purchase order number gets associated with
    the final contract.

    Each contract that goes to the law department also gets assigned a
    k number. But some contracts are rejected by the law department and are
    resubmitted. If this happens, the k number is retired. So there will be
    gaps in the k numbers.
    """

    __tablename__ = 'contracts'

    id = Column(Integer, primary_key=True)
    departmentid = Column(Integer, ForeignKey("departments.id"))
    vendorid = Column(Integer, ForeignKey("vendors.id"))
    contractnumber = Column(String)
    purchaseordernumber = Column(String)
    doc_cloud_id = Column(String, nullable=False)
    description = Column(String)
    title = Column(String)
    dateadded = Column(Date)

    def __init__(self, ponumber=None,
                 contractnumber=None,
                 vendor_id=None,
                 department_id=None,
                 dcid=None,
                 descript=None,
                 name=None,
                 added=None):
        self.purchaseordernumber = ponumber
        self.contractnumber = contractnumber
        self.vendorid = vendor_id
        self.departmentid = department_id
        self.doc_cloud_id = dcid
        self.description = descript
        self.title = name
        self.dateadded = added

    def __repr__(self):
        return (
            "<Contract: contractnumber {0} purchaseordernumber {1} " +
            "vendorid {2} departmentid {3}>"
        ).format(
            self.contractnumber,
            self.purchaseordernumber,
            self.vendorid,
            self.departmentid
        )


class CompanyAddress(Base):
    """
    Links addresses to companies.
    """

    __tablename__ = 'companiesaddresses'

    id = Column(Integer, primary_key=True)
    personID = Column(Integer, ForeignKey("companies.id"), nullable=False)
    companyID = Column(Integer, ForeignKey("addresses.id"), nullable=False)
    primaryaddress = Column(Boolean)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return (
            "<CompanyAddress(personID={0}, companyID={1}," +
            "primaryaddress={2})>"
        ).format(
            self.personID, self.companyID, self.primaryaddress
        )


class PersonAddress(Base):
    """
    Links people to addresses.
    """

    __tablename__ = 'peopleaddresses'

    id = Column(Integer, primary_key=True)
    personID = Column(Integer, ForeignKey("people.id"), nullable=False)
    companyID = Column(Integer, ForeignKey("addresses.id"), nullable=False)
    primaryaddress = Column(Boolean)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "<PersonAddress>"


class VendorOfficer(Base):
    """
    Links a vendor to people who are its officers.
    """

    __tablename__ = 'vendorsofficers'

    id = Column(Integer, primary_key=True)
    vendorid = Column(Integer, ForeignKey("vendors.id"), nullable=False)
    personid = Column(Integer, ForeignKey("people.id"), nullable=False)

    def __init__(self, vendorid, personid):
        self.vendorid = vendorid
        self.personid = personid

    def __repr__(self):
        return "<VendorOfficer(vendorid='%s')>" % (self.vendorid)


class VendorOfficerCompany(Base):
    """
    Links a vendor (from the city's system) with a company.
    """

    __tablename__ = 'vendorsofficerscompanies'

    id = Column(Integer, primary_key=True)
    vendorid = Column(Integer, ForeignKey("vendors.id"), nullable=False)
    companiesid = Column(Integer, ForeignKey("companies.id"), nullable=False)
    primaryaddress = Column(Boolean)

    def __init__(self, vendor_id, company_id):
        self.vendorid = vendor_id
        self.companiesid = company_id

    def __repr__(self):
        return "<VendorOfficerCompany(vendorid='%s')>" % (self.vendorid)


class EthicsRecord(Base):
    """
    It goes in datamanagement instead of lib/models because it doesn't really
    concern the public web app.
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
        return "${} to {} {} on {}".format(
            self.receiptamount, self.first, self.last, self.receiptdate)

    def __repr__(self):
        return "${} to {} {} on {}".format(
            self.receiptamount, self.first, self.last, self.receiptdate)


def remake_db():
    '''docstring'''

    engine = create_engine(CONNECTION_STRING)
    Base.metadata.create_all(engine)

if __name__ == "__main__":
    remake_db()
