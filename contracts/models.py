"""
The web app that runs at vault.thelensnola.org/contracts
"""

import re
import time
from flask import Flask, request, make_response
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
# from flask.ext.cache import Cache
from contracts.lib.vaultclasses import (
    Vendor,
    Department,
    Contract,
    Person,
    VendorOfficer
)
from contracts.lib.models import QueryBuilder
from documentcloud import DocumentCloud
from contracts import (
    CONNECTION_STRING,
    log
)

PAGELENGTH = 8

app = Flask(__name__)  # , template_folder=templates)
# cache = Cache(app, config={'CACHE_TYPE': 'simple'})
documentCloudClient = DocumentCloud()

engine = create_engine(CONNECTION_STRING)

dc_query = 'projectid: "1542-city-of-new-orleans-contracts"'


class Models(object):

    '''doctstring'''

    def __init__(self):
        '''docstring'''
        pass

    def get_home(self):
        '''docstring'''

        data = {}
        data['docs'] = self.get_contracts(0, PAGELENGTH)
        data['totaldocs'] = self.get_contracts_count()
        data['pages'] = int(data['totaldocs'] / PAGELENGTH) + 1
        data['vendors'] = self.get_vendors()
        data['departments'] = self.get_departments()
        data['officers'] = self.get_officers()
        data['status'] = "Newest city contracts ..."
        data['updateddate'] = time.strftime("%m/%d/%Y")
        data['dc_query'] = 'projectid: "1542-city-of-new-orleans-contracts"'

        return data

    def get_download(self, docid):
        '''docstring'''

        docs = self.query_document_cloud("document:" + '"' + docid + '"')
        response = make_response(docs.pop().pdf)
        disposition_header = "attachment; filename=" + docid + ".pdf"
        response.headers["Content-Disposition"] = disposition_header

        return response

    def get_vendors_page(self, q):
        '''docstring'''

        if q == "all":
            vendors = self.get_vendors()

        return vendors

    def get_officers_page(self, q):
        '''docstring'''

        if q == "all":
            officers = self.get_officers()

        return officers

    def get_departments_page(self, q):
        '''docstring'''

        if q == "all":
            departments = self.get_departments()
        else:
            pass

        return departments

    def get_contracts_page(self, doc_cloud_id):
        '''docstring'''

        doc_cloud_id = re.sub(".html$", "", doc_cloud_id)

        return doc_cloud_id

    def get_search_page(self):
        '''docstring'''

        offset = self.query_request("page")
        offset = self.get_offset(offset)

        searchterm = self.translate_web_query_to_dc_query()

        if searchterm == 'projectid: "1542-city-of-new-orleans-contracts"':
            docs = self.get_contracts(0, PAGELENGTH)
            docs = self.translate_to_doc_cloud_form(docs)
        else:
            docs = self.query_document_cloud(searchterm)
            # extract a window of PAGELENGTH number of docs
            docs = docs[offset * PAGELENGTH:((offset + 1) * PAGELENGTH)]

        totaldocs = self.get_total_docs(searchterm)

        pages = (totaldocs / PAGELENGTH)
        vendor = self.query_request("vendor").upper()
        pages = pages + 1  # increment 1 to get rid of 0 indexing
        page = offset + 1  # increment 1 to get rid of 0 indexing

        status = self.get_status(page, pages, searchterm)
        updateddate = time.strftime("%m/%d/%Y")
        vendors = self.get_vendors()
        officers = self.get_officers()
        departments = self.get_departments()

        log.info('Pages = {}'.format(pages))

        standard_query = 'projectid: "1542-city-of-new-orleans-contracts" '

        data = {}

        data['vendors'] = vendors
        data['departments'] = departments
        data['offset'] = offset
        data['totaldocs'] = totaldocs
        data['status'] = status
        data['pages'] = pages
        data['page'] = offset + 1
        data['docs'] = docs
        data['officers'] = officers
        data['query'] = searchterm.replace(standard_query, "")
        data['updated'] = updateddate
        data['url'] = "contracts"
        data['vendor'] = vendor

        return data

    # @cache.memoize(timeout=900)
    @staticmethod
    def query_document_cloud(searchterm):
        """
        This is it's own method so that queries
        can be cached via @memoize to speed things up
        """
        return documentCloudClient.documents.search(searchterm)

    @staticmethod
    def translate_to_doc_cloud_form(docs):
        """
        In the database each row for contracts has an ID which
        is different from the doc_cloud_id on document cloud.
        This just translates rows so that their id is equal
        to the doc_cloud_id. It's a bit awkward and should
        probably be refactored away at some point.
        """
        for d in docs:
            d.id = d.doc_cloud_id
        return docs

    # @cache.memoize(timeout=900)
    def get_contracts(self, offset, limit):
        """
        Simply query the newest contracts
        """
        sn = sessionmaker(bind=engine)
        sn.configure(bind=engine)
        session = sn()
        offset = offset * PAGELENGTH
        contracts = session.query(
            Contract
        ).order_by(
            Contract.dateadded.desc()
        ).offset(
            offset
        ).limit(
            limit
        ).all()
        session.close()
        contracts = self.translate_to_doc_cloud_form(contracts)
        return contracts

    # @cache.memoize(timeout=100000)
    @staticmethod
    def get_contracts_count():
        """
        Query the count of all contracts
        """
        sn = sessionmaker(bind=engine)
        sn.configure(bind=engine)
        session = sn()
        total = session.query(Contract).count()
        session.close()
        return total

    # @cache.memoize(timeout=100000)  # cache good for a day or so
    @staticmethod
    def get_vendors():
        """
        Query all vendors in the database linked to a contract
        """
        sn = sessionmaker(bind=engine)
        sn.configure(bind=engine)
        session = sn()
        vendors = session.query(Vendor.name).\
            filter(Vendor.id == Contract.vendorid).\
            distinct().order_by(Vendor.name)
        vendors = sorted(list(set([j[0].strip() for j in vendors])))
        vendors.insert(0, "Vendor (example: Three fold Consultants)".upper())
        session.close()
        return vendors

    # @cache.memoize(timeout=100000)  # cache good for a day or so
    @staticmethod
    def get_departments():
        """
        Query all departments in the database
        """
        sn = sessionmaker(bind=engine)
        sn.configure(bind=engine)
        session = sn()
        depts = session.query(Department.name).\
            distinct().order_by(Department.name).all()
        depts = [j[0].strip() for j in depts]
        depts = sorted(list(set(depts)))
        depts.insert(0, "Department (example: Information Technology)".upper())
        session.close()
        return depts

    # @cache.memoize(timeout=100000)  # cache good for a day or so
    @staticmethod
    def get_officers(vendor=None):
        """
        Get officers for a given vendor
        """
        sn = sessionmaker(bind=engine)
        sn.configure(bind=engine)
        session = sn()
        if vendor is None:
            officers = session.query(
                VendorOfficer,
                Person
            ).filter(
                VendorOfficer.personid == Person.id
            ).order_by(
                Person.name
            )
            session.close()
            officers = sorted(list(set([o[1].name for o in officers])))
            message = (
                "Company officer (example: Joe Smith) - feature in progress")
            officers.insert(0, message.upper())
            return officers
        else:
            vendor = vendor.replace("vendor:", "")
            officers = session.\
                query(VendorOfficer, Person, Vendor).\
                filter(VendorOfficer.personid == Person.id).\
                filter(VendorOfficer.vendorid == Vendor.id).\
                filter(Vendor.name == vendor).all()
            session.close()
            officers = list(set([o[1].name for o in officers]))
            print officers
            return sorted(officers)

    # @cache.memoize(timeout=100000)
    @staticmethod
    def translate_to_vendor(officerterm):
        """
        Translates a request for an officer to a request for a vendor
        associated with a given officer
        """
        sn = sessionmaker(bind=engine)
        sn.configure(bind=engine)
        session = sn()
        officerterm = officerterm.replace(
            '"', "").replace("officers:", "").strip()
        results = session.query(Person, VendorOfficer, Vendor).\
            filter(Person.name == officerterm).\
            filter(Person.id == VendorOfficer.personid).\
            filter(VendorOfficer.vendorid == Vendor.id).all()
        # todo fix to get .first() working
        output = results.pop()[2].name
        log.info("translating | {} to {}".format(officerterm, output))
        return output

    # @cache.memoize(timeout=100000)
    def get_pages(self, searchterm):
        """
        Get the total number of pages for a given search.
        """
        if searchterm == 'projectid: "1542-city-of-new-orleans-contracts"':
            return int(self.get_contracts_count() / PAGELENGTH)
        else:
            return int(len(self.query_document_cloud(searchterm)) / PAGELENGTH)

    # @cache.memoize(timeout=100000)
    def get_total_docs(self, searchterm):
        """
        Get the total number of relevant docs for a given search.
        """
        if searchterm == 'projectid: "1542-city-of-new-orleans-contracts"':
            return self.get_contracts_count()
        else:
            return int(len(self.query_document_cloud(searchterm)))

    @staticmethod
    def get_status(page, total, searchterm):
        """
        Tells the user what search has returned
        """
        basic_query = 'projectid: "1542-city-of-new-orleans-contracts"'
        output = ""
        output = output + str(total) \
            + " results | Query: " + \
            searchterm.\
            replace(basic_query, "")
        output = output + " | "
        if searchterm == basic_query:
            return output + "All city contracts: page "\
                + str(page) + " of " + str(total)
        else:
            return output + "Page " + str(page) + " of " + str(total)

    @staticmethod
    def query_request(field):
        """
        Pulls the field out from the request,
        returning "" if field is none
        """
        field = request.args.get(field)
        if field is None:
            return ""
        else:
            return field

    def translate_web_query_to_dc_query(self):
        """
        Translates a request URL to a DC query
        """
        query_builder = QueryBuilder()
        query = self.query_request("query")
        query_builder.add_text(query)
        query_builder.add_term(
            "projectid", "1542-city-of-new-orleans-contracts")

        terms = ['vendor', 'department']

        for t in terms:
            query_value = self.query_request(t)
            if self.query_request(t) != "":
                query_builder.add_term(t, query_value)

        officers = self.query_request('officer')

        if len(officers) > 0:
            officers = [officers]
            vendor = self.translate_to_vendor(officers[0])
            query_builder.add_term("vendor", vendor)

        return query_builder.get_query()

    @staticmethod
    def get_offset(offset):
        """
        Offsets cant be "" or less than 0.
        This handles translation
        """
        log.info("offset | {}".format(offset))
        if offset == "":
            offset = 0
        elif offset < 0:
            offset = 0
        else:
            offset = int(offset) - 1  # a page is one more than an offset
        return offset
