# -*- coding: utf-8 -*-

"""Represent the local database that tracks contracts."""

from datetime import date, timedelta
from sqlalchemy import desc
from contracts.db import (
    Vendor,
    Contract,
    Person,
    Department,
    VendorOfficer,
    ScrapeLog
)
from contracts import SESSION, TODAY_DATE, log


class LensDatabase(object):
    """Represent the local database that stores contracts information."""

    def __init__(self):
        """TODO."""
        pass

    def check_if_database_has_contract(self, purchase_order_number):
        """
        Check if local database already has this contract.

        :param purchase_order_number: The unique ID in the city's website.
        :type purchase_order_number: string
        :returns: boolean. True if the contract is present, False if not.
        """
        query_count = SESSION.query(
            Contract
        ).filter(
            Contract.purchaseordernumber == purchase_order_number
        ).count()

        SESSION.close()

        if query_count == 1:  # Database has the contract
            log.debug(
                'Database already has purchase order %s in contracts table',
                purchase_order_number)
            return True
        else:
            return False

    def add_to_database(self, purchase_order_object):
        """
        Add this contract to the local database.

        Initialize a Contract object class instance and fill out with the
        relevant information.

        :param purchase_order_object: The PurchaseOrder object instance.
        :type purchase_order_object: A PurchaseOrder object instance.
        """
        log.debug(
            "Adding purchase order %s to contracts table",
            purchase_order_object.purchase_order_number)

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

    def get_daily_contracts(self):
        """
        Get today's contracts (and the vendors).

        Not called on by this class, but is called on by emailer.py.

        :returns: A list of dicts (?) for the daily contracts.
        """
        contracts = SESSION.query(
            Contract.doc_cloud_id,
            Vendor.name
        ).filter(
            Contract.dateadded == TODAY_DATE
        ).filter(
            Contract.vendorid == Vendor.id
        ).all()

        SESSION.close()

        return contracts

    def get_all_contract_ids(self):
        """
        Fetch a list of all of the contract IDs in our DocumentCloud project.

        Not called on by this class, but is called on by backup.py.

        :returns: list. A list of all IDs in our DocumentCloud project.
        """
        query = SESSION.query(
            Contract.doc_cloud_id
        ).order_by(
            desc(Contract.dateadded)
        ).all()

        SESSION.close()

        document_ids = []

        for row in query:
            document_ids.append(row[0])

        return document_ids

    def get_people_associated_with_vendor(self, name):
        """
        Get a list of people associated with the vendor.

        Not called on by this class, but is called on by emailer.py.

        :param name: The vendor name.
        :type name: string
        :returns: list. The people who are associated with this vendor (how?).
        """
        query_people = SESSION.query(
            Person.name
        ).filter(
            Vendor.id == VendorOfficer.vendorid
        ).filter(
            Person.id == VendorOfficer.personid
        ).filter(
            Vendor.name == name
        ).all()

        SESSION.close()

        people = []

        log.debug('%d people associated with %s', len(query_people), name)

        for row in query_people:
            people.append(str(row[0]))

        return people

    def check_if_need_to_scrape(self, page):
        """
        If page is <= 10 and last scrape was before today, scrape it.

        If page is > 10 and last scrape was more than seven days ago, scrape.

        :params page: The purchasing site page number to check.
        :type page: int.
        :returns: boolean. True if need to scrape, False if not.
        """
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
                    'Skipping page %d because it was scraped recently', page)

                return False
        elif page > 10:
            if date_last_scraped < week_ago_date:
                return True  # Scrape this page
            else:
                log.debug(
                    'Skipping page %d because it was scraped recently', page)

                return False

    def _check_when_last_scraped(self, page):
        """
        Look up this page in scrape_log table to see when it was last scraped.

        :params page: The purchasing site's page to check.
        :type page: int.
        :returns: date. When this page was last scraped. None if never.
        """
        query = SESSION.query(
            ScrapeLog
        ).filter(
            ScrapeLog.page == page
        ).all()

        if len(query) == 0:  # No row yet for this page (total number varies)
            return None

        SESSION.close()

        # for row in query:
        date_last_scraped = query.pop().last_scraped

        log.debug(
            'This page was last scraped %s',
            date_last_scraped.strftime('%Y-%m-%d'))

        return date_last_scraped

    def update_scrape_log(self, page):
        """TODO."""
        query = SESSION.query(
            ScrapeLog
        ).filter(
            ScrapeLog.page == page
        ).all()

        if len(query) == 0:  # No row yet for this page (total number varies)
            # Add this page to database
            scrape_info = ScrapeLog(page, TODAY_DATE)
            SESSION.add(scrape_info)
            SESSION.commit()
        else:
            # Update this page in the database
            update_query = SESSION.query(
                ScrapeLog
            ).filter(
                ScrapeLog.page == page
            ).one()

            update_query.last_scraped = TODAY_DATE
            SESSION.commit()

    def _add_department_if_missing(self, department):
        """
        Call on a check to see if the database needs to add the department.

        If so, then calls a method to add the department to the database.

        :param department: ???
        :type department: ???
        """
        department_exists = self._check_if_department_exists(department)
        if department_exists is False:
            self._add_department(department)

    def _check_if_department_exists(self, department):
        """
        Check if database has this department.

        :param department: ???
        :type department: ???
        :returns: boolean. True if it exists in the database, False if not.
        """
        department_count = SESSION.query(
            Department
        ).filter(
            Department.name == department
        ).count()

        SESSION.close()

        if department_count == 0:
            log.debug('Department "%s" is missing from database', department)
            return False
        else:
            return True

    def _add_department(self, department):
        """
        Add department to the local database.

        :param meta_field: The department to add to local database.
        :type meta_field: string
        """
        log.debug('Adding department "%s" to database', department)

        department = Department(department)
        SESSION.add(department)
        SESSION.commit()

    def _add_vendor_if_missing(self, vendor, vendor_id_city=None):
        """
        Call on a check to see if the database needs to add the vendor.

        If so, then calls a method to add the vendor to the database.

        :param vendor: ???
        :type vendor: ???
        :param vendor_id_city: ???
        :type vendor_id_city: ???
        """
        vendor_exists = self._check_if_vendor_exists(vendor)

        if not vendor_exists:
            self._add_vendor(vendor, vendor_id_city=vendor_id_city)

    def _check_if_vendor_exists(self, vendor):
        """
        Check if database has this vendor.

        :param vendor: The vendor to check for.
        :type vendor: string?
        :returns: boolean. True if vendor exists in database, False if not.
        """
        vendor_count = SESSION.query(
            Vendor
        ).filter(
            Vendor.name == vendor
        ).count()

        SESSION.close()

        if vendor_count == 0:
            log.debug('Vendor "%s" is missing from database', vendor)
            return False
        else:
            return True

    def _add_vendor(self, vendor, vendor_id_city=None):
        """
        Add vendor to the local database.

        :param vendor: The vendor to add to our database.
        :type vendor: string
        """
        log.debug('Adding vendor "%s" to database', vendor)

        vendor = Vendor(vendor, vendor_id_city)

        SESSION.add(vendor)
        SESSION.commit()

    def _get_department_id(self, department):
        """
        Get the department's ID from our database.

        :param department: The department name.
        :type department: string
        :returns: string. The database ID for the department name.
        """
        log.debug('Finding ID for department "%s" in database', department)

        department = SESSION.query(
            Department
        ).filter(
            Department.name == department
        ).first()

        department_id = department.id

        SESSION.close()

        return department_id

    def _get_database_vendor_id(self, vendor):
        """
        Get a vendor's ID from our database.

        :param vendor: The vendor name.
        :type vendor: string
        :returns: string. The database's vendor ID for this vendor.
        """
        log.debug('Fetching database ID for vendor "%s"', vendor)

        vendor = SESSION.query(
            Vendor
        ).filter(
            Vendor.name == vendor
        ).first()

        vendor_id = vendor.id

        SESSION.close()

        return vendor_id

    def _add_contract_to_local_database(self, contract):
        """
        Add a contract to the local database.

        :param contract: The contract to add to our database.
        :type contract: A ___ class instance.
        """
        # # TODO: Extract piece of info rather than add entire object
        # log.debug(
        #     'Adding contract (knumber %s, purchase order %s) to database',
        #     contract.contractnumber,
        #     contract.purchaseordernumber
        # )

        # contract_count = session.query(
        #     Contract
        # ).filter(
        #     Contract.doc_cloud_id == contract.doc_cloud_id
        # ).count()

        # # Checking for the absence of this contract, meaning this contract is
        # # not in our DB.
        # if contract_count == 0:

        SESSION.add(contract)
        SESSION.commit()

    # Refactor to take a type TODO: What does this mean? Type of officer?
    def _get_officers(self):
        """
        Return a list of all company officers in the database.

        :returns: list. All of the company officers in our database.
        """
        # TODO: Test that this works correctly before using.

        officers_query = SESSION.query(
            Person.name
        ).all()
        # TODO: need to sort (alphabetically)?

        SESSION.close()

        officers = []

        for row in officers_query:
            officers.append(row.name)

        # return officers  # TODO: Uncomment once tested and working.

    # Not called in this class, nor elsewhere it seems.
    def _update_contract_from_document_cloud(self, document_cloud_id, fields):
        """
        Update an existing contract in the local database.

        TODO: compare to add_contract(), because this doesn't update. It adds.

        :param document_cloud_id: The unique ID in DocumentCloud.
        :type document_cloud_id: string
        :param fields: The metadata fields to add along with the contract?
        :type fields: dict
        """
        log.debug(
            'Updating contract in database that has DocumentCloud ID %s',
            document_cloud_id
        )

        contract = SESSION.query(
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

        SESSION.add(contract)
        SESSION.commit()

    # Not called in this class, nor elsewhere it seems.
    def _get_contract(self, purchase_order_number):
        """
        Get a contract from the database.

        :param purchase_order_no: The unique ID in the city's website.
        :type purchase_order_no: string
        :returns: dict. A dict (?) for the matching contract.
        """
        query = SESSION.query(
            Contract
        ).filter(
            Contract.purchaseordernumber == purchase_order_number
        ).first()

        SESSION.close()

        return query

    # Not called in this class, nor elsewhere it seems.
    def _get_contract_doc_cloud_id(self, document_cloud_id):
        """
        Get a contract from the DocumentCloud project.

        :param document_cloud_id: The unique ID in the DocumentCloud project.
        :type document_cloud_id: string
        :returns: dict. A dict (?) for the matching contract.
        """
        log.debug(
            'Find contract in database that has DocumentCloud ID %s',
            document_cloud_id
        )

        query = SESSION.query(
            Contract
        ).filter(
            Contract.doc_cloud_id == document_cloud_id
        ).first()

        SESSION.close()

        return query

    def get_half_filled_contracts(self):
        """
        A half-filled contract is when we know the DocumentCloud ID but don't
        know purchase order number or any of the other metadata in the city's
        purchase order system because when we upload the contract to
        DocumentCloud...

        Called on by sync_local_database_document_cloud.py.

        DocumentCloud doesn't give immediate access to all document properties.
        This pulls out the contracts in the database added during upload but
        that still need to have their details filled in.

        :returns: SQLAlchemy query result.
        """
        query = SESSION.query(
            Contract
        ).filter(
            Contract.departmentid is None
        ).all()

        SESSION.close()

        return query
