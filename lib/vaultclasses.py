import datetime
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Date, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
import ConfigParser

Base = declarative_base()

from contracts.settings import Settings

class Vendor(Base):
	__tablename__ = 'vendors'

	id = Column(Integer, primary_key=True)
	name = Column(String)

	def __init__(self, name):
		self.name = name

	def __repr__(self):
		return "<Vendor: {}>".format(self.name)

class Department(Base):
	__tablename__ = 'departments'

	id = Column(Integer, primary_key=True)
	name = Column(String)

	def __init__(self, name):
		self.name = name

	def __repr__(self):
		return "<Department(Department='%s')>" % (self.department)

class Person(Base):
	__tablename__ = 'people'

	id = Column(Integer, primary_key=True)
	name = Column(String)

	def __init__(self, name):
		self.name = name

	def __repr__(self):
		return "<Person(Name='%s')>" % (self.name)

class Company(Base):
	__tablename__ = 'companies'

	id = Column(Integer, primary_key=True)
	name = Column(String)

	def __init__(self, name):
		self.name = name

	def __repr__(self):
		return "<Department(Department='%s')>" % (self.department)

class Address(Base):
	__tablename__ = 'addresses'

	id = Column(Integer, primary_key=True)
	street = Column(String)
	city = Column(String)
	state = Column(String)
	zipcode = Column(Integer)
	sourcefile = Column(String)

	def __init__(self, street,city,state,zipcode,sourcefile):
		self.street = street
		self.city = city
		self.state = state
		self.zipcode = zipcode
		self.sourcefile = sourcefile

	def __repr__(self):
		return "<Department(Department='%s')>" % (self.department)

class Contract(Base):
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

	def __init__(self, pn,cn = None, vi= None, di= None, dcid= None, descript= None, name= None, added= None):
		self.purchaseordernumber = pn
		self.contractnumber = cn
		self.vendorid = vi
		self.departmentid = di
		self.doc_cloud_id = dcid
		self.description = descript
		self.title = name
		self.dateadded = added

	def __repr__(self):
		return "<Contract: contractnumber {} purchaseordernumber {} vendorid {} departmentid {}>".format(self.contractnumber, self.purchaseordernumber, self.vendorid, self.departmentid)
		

class CompanyAddress(Base):
	__tablename__ = 'companiesaddresses'

	id = Column(Integer, primary_key=True)
	personID = Column(Integer, ForeignKey("companies.id"), nullable=False)
	companyID = Column(Integer, ForeignKey("addresses.id"), nullable=False)
	primaryaddress = Column(Boolean)

	def __init__(self, name):
		self.name = name

	def __repr__(self):
		return "<Department(Department='%s')>" % (self.department)


class PersonAddress(Base):
	__tablename__ = 'peopleaddresses'

	id = Column(Integer, primary_key=True)
	personID = Column(Integer, ForeignKey("people.id"), nullable=False)
	companyID = Column(Integer, ForeignKey("addresses.id"), nullable=False)
	primaryaddress = Column(Boolean)

	def __init__(self, name):
		self.name = name

	def __repr__(self):
		return "<Department(Department='%s')>" % (self.department)


class VendorOfficer(Base):
	__tablename__ = 'vendorsofficers'

	id = Column(Integer, primary_key=True)
	vendorid = Column(Integer, ForeignKey("vendors.id"), nullable=False)
	personid = Column(Integer, ForeignKey("people.id"), nullable=False)

	def __init__(self, vendorID, personID):
		self.vendorid = vendorID
		self.personid = personID

	def __repr__(self):
		return "<VendorOfficer(Department='%s')>" % (self.vendorid)

class VendorOfficerCompany(Base):
	__tablename__ = 'vendorsofficerscompanies'

	id = Column(Integer, primary_key=True)
	vendorid = Column(Integer, ForeignKey("vendors.id"), nullable=False)
	companiesid = Column(Integer, ForeignKey("companies.id"), nullable=False)
	primaryaddress = Column(Boolean)

	def __init__(self, vendor_id, company_id):
		self.vendorid = vendor_id
		self.companiesid = company_id

	def __repr__(self):
		return "<VendorOfficerCompany(Department='%s')>" % (self.vendorid)


def remakeDB():
	engine = create_engine('postgresql://' + user + ':' + databasepassword + '@' + server + ':5432/thevault')
	Base.metadata.create_all(engine)

if __name__ == "__main__":
    remakeDB()