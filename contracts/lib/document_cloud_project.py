
"""
Represents the collection of contracts on DocumentCloud.
"""

import re
from datetime import date
from pythondocumentcloud import DocumentCloud
from contracts.db import Contract
from contracts.lib.purchase_order import PurchaseOrder
from contracts.lib.lens_repository import LensRepository
from contracts.lib.lens_database import LensDatabase
from contracts import (
    DOC_CLOUD_USERNAME,
    DOC_CLOUD_PASSWORD,
    BIDS_LOCATION
)


class DocumentCloudProject(object):
    '''
    Represents the collection of contracts on DocumentCloud.
    '''

    def __init__(self):
        doc_cloud_user = DOC_CLOUD_USERNAME
        doc_cloud_password = DOC_CLOUD_PASSWORD
        self.client = DocumentCloud(doc_cloud_user, doc_cloud_password)
        # sometimes won't need all the docs, so dont do the search on init
        self.docs = None
        self.skiplist = LensRepository().get_skip_list()

    # searchterm = '\'purchase order\':' + "'" + po + "'"
    # searchterm = '\'contract number\':' + "'" + k_no + "'"
    def get_contract(self, key, value):
        '''
        Fetches the contract with the specified field and value.

        :param field: The key for searching through the DocumentCloud API.
        :type field: string.
        :param value: The key's value.
        :type value: string.
        :returns: ???. The matching contract(s).
        '''

        searchterm = "'" + key + "':" + "'" + value + "'"
        doc = self.client.documents.search(searchterm).pop()

        return doc

    def has_contract(self, field, value):
        '''
        Checks if there is a contract for this field and value.

        :param field: The key for searching through the DocumentCloud API.
        :type field: string.
        :param value: The key's value.
        :type value: string.
        :returns: boolean. True if there is a contract found, False if not.
        '''

        searchterm = "'" + field + "':" + "'" + value + "'"

        if len(self.client.documents.search(searchterm)) < 1:
            return False  # it is a new contract

        return True  # it is an existing contract. We know the k-number

    def add_contract_to_document_cloud(self, purchase_order_number):
        '''
        Add a contract to our DocumentCloud project.

        :param purchase_order_no: The contract's unique ID in DocumentCloud.
        :type purchase_order_no: string.
        :returns: ???
        '''

        purchase_order_regex = re.compile(r'[A-Z]{2}\d+')
        # log.info(
        #     '{} | {} | Attempting to add {} to DocumentCloud | {}'.format(
        #         run_id, get_timestamp(), purchase_order_no, purchase_order_no
        #     )
        # )
        if not purchase_order_regex.match(purchase_order_number):
            # log.info(
            #     "{} doesn't look like a valid purchase order. " +
            #     "Skipping for now".format(purchase_order_no)
            # )
            return
        if purchase_order_number in self.skiplist:
            # log.info(
            #     '{} | {} | Not adding {} to DocumentCloud. In skiplist ' +
            #     '| {}'.format(
            #         run_id, get_timestamp(), purchase_order_no,
            #         purchase_order_no
            #     )
            # )
            return
        if not self.has_contract("purchase order", purchase_order_number):
            try:
                purchase_order = PurchaseOrder(purchase_order_number)
            except IndexError:
                # log.info(
                #     '{} | {} | Something looks wrong with the format on ' +
                #     'this one. Skipping for now | {}'.format(
                #         run_id, get_timestamp(),
                #         purchase_order_no, purchase_order_no
                #     )
                # )
                return
            # log.info(
            #     '{} | {} | Adding {} to DocumentCloud | {}'.format(
            #         run_id, get_timestamp(),
            #         purchase_order_no, purchase_order_no
            #     )
            # )

            # Checks if there is at least one attachment. Some don't have any.
            if len(purchase_order.attachments) > 0:
                counter = 1
                for attachment in purchase_order.attachments:
                    # Loop through each attachment

                    bidnumber = re.search(
                        '[0-9]+', attachment.get('href')).group()
                    bid_file_location = BIDS_LOCATION + \
                        bidnumber + ".pdf"
                    extra_string = ""
                    if counter > 1:
                        extra_string = str(counter) + " of " + \
                            str(len(purchase_order.attachments))
                    temp = purchase_order.description + extra_string
                    self.upload_contract(
                        bid_file_location,
                        purchase_order.data,
                        temp,
                        purchase_order.title + extra_string
                    )
                    counter += 1
        else:
            pass
            # log.info(
            #     '{} | {} | Not adding {} to DocumentCloud. Already up ' +
            #     'there | {}'.format(
            #         run_id, get_timestamp(),
            #         purchase_order_no, purchase_order_no
            #     )
            # )

    def get_all_docs(self):
        '''
        Runs a query for all of the contracts in our DocumentCloud project.

        :returns: list. A list of all of the project's contracts.
        '''

        if self.docs is None:
            self.docs = self.client.documents.search(
                'projectid: 1542-city-of-new-orleans-contracts')

        return self.docs

    def upload_contract(self, fname, data, description, title):
        '''
        This uploads a contract onto DocumentCloud.
        It also adds this contract to the Lens database.

        :param file: The contract PDF file?
        :type file: PDF
        :param data: The contract's (metadata).
        :type data: dict. ???
        :param description: The contract's description.
        :type description: string.
        :param title: The contract's title.
        :type title: string.
        :returns: ???
        '''

        if len(data['contract number']) < 1:
            # log.info(
            #     '{} | {} | Not adding {} to DocumentCloud. '
            #     'Contract number {} is null | {}'.format(
            #         run_id, get_timestamp(),
            #         data['purchase order'],
            #         data['contract number'],
            #         data['purchase order']
            #     )
            # )
            return  # do not upload. There is a problem

        title = title.replace("/", "")
        newcontract = self.client.documents.upload(
            fname,
            title,
            'City of New Orleans',
            description,
            None,
            'http://vault.thelensnola.org/contracts',
            'public',
            '1542-city-of-new-orleans-contracts',
            data,
            False
        )
        # log.info('{} | {} | {} has doc_cloud_id {} | {}'.format(
        #     run_id, get_timestamp(),
        #     data['purchase order'],
        #     newcontract.id,
        #     data['purchase order']
        # ))
        contract = Contract()

        # TODO: "Instance of 'Document' has no 'id' member":
        contract.doc_cloud_id = newcontract.id
        with LensDatabase() as db:
            contract.contractnumber = data['contract number']
            contract.purchaseordernumber = data['purchase order']
            contract.description = description
            contract.title = title
            contract.dateadded = date.today()

            with LensDatabase() as lens_db:
                lens_db.add_department(data['department'])
                lens_db.add_vendor(
                    data['vendor'],
                    vendor_id_city=data['vendor_id'])

                contract.departmentid = lens_db.get_department_id(
                    data['department'])
                contract.vendorid = lens_db.get_lens_vendor_id(data['vendor'])

            db.add_contract_to_lens_database(contract)

    def get_metadata(self, doc_cloud_id, meta_field):
        '''
        Fetches the metadata associated with a contract on DocumentCloud.
        Needs to get for departments and vendors, then uppercase them and
        then update them in DC.

        :param doc_cloud_id: The contract's unique ID in DocumentCloud.
        :type doc_cloud_id: string
        :param meta_field: The specific metadata field for this contract.
        :type meta_field: string
        :returns: ???
        '''

        contract = self.client.documents.get(doc_cloud_id)
        # contract.data[meta_field] = new_meta_data_value
        # contract.put()

        return contract

    def update_metadata(self, doc_cloud_id, meta_field, new_meta_data_value):
        '''
        Updates the metadata associated with the contracts on DocumentCloud.

        :param doc_cloud_id: The contract's unique ID in DocumentCloud.
        :type doc_cloud_id: string
        :param meta_field: The specific metadata field for this contract.
        :type meta_field: string
        :param new_meta_data_value: The new metadata value for this field.
        :type new_meta_data_value: string
        '''

        # log.info(
        #     '{} | {} | updating {} on DocumentCloud. ' +
        #     'Changing {} to {}'.format(
        #         run_id,
        #         get_timestamp(),
        #         doc_cloud_id,
        #         meta_field,
        #         new_meta_data_value
        #     )
        # )
        contract = self.client.documents.get(doc_cloud_id)
        contract.data[meta_field] = new_meta_data_value
        contract.put()
