
'''
Represents the Lens database that tracks contracts.
'''

from datetime import datetime, date
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
    Represents the local database that stores contracts information.
    '''

    def __init__(self):
        engine = create_engine(CONNECTION_STRING)
        self.sn = sessionmaker(bind=engine)

    # refactor to take a type
    def get_officers(self):
        '''
        Returns a list of all company officers in the database.

        :returns: list. All of the company officers in our database.
        '''

        # TODO: add SQL Alchemy logic to get officers

        pass

    def add_vendor_if_missing(self, vendor, vendor_id_city=None):
        '''
        Calls on a check to see if the database needs to add the vendor.
        If so, then calls a method to add the vendor to the database.

        :param vendor: ???
        :type vendor: ???
        :param vendor_id_city: ???
        :type vendor_id_city: ???
        '''

        vendor_exists = self.check_if_vendor_exists(vendor)
        if vendor_exists is False:
            self.add_vendor(vendor, vendor_id_city)

    def check_if_vendor_exists(self, vendor):
        '''
        Checks if database has this department.

        :param department: ???
        :type department: ???
        :returns: boolean. True if it exists in the database, False if not.
        '''

        session = self.sn()

        vendor_count = session.query(
            Vendor
        ).filter(
            Vendor.name == vendor
        ).count()

        session.close()

        if vendor_count == 0:
            return False
        else:
            return True

    # refactor to take a type
    def add_vendor(self, vendor, vendor_id_city=None):
        '''
        Add vendor to the Lens database.

        :param vendor: The vendor to add to our database.
        :type vendor: string
        '''

        session = self.sn()

        vendor = Vendor(vendor)
        vendor.vendor_id_city = vendor_id_city

        session.add(vendor)
        session.commit()

        session.close()

    def check_if_department_exists(self, department):
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
            return False
        else:
            return True

    def add_department_if_missing(self, department):
        '''
        Calls on a check to see if the database needs to add the department.
        If so, then calls a method to add the department to the database.

        :param department: ???
        :type department: ???
        '''

        department_exists = self.check_if_department_exists(department)
        if department_exists is False:
            self.add_department(department)

    def add_department(self, department):
        '''
        Add department to the local database.

        :param meta_field: The department to add to local database.
        :type meta_field: string
        '''

        session = self.sn()

        department = Department(department)
        session.add(department)
        session.commit()

        session.close()

    def add_contract_to_local_database(self, contract):
        '''
        Add a contract to the local database.

        :param contract: The contract to add to our database.
        :type contract: A ___ class instance.
        '''

        session = self.sn()

        contract_count = session.query(
            Contract
        ).filter(
            Contract.doc_cloud_id == contract.doc_cloud_id
        ).count()

        # Checking for the absence of this contract, meaning this contract is
        # not in our DB.
        if contract_count == 0:
            session.add(contract)
            session.commit()

        session.close()

    def get_all_contract_ids(self):
        '''
        Fetches a list of all of the contract IDs in our DocumentCloud project.

        :returns: list. A list of all IDs in our DocumentCloud project.
        '''

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

    def update_contract_from_document_cloud(self, document_cloud_id, fields):
        '''
        Update an existing contract in the Lens database.
        TODO: compare to add_contract(), because this doesn't update. It adds.

        :param document_cloud_id: The unique ID in DocumentCloud.
        :type document_cloud_id: string
        :param fields: The metadata fields to add along with the contract?
        :type fields: dict
        '''

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

    def has_contract(self, purchase_order_number):
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

        if query_count == 1:
            return True
        else:
            return False

    def get_contract(self, purchase_order_number):
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

    def get_contract_doc_cloud_id(self, document_cloud_id):
        '''
        Get a contract from the DocumentCloud project.

        :param document_cloud_id: The unique ID in the DocumentCloud project.
        :type document_cloud_id: string
        :returns: dict. A dict (?) for the matching contract.
        '''

        session = self.sn()

        query = session.query(
            Contract
        ).filter(
            Contract.doc_cloud_id == document_cloud_id
        ).first()

        session.close()

        return query

    def get_lens_vendor_id(self, vendor):
        '''
        Get a vendor's ID from our database.
        TODO: refactor

        :param vendor: The vendor.
        :type vendor: string
        :returns: string. The ID for the vendor.
        '''

        # self.session.flush()
        session = self.sn()

        vendor = session.query(
            Vendor
        ).filter(
            Vendor.name == vendor
        ).first()

        vendor_id = vendor.id

        session.close()

        return vendor_id

    def get_department_id(self, department):
        '''
        Get the department's ID from our database.
        TODO: refactor

        :param department: The department.
        :type department: string
        :returns: string. The ID for the department.
        '''

        session = self.sn()

        department_id = session.query(
            Department
        ).filter(
            Department.name == department
        ).first().id

        session.close()

        return department_id

    def get_half_filled_contracts(self):
        '''
        A half-filled contract is where we know DC ID but don't know PO number
        or any of the other metadata in the city's PO system because when we
        upload the contract to DC...

        DocumentCloud doesn't give immediate access to all document properties.
        This pulls out the contracts in the database added during upload but
        that still need to have their details filled in.

        :returns: SQLAlchemy query result.
        '''

        session = self.sn()

        query = session.query(
            Contract
        ).filter(
            Contract.departmentid is None
        ).all()

        session.close()

        return query

    def get_daily_contracts(self):  # defaults to today
        '''
        Get today's contracts (and the vendors) for the daily email.

        :returns: A list of dicts (?) for the daily contracts.
        '''

        today_string = datetime.today().strftime('%Y-%m-%d')

        session = self.sn()

        contracts = session.query(
            Contract.doc_cloud_id,
            Vendor.name
        ).filter(
            Contract.dateadded == today_string
        ).filter(
            Contract.vendorid == Vendor.id
        ).all()

        session.close()

        return contracts

    def get_people_associated_with_vendor(self, name):
        '''
        Get a list of people associated with the vendor.

        :param name: The vendor name.
        :type name: string
        :returns: list. The people who are associated with this vendor.
        '''

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

    def get_state_contributions(self, name):
        '''
        Find the state contributions for this contributor.

        :param name: The name.
        :type name: string
        :returns: list. The contributions associated with this name.
        '''

        session = self.sn()

        contributions = session.query(
            EthicsRecord
        ).filter(
            EthicsRecord.contributorname == name
        ).all()

        contributions.sort(key=lambda x: dateutil.parser.parse(x.receiptdate))

        session.close()

        return contributions

    def add_to_database(self, purchase_order_object):
        '''
        This was moved out from DocumentCloudProject since this has nothing to
        do with DocumentCloud.

        :param purchase_order_number: The contract to add.
        :type purchase_order_number: string.
        '''

        # contract = Contract()

        # # TODO: "Instance of 'Document' has no 'id' member":
        # contract.doc_cloud_id = new_contract.id

        # with LensDatabase() as database:
        #     contract.contractnumber = data['contract number']
        #     contract.purchaseordernumber = data['purchase order']
        #     contract.description = description
        #     contract.title = title
        #     contract.dateadded = date.today()

        #     with LensDatabase() as lens_db:
        #         lens_db.add_department(data['department'])
        #         lens_db.add_vendor(
        #             data['vendor'],
        #             vendor_id_city=data['vendor_id'])

        #         contract.departmentid = lens_db.get_department_id(
        #             data['department'])
        #         contract.vendorid = lens_db.get_lens_vendor_id(
        #             data['vendor'])

        #     database.add_contract_to_local_database(contract)

        session = self.sn()

        contract = Contract()

        # TODO: "Instance of 'Document' had no 'id' member". Might need to
        # have a follow-up method that pulls from DocumentCloud project and
        # inserts its ID into this row in the database.
        # contract.doc_cloud_id = new_contract.id

        contract.contractnumber = purchase_order_object.k_number
        contract.purchaseordernumber = purchase_order_object.purchaseorder
        contract.description = purchase_order_object.description
        contract.title = purchase_order_object.title
        contract.dateadded = date.today()

        self.add_department_if_missing(purchase_order_object.department)
        self.add_vendor_if_missing(
            purchase_order_object.vendor_name,
            purchase_order_object.vendor_id_city
        )

        contract.departmentid = self.get_department_id(
            purchase_order_object.department)
        contract.vendorid = self.get_lens_vendor_id(
            purchase_order_object.vendor_name)

        self.add_contract_to_local_database(contract)

        session.close()
