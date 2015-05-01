#!/usr/bin/python
"""
Some utility classes
"""
import re


def valid_po(purchaseorderno):
    """
    A simple method to determine if this
    is a valid purchase order
    """
    po_re = r'[A-Z]{2}\d{3,}'
    po_regex = re.compile(po_re)
    if po_regex.match(purchaseorderno):
        return True
    else:
        return False


class QueryBuilder(object):
    """
    Build a document cloud query
    """
    def __init__(self):
        """
        Initialized as blank.
        Terms are stored in a dictionary.
        """
        self.query = {}
        self.text = ""

    def add_term(self, term, value):
        """
        Add a term to the dictionary.
        If term is updated it will just
        re write the dictionary value
        """
        self.query[term] = value

    def add_text(self, text):
        """
        Add a freetext component to
        the query (ex. "playground")
        """
        self.text = text

    def get_query(self):
        """
        Translate the dictionary into
        a document cloud query
        """
        output = ""
        for k in self.query.keys():
            # 'projectid: "1542-city-of-new-orleans-contracts"'
            output += k + ":" + '"' + self.query[k] + '" '
        output = output + self.text
        return output.strip()
