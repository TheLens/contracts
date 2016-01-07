
'''
The tables for local database that mirrors DocumentCloud project and
methods for interacting with that database.
'''

from datetime import date, timedelta

from sqlalchemy import (create_engine, desc, Column, Integer, String,
                        ForeignKey, Date)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from contracts import CONNECTION_STRING, TODAY_DATE, log

Base = declarative_base()

# Emoji
red_stop_emoji = "\xF0\x9F\x9A\xAB"
green_check_emoji = "\xE2\x9C\x85"


class Address(Base):
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

    def __repr__(self):
        return (
            "<Address(street='%s', city='%s', state='%s', zipcode='%s')>" % (
                self.street, self.city, self.state, self.zipcode))


class Archive(Base):
    '''
    A backup of our DocumentCloud projects. Only receives data from
    DocumentCloud.
    '''

    __tablename__ = 'archive'

    id = Column(Integer, primary_key=True)

    # Metadata from DocumentCloud
    access = Column(String, nullable=True)
    canonical_url = Column(String, nullable=True)
    contributor = Column(String, nullable=True)
    contributor_organization = Column(String, nullable=True)
    created_at = Column(Date)
    description = Column(String, nullable=True)
    document_cloud_id = Column(String, nullable=True)
    document_title = Column(String, nullable=True)
    full_text_url = Column(String, nullable=True)
    large_image_url = Column(String, nullable=True)
    normal_image_url = Column(String, nullable=True)
    number_of_pages = Column(Integer, nullable=True)
    pdf_url = Column(String, nullable=True)
    project_id = Column(String, nullable=True)
    project_title = Column(String, nullable=True)
    published_url = Column(String, nullable=True)
    related_article = Column(String, nullable=True)
    small_image_url = Column(String, nullable=True)
    source = Column(String, nullable=True)
    thumbnail_image_url = Column(String, nullable=True)
    updated_at = Column(Date, nullable=True)

    # Custom metadata
    contract_number = Column(String, nullable=True)
    department = Column(String, nullable=True)
    purchase_order = Column(String, nullable=True)
    vendor = Column(String, nullable=True)
    vendor_id = Column(String, nullable=True)


class Company(Base):
    '''
    A "company" in this table is a businnes that is the officer of a business
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

    def __repr__(self):
        return "<Company(Name='%s')>" % self.name


class Contract(Base):
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
    # Our database's internal vendor ID:
    vendorid = Column(Integer, ForeignKey("vendors.id"))
    contractnumber = Column(String)
    purchaseordernumber = Column(String)
    # DocumentCloud project's vendor ID:
    doc_cloud_id = Column(String, nullable=False)
    description = Column(String)
    title = Column(String)
    dateadded = Column(Date)

    def __init__(self,
                 ponumber=None,
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
        return ("<Contract: contractnumber {0} purchaseordernumber {1} " +
                "vendorid {2} departmentid {3}>").format(
            self.contractnumber,
            self.purchaseordernumber,
            self.vendorid,
            self.departmentid)


class Department(Base):
    '''
    A department is a part of city government. Ex: Blight, sanitation.

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

    def __repr__(self):
        return "<Department(Name='%s')>" % self.name


class Person(Base):
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

    def __repr__(self):
        return "<Person(Name='%s')>" % self.name


class ScrapeLog(Base):
    '''
    Keeps a record of the last time we checked each index page on the city's
    purchasing site.
    '''

    __tablename__ = 'scrape_log'

    pid = Column(Integer, primary_key=True)
    page = Column(Integer, nullable=False)
    last_scraped = Column(Date, nullable=False)

    def __init__(self, page, last_scraped):
        self.page = page
        self.last_scraped = last_scraped

    def __repr__(self):
        return "<ScrapeLog (Page='%s', Last scraped=%s>" % (
            self.page, self.last_scraped)


class Vendor(Base):
    '''
    A vendor is a company that sells goods or services to the city.

    :param id: The table's primary key, which is also our internal vendor ID.
    :type id: int
    :param name: The vendor's name.
    :type name: string
    :param vendor_id_city: The city purchasing site's vendor ID.
    :type vendor_id_city: string
    '''

    __tablename__ = 'vendors'

    id = Column(Integer, primary_key=True)  # Our internal unique ID
    name = Column(String)
    vendor_id_city = Column(String)

    def __init__(self, name, vendor_id_city):
        self.name = name
        self.vendor_id_city = vendor_id_city

    def __repr__(self):
        return "<Vendor(Name='%s', City vendor ID=%s>" % (
            self.name, self.vendor_id_city)


