
'''Test cases for contracts.lib.models.'''

from unittest import TestCase
from contracts.lib.models import (
    DocumentCloudProject,
    PurchaseOrder,
    # LensRepository,
    valid_purchase_order,
    LensDatabase
)


class TestLibModels(TestCase):

    pass

    # def test_translate_query_vendor(self):
    #     output = Models().translate_to_vendor('ALDEN J MCDONALD')
    #     print output
    #     self.assertEquals(output.strip(), 'Liberty Bank')

    # def test_translate_web_query_to_dc_query(self):
    #     data = {
    #         'search_input': '',
    #         'department': '',
    #         'vendor': '',
    #         'officer': 'ALDEN J MCDONALD',
    #         'current_page': ''
    #     }
    #     output = Models().translate_web_query_to_dc_query(data)
    #     print output
    #     self.assertEquals(
    #         output.strip(),
    #         'projectid:"1542-city-of-new-orleans-contracts" ' +
    #         'vendor:"Liberty Bank "')

    def test_valid_purchase_order(self):
        self.assertEquals(valid_purchase_order("HS486912"), True)

    def test_valid_purchase_order1(self):
        # utils = Utilities()
        self.assertEquals(valid_purchase_order("HS4"), False)

    def test_document_cloud_project_has_purchase_order(self):
        d = DocumentCloudProject()
        self.assertEquals(d.has_contract('purchase order', 'HL592896'), True)

    def test_document_cloud_project_has_purchase_order2(self):
        d = DocumentCloudProject()
        self.assertEquals(
            d.has_contract('purchase order', 'somerandomstuff'), False)

    def test_document_cloud_project_get_all_docs(self):
        d = DocumentCloudProject()
        self.assertEquals(d.docs, None)

    def test_document_cloud_project_get_all_docs2(self):
        d = DocumentCloudProject()
        d.get_all_docs()
        self.assertNotEquals(d.docs, None)

    def test_get_contract(self):
        d = DocumentCloudProject()
        self.assertEquals(d.get_contract(
            "purchase order",
            "HL592896").id,
            "1684637-orleans-parish-sheriffs-office-1st-amendment-to")

    def test_purchase_order(self):
        po = PurchaseOrder('HS486912')
        self.assertEquals(po.purchaseorder, "HS486912")

    def test_vendor_id(self):
        po = PurchaseOrder('HS486912')
        self.assertEquals(po.vendor_id_city, "00000843")

    def test_update_metadata(self):
        po = PurchaseOrder('ED263245')
        d = DocumentCloudProject()
        doc_cloud_id = d.get_contract("purchase order", "ED263245").id
        d.update_metadata(doc_cloud_id, "vendor_id", po.vendor_id_city)
        contract = d.client.documents.get(doc_cloud_id)
        self.assertEquals(contract.data["vendor_id"], po.vendor_id_city)

    def test_repository_has_contract(self):
        repo = LensDatabase()
        self.assertEquals(repo.has_contract("YH380294"), True)

    def test_valid_purchase_order2(self):
        self.assertEquals(valid_purchase_order("noates3p4"), False)

# if __name__ == '__main__':
#     TestDocumentCloudProject().test_translate_query_vendor()
