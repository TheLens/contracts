"""
The web app that runs at vault.thelensnola.org/contracts.
"""

# import re
import time
from flask import make_response
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
# from flask.ext.cache import Cache
from contracts.db import (
    Vendor,
    Department,
    Contract,
    Person,
    VendorOfficer
)
from pythondocumentcloud import DocumentCloud
from contracts import (
    CONNECTION_STRING,
    log
)

# cache = Cache(app, config={'CACHE_TYPE': 'simple'})


class Models(object):

    '''doctstring'''

    def __init__(self):
        '''docstring'''

        self.engine = create_engine(CONNECTION_STRING)
        self.pagelength = 8  # DocumentCloud API default is 10
        self.dc_query = 'projectid:1542-city-of-new-orleans-contracts'
        self.document_cloud_client = DocumentCloud()

    def get_home(self):
        '''docstring'''

        log.debug('get_home')

        data = {}
        log.debug(data)

        # Get a list of vendors for dropdown
        data['vendors'] = self.get_vendors()
        log.debug(data)

        # Get a list of departments for dropdown
        data['departments'] = self.get_departments()
        log.debug(data)

        # Get a list of officers for dropdown
        data['officers'] = self.get_officers()
        log.debug(data)

        # Find the last updated date for footer
        data['updated_date'] = time.strftime("%b %-d, %Y")
        log.debug(data)

        log.debug('Done collecting home data')

        return data

    def get_search_page(self, request):
        '''docstring'''

        log.debug('start get_search_page')

        # Extract search parameters (text input and dropdown selections)
        data = self.parse_query_string(request)

        incoming_data = data

        # Transform query parameters into string for DocumentCloud API.
        search_term = self.translate_web_query_to_dc_query(data)

        if search_term == self.dc_query:  # If no search input
            log.debug('No search parameters entered.')

            # Get a list of contracts from local DB, without any search filter:
            documents = self.get_contracts(limit=self.pagelength)

            # Fixing IDs:
            documents = self.translate_to_doc_cloud_form(documents)
        else:
            log.debug('Some search parameters entered.')

            # Get a list of contracts by querying our project on DocCloud:
            documents = self.query_document_cloud(
                search_term, page=data['current_page'])

        number_of_documents = self.find_number_of_documents(search_term)

        number_of_pages = number_of_documents / self.pagelength

        # Increment by 1 to correct zero-indexing:
        number_of_pages = number_of_pages + 1
        log.debug('number_of_pages: %d', number_of_pages)

        # Create results language to tell user what they searched for:
        status = self.get_status(
            data['current_page'], number_of_pages, search_term)

        updated_date = time.strftime("%b %-d, %Y")

        vendors = self.get_vendors()
        officers = self.get_officers()
        departments = self.get_departments()

        output_data = {}

        output_data['vendors'] = vendors
        output_data['departments'] = departments
        output_data['officers'] = officers
        output_data['number_of_documents'] = number_of_documents
        output_data['status'] = status
        output_data['number_of_pages'] = number_of_pages
        output_data['current_page'] = data['current_page']
        output_data['documents'] = documents
        output_data['updated_date'] = updated_date

        log.debug('end of get_search_page')
        # log.debug('current_page: %d', output_data['current_page'])

        return output_data, incoming_data

    @staticmethod
    def get_contracts_page(doc_cloud_id):
        '''docstring'''

        data = {}

        updated_date = time.strftime("%b %-d, %Y")

        data['doc_cloud_id'] = doc_cloud_id
        data['updated_date'] = updated_date

        return data

    def get_download(self, docid):
        '''docstring'''

        docs = self.query_document_cloud("document:" + '"' + docid + '"')
        response = make_response(docs.pop().pdf)
        disposition_header = "attachment; filename=" + docid + ".pdf"
        response.headers["Content-Disposition"] = disposition_header

        return response

    @staticmethod
    def parse_query_string(request):
        '''
        Receives URL query string parameters and returns as dict.

        :param request: A (Flask object?) containing query string.
        :returns: A dict with the query string parameters.
        '''

        log.debug('parse_query_string')

        data = {}
        data['search_input'] = request.args.get('query')
        data['vendor'] = request.args.get('vendor')
        data['department'] = request.args.get('department')
        data['officer'] = request.args.get('officer')
        data['current_page'] = request.args.get('page')

        if data['current_page'] is None or data['current_page'] == '':
            data['current_page'] = 1
        else:
            data['current_page'] = int(data['current_page'])

        log.debug('current_page: %d', data['current_page'])

        # Change any missing parameters to 0-length string
        for key in data:
            if data[key] is None:
                data[key] = ''

        return data

    # @cache.memoize(timeout=900)
    def query_document_cloud(self, search_term, page=1):
        """
        This is it's own method so that queries can be cached via @memoize to
        speed things up.
        """

        log.debug('search_term: "%s"', search_term)

        log.debug('Page: %d', page)

        output = self.document_cloud_client.documents.search(
            search_term, page=page, per_page=self.pagelength)

        log.debug('len(output): %d', len(output))

        return output

    # @cache.memoize(timeout=900)
    def query_document_cloud_count(self, search_term):
        """
        Finds the number of documents in DocumentCloud matching this query.
        """

        log.debug(
            'query_document_cloud_count with search_term: %s', search_term)

        output = self.document_cloud_client.documents.search_count(search_term)

        log.debug('output')
        log.debug(output)

        return output

    @staticmethod
    def translate_to_doc_cloud_form(documents):
        """
        In the database each row for contracts has an ID which is different
        from the doc_cloud_id on DocumentCloud. This just translates rows so
        that their id is equal to the doc_cloud_id. It's a bit awkward and
        should probably be refactored away at some point.
        """

        log.debug('translate_to_doc_cloud_form')

        for document in documents:
            document.id = document.doc_cloud_id

        return documents

    # @cache.memoize(timeout=900)
    def get_contracts(self, offset=0, limit=None):
        """
        Simply query the newest contracts.
        """

        log.debug('get_contracts')

        sn = sessionmaker(bind=self.engine)
        session = sn()
        offset = offset * self.pagelength

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

        log.debug(contracts)

        return contracts

    # @cache.memoize(timeout=100000)
    def get_contracts_count(self):
        """
        Query the count of all contracts.
        """

        log.debug('Start get_contracts_count')

        sn = sessionmaker(bind=self.engine)
        session = sn()

        total = session.query(
            Contract
        ).count()

        session.close()

        log.debug('End of get_contracts_count')

        return total

    # @cache.memoize(timeout=100000)  # cache good for a day or so
    def get_vendors(self):
        """
        Query all vendors in the database linked to a contract.
        """

        sn = sessionmaker(bind=self.engine)
        session = sn()

        vendors = session.query(
            Vendor.name
        ).filter(
            Vendor.id == Contract.vendorid
        ).distinct().order_by(
            Vendor.name
        )

        vendors = [vendor[0].strip() for vendor in vendors]

        session.close()

        return vendors

    # @cache.memoize(timeout=100000)  # cache good for a day or so
    def get_departments(self):
        """
        Query all departments in the database.
        """

        sn = sessionmaker(bind=self.engine)
        session = sn()

        departments = session.query(
            Department.name
        ).distinct().order_by(
            Department.name
        ).all()

        departments = [department[0].strip() for department in departments]

        # log.debug(departments)

        # departments = sorted(list(set(departments)))

        # log.debug(departments)

        session.close()

        return departments

    # @cache.memoize(timeout=100000)  # cache good for a day or so
    def get_officers(self, vendor=None):
        """
        Get officers for a given vendor.
        """

        sn = sessionmaker(bind=self.engine)
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
            officers = sorted(
                list(
                    set(
                        [o[1].name for o in officers]
                    )
                )
            )

            return officers
        else:
            vendor = vendor.replace("vendor:", "")
            officers = session.query(
                VendorOfficer,
                Person,
                Vendor
            ).filter(
                VendorOfficer.personid == Person.id
            ).filter(
                VendorOfficer.vendorid == Vendor.id
            ).filter(
                Vendor.name == vendor
            ).all()
            session.close()
            officers = list(set([o[1].name for o in officers]))
            print officers
            return sorted(officers)

    # @cache.memoize(timeout=100000)
    def translate_to_vendor(self, officerterm):
        """
        Translates a request for an officer to a request for a vendor
        associated with a given officer.
        """

        sn = sessionmaker(bind=self.engine)
        session = sn()

        officerterm = officerterm.replace(
            '"', "").replace("officers:", "").strip()

        results = session.query(
            Person,
            VendorOfficer,
            Vendor
        ).filter(
            Person.name == officerterm
        ).filter(
            Person.id == VendorOfficer.personid
        ).filter(
            VendorOfficer.vendorid == Vendor.id
        ).all()  # todo fix to get .first() working

        output = results.pop()[2].name
        log.info("translating %s to %s", officerterm, output)

        return output

    # @cache.memoize(timeout=100000)
    def find_number_of_documents(self, search_term):
        """
        Get the total number of relevant docs for a given search.
        """

        log.debug('find_number_of_documents')

        if search_term == self.dc_query:
            log.debug('if')
            # Get count for local DB:
            return self.get_contracts_count()
        else:
            log.debug('else')
            # Get count for DocumentCloud output:
            return self.query_document_cloud_count(search_term)

    def get_status(self, page, total, search_term):
        """
        Tells the user what search has returned.
        """

        output = str(total) + " results | Query: " + search_term.replace(
            self.dc_query, "") + " | "

        if search_term == self.dc_query:
            return output + "All city contracts: page " + \
                str(page) + " of " + str(total)
        else:
            return output + "Page " + str(page) + " of " + str(total)

    def translate_web_query_to_dc_query(self, data):
        """
        Translates search input parameters into a request string for the
        DocumentCloud API.
        Use 'projectid:1542-city-of-new-orleans-contracts' to restrict search
        to our project.
        """

        log.debug('translate_web_query_to_dc_query')

        query_builder = QueryBuilder()
        query_builder.add_text(data['search_input'])
        query_builder.add_term(
            self.dc_query.split(':')[0], self.dc_query.split(':')[1])

        terms = ['vendor', 'department']  # , 'officer']

        for term in terms:
            query_value = data[term]
            if query_value != "":
                query_builder.add_term(term, query_value)

        # officers = self.query_request('officer')

        # if len(officers) > 0:
        #     officers = [officers]
        #     vendor = self.translate_to_vendor(officers[0])
        #     query_builder.add_term("vendor", vendor)

        output = query_builder.get_query()

        log.debug(output)

        return output


class QueryBuilder(object):
    """
    Build a query for the DocumentCloud API.
    """

    def __init__(self):
        """
        Initialized as blank. Terms are stored in a dictionary.
        """

        self.query = {}
        self.text = ""

    def add_term(self, term, value):
        """
        Add a term to the dictionary. If term is updated it will just
        re-write the dictionary value.
        """

        self.query[term] = value

    def add_text(self, text):
        """
        Add a freetext component to the query (ex. 'playground').
        """

        self.text = text

    def get_query(self):
        """
        Translate the dictionary into a DocumentCloud query.
        """

        output = ""
        for k in self.query.keys():
            output += k + ":" + '"' + self.query[k] + '" '
        output = output + self.text
        return output.strip()
