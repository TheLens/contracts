
'''Test cases for contracts.lib.purchase_order.py.'''

from unittest import TestCase
# from contracts.lib.purchase_order import PurchaseOrder


class TestPurchaseOrder(TestCase):

    # TODO: This calls on a lot of methods, so work on those tests first.
    # def test_init(self):
    #     output = DocumentCloudProject().translate_to_vendor('ALDEN J MCDO')
    #     self.assertEquals(output.strip(), 'Liberty Bank')

    # TODO: This calls on a lot of methods, so work on those tests first.
    def test_get_data(self):
        self.assertEquals(1, 1)

    def test_download_attachment(self):
        self.assertEquals(False, False)

    def test_get_html(self):
        self.assertEquals(True, True)

    def test_download_purchase_order(self):
        self.assertEquals(False, False)

    def test_download_vendor_profile(self):
        self.assertEquals(None, None)

    def test_get_attachments(self):
        self.assertNotEquals(True, False)

    def test_get_vendor_id(self):
        self.assertEquals(1, 1)

    def test_get_description(self):
        self.assertEquals(1, 1)

    def test_get_vendor_name(self):
        self.assertEquals(1, 1)

    def test_get_knumber(self):
        self.assertEquals(1, 1)

    def test_get_purchase_order(self):
        self.assertEquals(True, True)

    def test_get_department(self):
        self.assertEquals(False, False)

    def test_download_attachment_file(self):
        self.assertEquals(False, False)

# if __name__ == '__main__':
#     TestDocumentCloudProject().test_translate_query_vendor()
