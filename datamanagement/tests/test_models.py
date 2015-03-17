from unittest import TestCase
from contracts.datamanagement.lib.models import DocumentCloudProject, PurchaseOrder, LensRepository
from contracts.settings import Settings

s = Settings()

class TestDocumentCloudProject(TestCase):

    def test_DocumentCloudProject_has_purchase_order(self):
        d = DocumentCloudProject()
        self.assertEquals(d.has_contract('purchase order', 'HL592896'), True)


    def test_DocumentCloudProject_has_purchase_order2(self):
        d = DocumentCloudProject()
        self.assertEquals(d.has_contract('purchase order', 'somerandomstuff'), False)


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


    def test_vendor_id(self):
        corpus_loc = s.corpus_loc
        lines = corpus_loc + "/purchaseorders/" + "HS486912"
        lines = "".join([l.replace("\n", "") for l in open(lines)])
        po = PurchaseOrder(lines)
        self.assertEquals(po.vendor_id_city, "00000843")


    def test_update_metadata(self):
        corpus_loc = s.corpus_loc
        lines = corpus_loc + "/purchaseorders/" + "ED263245"
        lines = "".join([l.replace("\n", "") for l in open(lines)])
        po = PurchaseOrder(lines)
        d = DocumentCloudProject()
        doc_cloud_id = d.get_contract("purchase order", "ED263245").id
        d.update_metadata(doc_cloud_id , "vendor_id", po.vendor_id_city)
        contract = d.client.documents.get(doc_cloud_id)
        self.assertEquals(contract.data["vendor_id"], po.vendor_id_city)

    def test_repository_has_pos(self):
        repo = LensRepository()
        self.assertEquals(repo.has_pos("YH380294"), True)


    def test_valid_po(self):
        repo = LensRepository()
        self.assertEquals(repo.has_pos("noates3p4"), False)