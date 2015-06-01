
"""
Represents the Lens database that tracks contracts.
"""

from datetime import datetime
import dateutil
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker
from contracts.db import (
    Vendor,
    Contract,
    Person,
    Department,
    VendorOfficer,
    EthicsRecord
)
from contracts import CONNECTION_STRING


class LensDatabase(object):
    '''
    Represents the Lens database that tracks contracts.
    '''

    def __init__(self):
        engine = create_engine(CONNECTION_STRING)
        sn = sessionmaker(bind=engine)
        self.session = sn()

    def __enter__(self):
        '''
        This gets called when you do with LensDatabase() as db:"
        '''

        return self

    # refactor to take a type
    def get_officers(self):
        """
        Returns a list of all company officers in the database

        :returns: ???
        """

        pass
        # to do Tom Thoren

    # refactor to take a type
    def add_vendor(self, vendor, vendor_id_city=None):
        """
        Add vendor to the Lens database.

        :param vendor: The vendor to add to our database.
        :type vendor: string
        """

        indb = self.session.query(
            Vendor
        ).filter(
            Vendor.name == vendor
        ).count()
        if indb == 0:
            vendor = Vendor(vendor)
            vendor.vendor_id_city = vendor_id_city
            self.session.add(vendor)
            self.session.commit()

    def add_department(self, department):
        """
        Add department to the Lens database.

        :param meta_field: The department to add to our database.
        :type meta_field: string
        """

        indb = self.session.query(
            Department
        ).filter(
            Department.name == department
        ).count()

        if indb == 0:
            department = Department(department)
            self.session.add(department)
            self.session.commit()

    def add_contract_to_lens_database(self, contract):
        """
        Add a contract to the Lens database.

        :param meta_field: The contract to add to our database.
        :type meta_field: string
        """

        indb = self.session.query(
            Contract
        ).filter(
            Contract.doc_cloud_id == contract.doc_cloud_id
        ).count()

        # Checking for the absence of this contract, meaning this contract is
        # not in our DB.
        if indb == 0:
            self.session.add(contract)
            self.session.flush()
            self.session.commit()

    def get_all_contract_ids(self):
        '''
        Fetches a list of all of the contract IDs in DocumentCloud project.

        :returns: list. A list of all IDs in DocumentCloud project.
        '''

        doc_id_query = self.session.query(
            Contract.doc_cloud_id
        ).order_by(
            desc(Contract.dateadded)
        ).all()

        dcids = [i[0] for i in doc_id_query]

        return dcids

    def update_contract_from_doc_cloud_doc(self, doc_cloud_id, fields):
        """
        Update an existing contract in the Lens database.
        TODO: compare to add_contract()

        :param doc_cloud_id: The unique ID in DocumentCloud.
        :type doc_cloud_id: string
        :param fields: The metadata fields to add along with the contract?
        :type fields: dict
        """

        contract = self.session.query(
            Contract
        ).filter(
            Contract.doc_cloud_id == doc_cloud_id
        ).first()

        contract.contractnumber = fields['contractno']
        contract.vendorid = fields['vendor']
        contract.departmentid = fields['department']
        contract.dateadded = fields['dateadded']
        contract.title = fields['title']
        contract.purchaseordernumber = fields['purchaseno']
        contract.description = fields['description']
        self.session.add(contract)
        self.session.flush()
        self.session.commit()

    def has_contract(self, purchase_order_no):
        """
        Checks if the database (?) already has this contract.

        :param purchase_order_no: The unique ID in the city's website.
        :type purchase_order_no: string
        :returns: boolean. True if the contract is present, False if not.
        """

        indb = self.session.query(
            Contract
        ).filter(
            Contract.purchaseordernumber == purchase_order_no
        ).count()

        if indb == 1:
            return True
        else:
            return False

    def get_contract(self, purchase_order_no):
        """
        Get a contract from the database.

        :param purchase_order_no: The unique ID in the city's website.
        :type purchase_order_no: string
        :returns: dict. A dict (?) for the matching contract.
        """

        query = self.session.query(
            Contract
        ).filter(
            Contract.purchaseordernumber == purchase_order_no
        ).first()

        return query

    def get_contract_doc_cloud_id(self, doc_cloud_id):
        """
        Get a contract from the DocumentCloud project.

        :param doc_cloud_id: The unique ID in the DocumentCloud project.
        :type doc_cloud_id: string
        :returns: dict. A dict (?) for the matching contract.
        """

        query = self.session.query(
            Contract
        ).filter(
            Contract.doc_cloud_id == doc_cloud_id
        ).first()

        return query

    def get_lens_vendor_id(self, vendor):
        """
        Get a vendor's ID from our database.
        TODO: refactor

        :param vendor: The vendor.
        :type vendor: string
        :returns: string. The ID for the vendor.
        """

        self.session.flush()

        vendor = self.session.query(
            Vendor
        ).filter(
            Vendor.name == vendor
        ).first()

        return vendor.id

    def get_department_id(self, department):
        """
        Get the department's ID from our database.
        TODO: refactor

        :param department: The department.
        :type department: string
        :returns: string. The ID for the department.
        """

        department_id = self.session.query(
            Department
        ).filter(
            Department.name == department
        ).first().id

        return department_id

    def get_half_filled_contracts(self):
        """
        A half-filled contract is where we know DC ID but don't know PO number
        or any of the other metadata in the city's PO system because when we
        upload the contract to DC...

        DocumentCloud doesn't give immediate access to all document properties.
        This pulls out the contracts in the database added during upload but
        that still need to have their details filled in.

        :returns: SQLAlchemy query result.
        """

        query = self.session.query(
            Contract
        ).filter(
            Contract.departmentid is None
        ).all()

        return query

    def get_daily_contracts(self):  # defaults to today
        """
        Get today's contracts (and the vendors) for the daily email.

        :returns: A list of dicts (?) for the daily contracts.
        """

        today_string = datetime.today().strftime('%Y-%m-%d')

        contracts = self.session.query(
            Contract.doc_cloud_id,
            Vendor.name
        ).filter(
            Contract.dateadded == today_string
        ).filter(
            Contract.vendorid == Vendor.id
        ).all()

        return contracts

    def get_people_associated_with_vendor(self, name):
        """
        Get a list of people associated with the vendor.

        :param name: The vendor name.
        :type name: string
        :returns: list. The people who are associated with this vendor.
        """

        recccs = self.session.query(
            Person.name
        ).filter(
            Vendor.id == VendorOfficer.vendorid
        ).filter(
            Person.id == VendorOfficer.personid
        ).filter(
            Vendor.name == name
        ).all()

        return [str(i[0]) for i in recccs]

    def get_state_contributions(self, name):
        '''
        Find the state contributions for this contributor.

        :param name: The name.
        :type name: string
        :returns: list. The contributions associated with this name.
        '''

        recccs = self.session.query(
            EthicsRecord
        ).filter(
            EthicsRecord.contributorname == name
        ).all()

        recccs.sort(key=lambda x: dateutil.parser.parse(x.receiptdate))

        return recccs

    def __exit__(self, type, value, traceback):
        """
        Called when the database is closed.
        """

        self.session.close()
