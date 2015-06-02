
'''
Interacting with the DocumentCloud project.
'''

import re
from pythondocumentcloud import DocumentCloud
from contracts.lib.utilities import Utilities
from contracts import (
    DOC_CLOUD_USERNAME,
    DOC_CLOUD_PASSWORD,
    BIDS_LOCATION,
    PROJECT_URL,
    log
)


class DocumentCloudProject(object):
    '''
    Methods for interacting with the collection of contracts on DocumentCloud.
    This project is what users interact with in the app.
    '''

    def __init__(self):
        self.project_id = '1542-city-of-new-orleans-contracts'
        self.api_connection = DocumentCloud(
            DOC_CLOUD_USERNAME, DOC_CLOUD_PASSWORD)

    def check_if_need_to_upload(self, purchase_order_number):
        '''
        Checks DocumentCloud project to determine whether this contract needs
        to be uploaded.

        :param purchase_order_number: The contract's purchase order number.
        :type purchase_order_number: string.
        :returns: boolean. True if need to upload, False if don't need to.
        '''

        output = Utilities().check_that_contract_is_valid_and_public(
            purchase_order_number)

        contract_exists = self._check_if_contract_exists(
            "purchase order", purchase_order_number)
        if contract_exists:
            pass
            # log.info(
            #     '{} | {} | Not adding {} to DocumentCloud. Already up ' +
            #     'there | {}'.format(
            #         run_id, get_timestamp(),
            #         purchase_order_no, purchase_order_no
            #     )
            # )

        if output is False or contract_exists:
            return False  # Do not upload contract
        else:
            return True

    def _search_for_contract(self, key, value):
        '''
        Fetches the contract with the specified key and value from the
        DocumentCloud project.

        :param key: The key for searching through the DocumentCloud API.
        :type key: string.
        :param value: The key's value.
        :type value: string.
        :returns: A PythonDocumentCloud.Document class instance for the \
        matching contract.
        '''

        # searchterm = '\'purchase order\':' + "'" + po + "'"
        # searchterm = '\'contract number\':' + "'" + k_no + "'"

        search_term = "'" + key + "':" + "'" + value + "'"
        document = self.api_connection.documents.search(search_term).pop()

        return document

    def _check_if_contract_exists(self, key, value):
        '''
        Checks if there is a contract for this field and value in our
        DocumentCloud project.

        :param key: The key for searching through the DocumentCloud API.
        :type key: string.
        :param value: The key's value.
        :type value: string.
        :returns: boolean. True if there is a contract found, False if no \
        contract is found.
        '''

        search_term = "'" + key + "':" + "'" + value + "'"

        if len(self.api_connection.documents.search(search_term)) < 1:
            return False
        else:
            return True

    def prepare_then_add_contract(self, purchase_order_object):
        '''
        Call on method to make minor adjustments, then call on another method
        to upload the contract file and its metadata to the DocumentCloud
        project.

        :param purchase_order_object: A PurchaseOrder object instance.
        '''

        # Verify that there is at least one attachment (an actual contract?).
        number_of_attachments = len(purchase_order_object.attachments)

        if number_of_attachments > 0:
            for i, attachment in enumerate(purchase_order_object.attachments):
                bid_number = re.search(
                    '[0-9]+', attachment.get('href')).group()
                bid_file_location = BIDS_LOCATION + '/' + bid_number + ".pdf"

                purchase_order_object = self.prepare_contract(
                    purchase_order_object,
                    i
                )
                self._upload_contract(
                    bid_file_location,
                    purchase_order_object.data,
                    purchase_order_object.description,
                    purchase_order_object.title
                )

    def prepare_contract(self, purchase_order_object, iteration_value):
        '''
        Prepares to add a contract to our DocumentCloud project.

        :param purchase_order_number: A PurchaseOrder object instance.
        :returns: A modified PurchaseOrder object instance.
        '''

        number_of_attachments = len(purchase_order_object.attachments)

        # If multiple attachments, add language like "page 1 of 2":
        page_string = ""
        if number_of_attachments > 1:
            page_string = str(iteration_value + 1) + " of " + \
                str(number_of_attachments)

        # description = purchase_order_object.description + page_string
        purchase_order_object.description += page_string

        # title = purchase_order_object.title + page_string
        purchase_order_object.title += page_string

        return purchase_order_object

    def _upload_contract(self, filename, data, description, title):
        '''
        This actually uploads a contract to our DocumentCloud project.

        :param filename: The path to the downloaded contract PDF file (?).
        :type filename: string
        :param data: The contract's metadata (?).
        :type data: dict. (?)
        :param description: The contract's description.
        :type description: string.
        :param title: The contract's title.
        :type title: string.
        '''

        log.debug(filename)
        log.debug(data)
        log.debug(description)
        log.debug(title)

        # TODO: Move to another method. Also possible that this was checked
        # previously in the PurchaseOrder class.
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

        title = title.replace("/", "")  # TODO: Not sure what this does

        # new_contract = self.api_connection.documents.upload(
        self.api_connection.documents.upload(
            filename,
            title,
            'City of New Orleans',  # Source of this file
            description,
            None,  # Related article
            PROJECT_URL,  # Published URL
            'public',  # Access
            self.project_id,  # Project
            data,  # Data
            False  # Secure
        )
        # log.info('{} | {} | {} has doc_cloud_id {} | {}'.format(
        #     run_id, get_timestamp(),
        #     data['purchase order'],
        #     new_contract.id,
        #     data['purchase order']
        # ))

        # Note: Addition of this contract to LensDatabase was moved to that
        # class' ___ method.

    def _get_all_contracts(self):
        '''
        Runs a query for all of the contracts in our DocumentCloud project.

        :returns: A list of all of the project's contracts, stored as \
        PythonDocumentCloud instances.
        '''

        # TODO: parameterize this search term
        contracts = self.api_connection.documents.search(
            'projectid:%s' % self.project_id)

        return contracts

    def _get_metadata(self, document_cloud_id):
        '''
        Fetches the metadata associated with this contract on our
        DocumentCloud project.

        :param document_cloud_id: The contract's unique ID in DocumentCloud.
        :type document_cloud_id: string
        :returns: dict? The contract's metadata.
        '''

        contract = self.api_connection.documents.get(document_cloud_id)
        metadata = contract.data

        return metadata

    def _update_metadata(self, document_cloud_id, meta_key, meta_value):
        '''
        Updates the metadata associated with the contracts on DocumentCloud.

        :param document_cloud_id: The contract's unique ID in DocumentCloud.
        :type document_cloud_id: string
        :param meta_key: The specific metadata field for this contract.
        :type meta_key: string
        :param meta_value: The new metadata value for this field.
        :type meta_value: string
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
        contract = self.api_connection.documents.get(document_cloud_id)
        contract.data[meta_key] = meta_value
        contract.put()
