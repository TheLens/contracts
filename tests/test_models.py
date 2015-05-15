
'''docstring'''

from unittest import TestCase
from contracts.lib.models import (
    DocumentCloudProject,
    PurchaseOrder
    # LensRepository
)
from contracts.lib.models import valid_purchase_order


class TestDocumentCloudProject(TestCase):

    '''docstring'''

    def test_valid_purchase_order(self):
        '''docstring'''

        self.assertEquals(valid_purchase_order("HS486912"), True)

    def test_valid_purchase_order1(self):
        '''docstring'''

        # utils = Utilities()
        self.assertEquals(valid_purchase_order("HS4"), False)

    def test_document_cloud_project_has_purchase_order(self):
        '''docstring'''

        document = DocumentCloudProject()
        self.assertEquals(
            document.has_contract('purchase order', 'HL592896'), True)

    def test_document_cloud_project_has_purchase_order2(self):
        '''docstring'''

        document = DocumentCloudProject()
        self.assertEquals(
            document.has_contract('purchase order', 'somerandomstuff'), False)

    def test_document_cloud_project_get_all_docs(self):
        '''docstring'''

        document = DocumentCloudProject()
        self.assertEquals(document.docs, None)

    def test_document_cloud_project_get_all_docs2(self):
        '''docstring'''

        document = DocumentCloudProject()
        document.get_all_docs()
        self.assertNotEquals(document.docs, None)

    def test_get_contract(self):
        '''docstring'''

        document = DocumentCloudProject()
        self.assertEquals(
            document.get_contract(
                "purchase order",
                "HL592896"
            ).id,
            "1684637-orleans-parish-sheriffs-office-1st-amendment-to"
        )

    def test_purchase_order(self):
        '''docstring'''

        purchase_order = PurchaseOrder('HS486912')
        self.assertEquals(purchase_order.purchaseorder, "HS486912")

    def test_vendor_id(self):
        '''docstring'''

        purchase_order = PurchaseOrder('HS486912')
        self.assertEquals(purchase_order.vendor_id_city, "00000843")

    def test_update_metadata(self):
        '''docstring'''

        purchase_order = PurchaseOrder('ED263245')
        document = DocumentCloudProject()
        doc_cloud_id = document.get_contract("purchase order", "ED263245").id
        document.update_metadata(
            doc_cloud_id, "vendor_id", purchase_order.vendor_id_city)
        contract = document.client.documents.get(doc_cloud_id)
        self.assertEquals(
            contract.data["vendor_id"], purchase_order.vendor_id_city)

    # def test_repository_has_pos(self):
    #     repo = LensRepository()
    #     self.assertEquals(repo.has_pos("YH380294"), True)

    # def test_valid_purchase_order2(self):
    #     repo = LensRepository()
    #     self.assertEquals(repo.has_pos("noates3p4"), False)
