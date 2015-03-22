import re 

class Utilities():

    def valid_po(self, purchaseorderno):
        po_re = '[A-Z]{2}\d+'
        po_regex = re.compile(po_re)
        if po_regex.match(purchaseorderno):
            return True
        else:
            return False