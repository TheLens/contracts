from unittest import TestCase
from contracts.datamanagement.lib.models import DocumentCloudProject, PurchaseOrder
from contracts.settings import Settings

s = Settings()

class TestDocumentCloudProject(TestCase):

    def test_DocumentCloudProject_has_purchase_order(self):
        d = DocumentCloudProject()
        self.assertEquals(d.has_contract_with_purchase_order('HL592896'), True)


    def test_DocumentCloudProject_has_purchase_order2(self):
        d = DocumentCloudProject()
        self.assertEquals(d.has_contract_with_purchase_order('somerandomstuff'), False)


    def test_DocumentCloudProject_get_all_docs(self):
        d = DocumentCloudProject()
        self.assertEquals(d.docs, None)


    def test_DocumentCloudProject_get_all_docs2(self):
        d = DocumentCloudProject()
        d.get_all_docs()
        self.assertNotEquals(d.docs, None)


    def test_get_contract(self):
        d = DocumentCloudProject()
        self.assertEquals(d.get_contract("purchase order" ,"HL592896").id, "1684637-orleans-parish-sheriffs-office-1st-amendment-to")


    def test_purchase_order(self):
        corpus_loc = s.corpus_loc
        lines = corpus_loc + "/purchaseorders/" + "HS486912"
        lines = "".join([l.replace("\n", "") for l in open(lines)])
        po = PurchaseOrder(lines)
        self.assertEquals(po.purchaseorder, "HS486912")