# -*- coding: utf-8 -*-

'''
Represents the local database that tracks contracts.
'''

from datetime import date, timedelta
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker

from contracts.db import (
    Vendor,
    Contract,
    Person,
    Department,
    VendorOfficer,
    ScrapeLog
)
from contracts import CONNECTION_STRING, TODAY_DATE, log

# Emoji
red_stop = "\xF0\x9F\x9A\xAB"
green_check = "\xE2\x9C\x85"


class LensDatabase(object):
    '''
    Represents the local database that stores contracts information.
    '''

    def __init__(self):
        engine = create_engine(CONNECTION_STRING)
        self.sn = sessionmaker(bind=engine)

    def check_if_database_has_contract(self, purchase_order_number):
        '''
        Checks if local database already has this contract.

        :param purchase_order_number: The unique ID in the city's website.
        :type purchase_order_number: string
        :returns: boolean. True if the contract is present, False if not.
        '''

        session = self.sn()

        query_count = session.query(
            Contract
        ).filter(
            Contract.purchaseordernumber == purchase_order_number
        ).count()

        session.close()

        if query_count == 1:  # Database has the contract
            print (
                '%s  Database already has purchase ' % (red_stop) +
                'order %s in contracts table.' % purchase_order_number)
            log.debug(
                '%s  ' % (red_stop) +
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

        print (
            "%s  " % (green_check) +
            "Adding purchase order %s to database's contracts table..." % (
                purchase_order_object.purchase_order_number))
        log.debug(
            "%s  " % (green_check) +
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
            vendor_id_city=purchase_order_object.vendor_id_city
        )

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

        contracts = session.query(
            Contract.doc_cloud_id,
            Vendor.name
        ).filter(
            Contract.dateadded == TODAY_DATE
        ).filter(
            Contract.vendorid == Vendor.id
        ).all()

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

        query = session.query(
            Contract.doc_cloud_id
        ).order_by(
            desc(Contract.dateadded)
        ).all()

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

        query_people = session.query(
            Person.name
        ).filter(
            Vendor.id == VendorOfficer.vendorid
        ).filter(
            Person.id == VendorOfficer.personid
        ).filter(
            Vendor.name == name
        ).all()

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
                log.debug(
                    'Page %d has been scraped recently. Skipping.',
                    page)
                print (
                    'Page %d has been scraped recently. Skipping.' % page)

                return False
        elif page > 10:
            if date_last_scraped < week_ago_date:
                return True  # Scrape this page
            else:
                log.debug(
                    'Page %d has been scraped recently. Skipping.',
                    page)
                print (
                    'Page %d has been scraped recently. Skipping.' % page)

                return False

    def _check_when_last_scraped(self, page):
        '''
        Looks up this page in scrape_log table to see when it was last scraped.

        :params page: The purchasing site's page to check.
        :type page: int.
        :returns: date. When this page was last scraped. None if never.
        '''

        session = self.sn()

        query = session.query(
            ScrapeLog
        ).filter(
            ScrapeLog.page == page
        ).all()

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

        query = session.query(
            ScrapeLog
        ).filter(
            ScrapeLog.page == page
        ).all()

        if len(query) == 0:  # No row yet for this page (total number varies)
            # Add this page to database
            scrape_info = ScrapeLog(page, TODAY_DATE)
            session.add(scrape_info)
            session.commit()
        else:
            # Update this page in the database
            update_query = session.query(
                ScrapeLog
            ).filter(
                ScrapeLog.page == page
            ).one()

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

        department_count = session.query(
            Department
        ).filter(
            Department.name == department
        ).count()

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

        vendor_count = session.query(
            Vendor
        ).filter(
            Vendor.name == vendor
        ).count()

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

        department = session.query(
            Department
        ).filter(
            Department.name == department
        ).first()

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

        vendor = session.query(
            Vendor
        ).filter(
            Vendor.name == vendor
        ).first()

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

        officers_query = session.query(
            Person.name
        ).all()
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
            document_cloud_id
        )

        session = self.sn()

        contract = session.query(
            Contract
        ).filter(
            Contract.doc_cloud_id == document_cloud_id
        ).first()

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

        query = session.query(
            Contract
        ).filter(
            Contract.purchaseordernumber == purchase_order_number
        ).first()

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

        query = session.query(
            Contract
        ).filter(
            Contract.doc_cloud_id == document_cloud_id
        ).first()

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

        query = session.query(
            Contract
        ).filter(
            Contract.departmentid is None
        ).all()

        session.close()

        return query
