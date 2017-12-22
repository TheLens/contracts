# -*- coding: utf-8 -*-

'''
Interacting with the DocumentCloud project.
'''

import re
from pythondocumentcloud import DocumentCloud
from contracts.lib.utilities import Utilities
from contracts import (
    DOC_CLOUD_USERNAME,
    DOC_CLOUD_PASSWORD,
    DOCUMENTS_DIR,
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

        validity = Utilities().check_that_contract_is_valid_and_public(
            purchase_order_number)

        contract_exists = self._check_if_document_cloud_has_contract(
            "purchase order", purchase_order_number)

        if validity is False or contract_exists:
            log.debug('Not uploading purchase order {} to DocumentCloud'.format(
                purchase_order_number))
            return False
        else:
            return True

    # def _search_for_contract(self, key, value):
    #     '''
    #     Fetches the contract with the specified key and value from the
    #     DocumentCloud project.

    #     :param key: The key for searching through the DocumentCloud API.
    #     :type key: string.
    #     :param value: The key's value.
    #     :type value: string.
    #     :returns: A PythonDocumentCloud.Document class instance for the \
    #     matching contract.
    #     '''

    #     # Ex. "'%s':'%s'" % ('purchase order', purchase_order_number)
    #     # Ex. "'%s':'%s'" % ('contract number', k_number)

    #     search_term = "'%s':'%s'" % (key, value)
    #     document = self.api_connection.documents.search(search_term).pop()

    #     return document

    def _check_if_document_cloud_has_contract(self, key, value):
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

        # Ex. "'%s':'%s'" % ('purchase order', purchase_order_number)
        # Ex. "'%s':'%s'" % ('contract number', k_number)

        search_term = "'%s':'%s'" % (key, value)

        if len(self.api_connection.documents.search(search_term)) < 1:
            return False  # DocumentCloud project does not have contract.
        else:
            return True

    def prepare_then_add_contract(self, purchase_order_object):
        '''
        Call on method to make minor adjustments, then call on another method
        to upload the contract file and its metadata to the DocumentCloud
        project.

        :param purchase_order_object: A PurchaseOrder object instance.
        '''

        # Verify that there is at least one file to download.
        number_of_attachments = len(purchase_order_object.attachments)

        log.debug('There are %d attachments to upload.', number_of_attachments)

        if number_of_attachments > 0:
            for i, attachment in enumerate(purchase_order_object.attachments):
                attachment_id = re.search(
                    '[0-9]+', attachment.get('href')).group()
                attachment_location = (
                    '%s/%s.pdf' % (DOCUMENTS_DIR, attachment_id)
                )

                purchase_order_object = self.prepare_contract(
                    purchase_order_object,
                    i
                )
                self._upload_contract(
                    attachment_location,
                    purchase_order_object
                )

    @staticmethod
    def prepare_contract(purchase_order_object, iteration_value):
        '''
        Prepares to add a contract to our DocumentCloud project by making
        minor adjustments, such as changing the description and title language
        if there are multiple attachments.

        :param purchase_order_number: A PurchaseOrder object instance.
        :returns: A modified PurchaseOrder object instance.
        '''

        log.debug('Making modifications to contract data before uploading.')

        number_of_attachments = len(purchase_order_object.attachments)

        # If multiple attachments, add language like "page 1 of 2":
        page_string = ""
        if number_of_attachments > 1:
            page_string = "%s of %s" % (
                str(iteration_value + 1),
                str(number_of_attachments)
            )

        purchase_order_object.description += page_string

        purchase_order_object.title += page_string

        return purchase_order_object

    def _upload_contract(self, filename, purchase_order_object):
        '''
        This actually uploads a contract to our DocumentCloud project.

        :param filename: The path to the downloaded contract PDF file (?).
        :type filename: string
        :param description: The contract's description.
        :type description: string.
        :param title: The contract's title.
        :type title: string.
        '''

        log.debug('Uploading purchase order %s to DocumentCloud.', filename)

        is_null = self._check_if_contract_number_is_null(purchase_order_object)
        if is_null:
            return

        purchase_order_object.title = purchase_order_object.title.replace(
            "/", "")  # Not sure why this is necessary

        purchase_order_number = str(purchase_order_object.purchaseorder)
        title = str(purchase_order_object.title)

        log.debug('Uploading purchase order {} ({}) to DocumentCloud'.format(
            purchase_order_number, title)

        self.api_connection.documents.upload(
            filename,
            title,
            'City of New Orleans',  # Source of this file
            purchase_order_object.description,
            None,  # Related article
            PROJECT_URL,  # Published URL
            'public',  # Access
            self.project_id,  # Project
            purchase_order_object.data,  # Data
            False  # Secure
        )

    @staticmethod
    def _check_if_contract_number_is_null(purchase_order_object):
        '''
        Checks if this contract number is null.

        :params purchase_order_object: A PurchaseOrder object.
        :type purchase_order_object: A PurchaseOrder object.
        :returns: boolean. True if the contract number is null, False if not.
        '''

        if len(purchase_order_object.data['contract number']) < 1:
            log.info(
                'Not uploading purchase order %s to DocumentCloud. ' +
                'Contract number %s is null',
                purchase_order_object.data['purchase order'],
                purchase_order_object.data['contract number']
            )
            return True  # Contract number is null. Do not upload.
        else:
            return False

    # def _get_all_contracts(self):
    #     '''
    #     Runs a query for all of the contracts in our DocumentCloud project.

    #     :returns: A list of all of the project's contracts, stored as \
    #     PythonDocumentCloud instances.
    #     '''

    #     contracts = self.api_connection.documents.search(
    #         'projectid:%s' % self.project_id)

    #     return contracts

    # def _get_metadata(self, document_cloud_id):
    #     '''
    #     Fetches the metadata associated with this contract on our
    #     DocumentCloud project.

    #     :param document_cloud_id: The contract's unique ID in DocumentCloud.
    #     :type document_cloud_id: string
    #     :returns: dict? The contract's metadata.
    #     '''

    #     contract = self.api_connection.documents.get(document_cloud_id)
    #     metadata = contract.data

    #     return metadata

    # def _update_metadata(self, document_cloud_id, meta_key, meta_value):
    #     '''
    #     Updates the metadata associated with the contracts on DocumentCloud.

    #     :param document_cloud_id: The contract's unique ID in DocumentCloud.
    #     :type document_cloud_id: string
    #     :param meta_key: The specific metadata field for this contract.
    #     :type meta_key: string
    #     :param meta_value: The new metadata value for this field.
    #     :type meta_value: string
    #     '''

    #     # log.info(
    #     #     '{} | {} | updating {} on DocumentCloud. ' +
    #     #     'Changing {} to {}'.format(
    #     #         run_id,
    #     #         get_timestamp(),
    #     #         doc_cloud_id,
    #     #         meta_field,
    #     #         new_meta_data_value
    #     #     )
    #     # )
    #     contract = self.api_connection.documents.get(document_cloud_id)
    #     contract.data[meta_key] = meta_value
    #     contract.put()
