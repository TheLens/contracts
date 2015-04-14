#!/usr/bin/python
"""
Some utility classes
"""
import re


class Utilities():

    def valid_po(self, purchaseorderno):
        po_re = '[A-Z]{2}\d{3,}'
        po_regex = re.compile(po_re)
        if po_regex.match(purchaseorderno):
            return True
        else:
            return False


class QueryBuilder():
    """
    Build a document cloud query
    """
    def __init__(self):
        self.query = {}
        self.text = ""

    def add_term(self, term, value):
        self.query[term] = value

    def add_text(self, text):
        self.text = text

    def get_query(self):
        output = ""
        for k in self.query.keys():
            # 'projectid: "1542-city-of-new-orleans-contracts"'
            output += k + ":" + '"' + self.query[k] + '" '
        output = output + self.text
        return output.strip()