class VendorOfficer(Base):
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

    def __repr__(self):
        return "<VendorOfficer(vendorid='%s')>" % (self.vendorid)


# class VendorOfficerCompany(Base):
#     '''
#     A link table between vendors (from the city's system) and companies.

#     :param id: The table's primary key.
#     :type id: int
#     :param vendorid: ???, foreign key points to vendors.id.
#     :type vendorid: int
#     :param companiesid: ???, foreign key points to companies.id.
#     :type companiesid: int
#     :param primaryaddress: ???
#     :type primaryaddress: boolean
#     '''

#     __tablename__ = 'vendorsofficerscompanies'

#     id = Column(Integer, primary_key=True)
#     vendorid = Column(Integer, ForeignKey("vendors.id"), nullable=False)
#     companiesid = Column(Integer, ForeignKey("companies.id"), nullable=False)
#     primaryaddress = Column(Boolean)

#     def __init__(self, vendor_id, company_id):
#         self.vendorid = vendor_id
#         self.companiesid = company_id

#     def __repr__(self):
#         return "<VendorOfficerCompany(vendorid='%s')>" % (self.vendorid)


class Db(object):
    '''Represents the local database that stores contracts information.'''

    def __init__(self):
        self.engine = create_engine(CONNECTION_STRING)
        self.sn = sessionmaker(bind=self.engine)

    def remake_db(self):
        '''Creates the database via SQLAlchemy.'''

        Base.metadata.create_all(self.engine)

    def check_if_database_has_contract(self, purchase_order_number):
        '''
        Checks if database already has this contract.

        :param purchase_order_number: The unique ID in the city's website.
        :type purchase_order_number: string
        :returns: boolean. True if the contract is present, False if not.
        '''

        session = self.sn()

        query_count = (
            session.query(Contract)
            .filter(Contract.purchaseordernumber == purchase_order_number)
            .count())

        session.close()

        if query_count == 1:  # Database has the contract
            print '%s  Database already has purchase ' % (red_stop_emoji) + \
                'order %s in contracts table.' % purchase_order_number
            log.debug(
                '%s  ' % (red_stop_emoji) +
                'Database already has purchase order %s in contracts table.',
                purchase_order_number)

            return True

        return False

    def add_to_database(self, purchase_order_object):
        '''
        Add this contract to the local database. Initialize a Contract object
        class instance and fill out with the relevant information.

        :param purchase_order_object: The PurchaseOrder object instance.
        :type purchase_order_object: A PurchaseOrder object instance.
        '''

        print "%s  " % (green_check_emoji) + \
            "Adding purchase order %s to database's contracts table..." % (
                purchase_order_object.purchase_order_number)
        log.debug(
            "%s  " % (green_check_emoji) +
            "Adding purchase order %s to database's contracts table.",
            purchase_order_object.purchase_order_number)

        session = self.sn()

        contract = Contract()

        # TODO: Might need to have a follow-up method that pulls from
        # DocumentCloud project and inserts its ID into this row in the
        # database.
        # contract.doc_cloud_id = TODO

        contract.contractnumber = purchase_order_object.k_number
        contract.purchaseordernumber = purchase_order_object.purchaseorder
        contract.description = purchase_order_object.description
        contract.title = purchase_order_object.title
        contract.dateadded = date.today()

        self._add_department_if_missing(purchase_order_object.department)
        self._add_vendor_if_missing(
            purchase_order_object.vendor_name,
            vendor_id_city=purchase_order_object.vendor_id_city)

        contract.departmentid = self._get_department_id(
            purchase_order_object.department)
        contract.vendorid = self._get_database_vendor_id(
            purchase_order_object.vendor_name)

        self._add_contract_to_local_database(contract)

        session.close()

    def get_daily_contracts(self):
        '''
        Get today's contracts (and the vendors).

        Not called on by this class, but is called on by emailer.py.

        :returns: A list of dicts (?) for the daily contracts.
        '''

        session = self.sn()

        contracts = (
            session.query(Contract.doc_cloud_id, Vendor.name)
            .filter(Contract.dateadded == TODAY_DATE)
            .filter(Contract.vendorid == Vendor.id)
            .all())

        session.close()

        return contracts

    def get_all_contract_ids(self):
        '''
        Fetches a list of all of the contract IDs in our DocumentCloud project.

        Not called on by this class, but is called on by backup.py.

        :returns: list. A list of all IDs in our DocumentCloud project.
        '''

        log.debug('Fetching a list of all contract IDs in database.')

        session = self.sn()

        query = (
            session.query(Contract.doc_cloud_id)
            .order_by(desc(Contract.dateadded))
            .all())

        session.close()

        document_ids = []

        for row in query:
            document_ids.append(row[0])

        return document_ids

    def get_people_associated_with_vendor(self, name):
        '''
        Get a list of people associated with the vendor.

        Not called on by this class, but is called on by emailer.py.

        :param name: The vendor name.
        :type name: string
        :returns: list. The people who are associated with this vendor (how?).
        '''

        log.debug('Finding people associated with %s.', name)

        session = self.sn()

        query_people = (
            session.query(Person.name)
            .filter(Vendor.id == VendorOfficer.vendorid)
            .filter(Person.id == VendorOfficer.personid)
            .filter(Vendor.name == name)
            .all())

        session.close()

        people = []

        for row in query_people:
            people.append(str(row[0]))

        return people

    def check_if_need_to_scrape(self, page):
        '''
        If page is <= 10 and last scrape was before today, scrape.
        If page is > 10 and last scrape was more than seven days ago, scrape.

        :params page: The purchasing site page number to check.
        :type page: int.
        :returns: boolean. True if need to scrape, False if not.
        '''

        today_date = date.today()
        week_ago_date = date.today() - timedelta(days=7)

        date_last_scraped = self._check_when_last_scraped(page)

        if date_last_scraped is None:
            return True  # Scrape this page
        elif page <= 10:
            if date_last_scraped < today_date:
                return True  # Scrape this page
            else:
                log.debug('Page %d has been scraped recently. Skipping.', page)
                print 'Page %d has been scraped recently. Skipping.' % page

                return False
        elif page > 10:
            if date_last_scraped < week_ago_date:
                return True  # Scrape this page
            else:
                log.debug('Page %d has been scraped recently. Skipping.', page)
                print 'Page %d has been scraped recently. Skipping.' % page

                return False

    def _check_when_last_scraped(self, page):
        '''
        Looks up this page in scrape_log table to see when it was last scraped.

        :params page: The purchasing site's page to check.
        :type page: int.
        :returns: date. When this page was last scraped. None if never.
        '''

        session = self.sn()

        query = (
            session.query(ScrapeLog)
            .filter(ScrapeLog.page == page)
            .all())

        if len(query) == 0:  # No row yet for this page (total number varies)
            return None

        session.close()

        date_last_scraped = query.pop().last_scraped

        log.debug(
            'This page was last scraped %s',
            date_last_scraped.strftime('%Y-%m-%d'))

        return date_last_scraped

    def update_scrape_log(self, page):
        '''docstring'''

        session = self.sn()

        query = (
            session.query(ScrapeLog)
            .filter(ScrapeLog.page == page)
            .all())

        if len(query) == 0:  # No row yet for this page (total number varies)
            # Add this page to database
            scrape_info = ScrapeLog(page, TODAY_DATE)
            session.add(scrape_info)
            session.commit()
        else:
            # Update this page in the database
            update_query = (
                session.query(ScrapeLog)
                .filter(ScrapeLog.page == page)
                .one())

            update_query.last_scraped = TODAY_DATE
            session.commit()

        session.close()

    def _add_department_if_missing(self, department):
        '''
        Calls on a check to see if the database needs to add the department.
        If so, then calls a method to add the department to the database.

        :param department: ???
        :type department: ???
        '''

        department_exists = self._check_if_department_exists(department)

        if not department_exists:
            self._add_department(department)

    def _check_if_department_exists(self, department):
        '''
        Checks if database has this department.

        :param department: ???
        :type department: ???
        :returns: boolean. True if it exists in the database, False if not.
        '''

        session = self.sn()

        department_count = (
            session.query(Department)
            .filter(Department.name == department)
            .count())

        session.close()

        if department_count == 0:
            log.debug('Department %s is missing from database.', department)
            return False

        return True

    def _add_department(self, department):
        '''
        Add department to the local database.

        :param meta_field: The department to add to local database.
        :type meta_field: string
        '''

        log.debug('Adding department "%s" to database.', department)

        session = self.sn()

        department = Department(department)
        session.add(department)
        session.commit()

        session.close()

    def _add_vendor_if_missing(self, vendor, vendor_id_city=None):
        '''
        Calls on a check to see if the database needs to add the vendor.
        If so, then calls a method to add the vendor to the database.

        :param vendor: ???
        :type vendor: ???
        :param vendor_id_city: ???
        :type vendor_id_city: ???
        '''

        vendor_exists = self._check_if_vendor_exists(vendor)

        if not vendor_exists:
            self._add_vendor(vendor, vendor_id_city=vendor_id_city)

    def _check_if_vendor_exists(self, vendor):
        '''
        Checks if database has this vendor.

        :param vendor: The vendor to check for.
        :type vendor: string?
        :returns: boolean. True if this vendor exists in the database, \
                           False if not.
        '''

        session = self.sn()

        vendor_count = (
            session.query(Vendor)
            .filter(Vendor.name == vendor)
            .count())

        session.close()

        if vendor_count == 0:
            log.debug('Vendor "%s" is missing from database.', vendor)
            return False

        return True

    def _add_vendor(self, vendor, vendor_id_city=None):
        '''
        Add vendor to the local database.

        :param vendor: The vendor to add to our database.
        :type vendor: string
        '''

        log.debug('Adding vendor "%s" to database.', vendor)

        session = self.sn()

        vendor = Vendor(vendor, vendor_id_city)

        session.add(vendor)
        session.commit()

        session.close()

    def _get_department_id(self, department):
        '''
        Get the department's ID from our database.

        :param department: The department name.
        :type department: string
        :returns: string. The database ID for the department name.
        '''

        log.debug('Finding ID for department "%s" in database.', department)

        session = self.sn()

        department = (
            session.query(Department)
            .filter(Department.name == department)
            .first())

        department_id = department.id

        session.close()

        return department_id

    def _get_database_vendor_id(self, vendor):
        '''
        Get a vendor's ID from our database.

        :param vendor: The vendor name.
        :type vendor: string
        :returns: string. The database's vendor ID for this vendor.
        '''

        log.debug('Fetching database ID for vendor "%s".', vendor)

        session = self.sn()

        vendor = (
            session.query(Vendor)
            .filter(Vendor.name == vendor)
            .first())

        vendor_id = vendor.id

        session.close()

        return vendor_id

    def _add_contract_to_local_database(self, contract):
        '''
        Add a contract to the local database.

        :param contract: The contract to add to our database.
        :type contract: A ___ class instance.
        '''

        # # TODO: Extract piece of info rather than add entire object
        # log.debug(
        #     'Adding contract (knumber %s, purchase order %s) to database',
        #     contract.contractnumber,
        #     contract.purchaseordernumber
        # )

        session = self.sn()

        # contract_count = session.query(
        #     Contract
        # ).filter(
        #     Contract.doc_cloud_id == contract.doc_cloud_id
        # ).count()

        # # Checking for the absence of this contract, meaning this contract is
        # # not in our DB.
        # if contract_count == 0:

        session.add(contract)
        session.commit()

        session.close()

    # Refactor to take a type TODO: What does this mean? Type of officer?
    def _get_officers(self):
        '''
        Returns a list of all company officers in the database.

        :returns: list. All of the company officers in our database.
        '''

        # TODO: Test that this works correctly before using.

        session = self.sn()

        officers_query = session.query(Person.name).all()
        # TODO: need to sort (alphabetically)?

        session.close()

        officers = []

        for row in officers_query:
            officers.append(row.name)

        # return officers  # TODO: Uncomment once tested and working.

    # Not called in this class, nor elsewhere it seems.
    def _update_contract_from_document_cloud(self, document_cloud_id, fields):
        '''
        Update an existing contract in the local database.
        TODO: compare to add_contract(), because this doesn't update. It adds.

        :param document_cloud_id: The unique ID in DocumentCloud.
        :type document_cloud_id: string
        :param fields: The metadata fields to add along with the contract?
        :type fields: dict
        '''

        log.debug(
            'Updating contract in database that has DocumentCloud ID %s',
            document_cloud_id)

        session = self.sn()

        contract = (
            session.query(Contract)
            .filter(Contract.doc_cloud_id == document_cloud_id)
            .first())

        contract.contractnumber = fields['contractno']
        contract.vendorid = fields['vendor']
        contract.departmentid = fields['department']
        contract.dateadded = fields['dateadded']
        contract.title = fields['title']
        contract.purchaseordernumber = fields['purchaseno']
        contract.description = fields['description']

        session.add(contract)
        session.commit()

        session.close()

    # Not called in this class, nor elsewhere it seems.
    def _get_contract(self, purchase_order_number):
        '''
        Get a contract from the database.

        :param purchase_order_no: The unique ID in the city's website.
        :type purchase_order_no: string
        :returns: dict. A dict (?) for the matching contract.
        '''

        session = self.sn()

        query = (
            session.query(Contract)
            .filter(Contract.purchaseordernumber == purchase_order_number)
            .first())

        session.close()

        return query

    # Not called in this class, nor elsewhere it seems.
    def _get_contract_doc_cloud_id(self, document_cloud_id):
        '''
        Get a contract from the DocumentCloud project.

        :param document_cloud_id: The unique ID in the DocumentCloud project.
        :type document_cloud_id: string
        :returns: dict. A dict (?) for the matching contract.
        '''

        log.debug(
            'Find contract in database that has DocumentCloud ID %s.',
            document_cloud_id)

        session = self.sn()

        query = (
            session.query(Contract)
            .filter(Contract.doc_cloud_id == document_cloud_id)
            .first())

        session.close()

        return query

    def get_half_filled_contracts(self):
        '''
        A half-filled contract is when we know the DocumentCloud ID but don't
        know purchase order number or any of the other metadata in the city's
        purchase order system because when we upload the contract to
        DocumentCloud...

        Called on by sync_local_database_document_cloud.py.

        DocumentCloud doesn't give immediate access to all document properties.
        This pulls out the contracts in the database added during upload but
        that still need to have their details filled in.

        :returns: SQLAlchemy query result.
        '''

        log.debug('_get_half_filled_contracts')

        session = self.sn()

        query = (
            session.query(Contract)
            .filter(Contract.departmentid is None)
            .all())

        session.close()

        return query

    def update_or_add_to_archive(self, metadata):
        '''If this dict is already present, then update. If not, then add.'''

        session = self.sn()

        query = (
            session.query(Archive)
            .filter(Archive.purchase_order == metadata['purchase order'])
            .first())

        if query is not None:
            # Update
            query.access = metadata['access']
            query.canonical_url = metadata['canonical_url']
            query.contributor = metadata['contributor']
            query.contributor_organization = (
                metadata['contributor_organization'])
            query.created_at = metadata['created_at']
            query.description = metadata['description']
            query.document_cloud_id = metadata['document_cloud_id']
            query.document_title = metadata['document_title']
            query.full_text_url = metadata['full_text_url']
            query.large_image_url = metadata['large_image_url']
            query.normal_image_url = metadata['normal_image_url']
            query.number_of_pages = metadata['number_of_pages']
            query.pdf_url = metadata['pdf_url']
            query.project_id = metadata['project_id']
            query.project_title = metadata['project_title']
            query.published_url = metadata['published_url']
            query.related_article = metadata['related_article']
            query.small_image_url = metadata['small_image_url']
            query.source = metadata['source']
            query.thumbnail_image_url = metadata['thumbnail_image_url']
            query.updated_at = metadata['updated_at']

            # Custom metadata
            query.contract_number = metadata['contract number']
            query.department = metadata['department']
            query.purchase_order = metadata['purchase order']
            query.vendor = metadata['vendor']
            query.vendor_id = metadata['vendor_id']
        else:
            # Add
            a = Archive()

            a.access = metadata['access']
            a.canonical_url = metadata['canonical_url']
            a.contributor = metadata['contributor']
            a.contributor_organization = (
                metadata['contributor_organization'])
            a.created_at = metadata['created_at']
            a.description = metadata['description']
            a.document_cloud_id = metadata['document_cloud_id']
            a.document_title = metadata['document_title']
            a.full_text_url = metadata['full_text_url']
            a.large_image_url = metadata['large_image_url']
            a.normal_image_url = metadata['normal_image_url']
            a.number_of_pages = metadata['number_of_pages']
            a.pdf_url = metadata['pdf_url']
            a.project_id = metadata['project_id']
            a.project_title = metadata['project_title']
            a.published_url = metadata['published_url']
            a.related_article = metadata['related_article']
            a.small_image_url = metadata['small_image_url']
            a.source = metadata['source']
            a.thumbnail_image_url = metadata['thumbnail_image_url']
            a.updated_at = metadata['updated_at']

            # Custom metadata
            a.contract_number = metadata['contract number']
            a.department = metadata['department']
            a.purchase_order = metadata['purchase order']
            a.vendor = metadata['vendor']
            a.vendor_id = metadata['vendor_id']

            session.add(a)

        session.commit()
        session.close()

if __name__ == '__main__':
    Db().remake_db()
