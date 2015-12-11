
'''The web app that runs at vault.thelensnola.org/contracts.'''

import time
from flask import make_response
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
# from flask.ext.cache import Cache

from pythondocumentcloud import DocumentCloud

from contracts import CONNECTION_STRING, log
from contracts._db import (
    Vendor,
    Department,
    Contract,
    Person,
    VendorOfficer
)
from contracts._results_language import ResultsLanguage

# cache = Cache(app, config={'CACHE_TYPE': 'simple'})

# Emoji
red_no_emoji = "\xF0\x9F\x9A\xAB"


class Models(object):

    '''Methods for retrieving data for certain app views.'''

    def __init__(self):
        self.pagelength = 10  # DocumentCloud API default is 10
        self.dc_contracts_query = 'projectid:1542-city-of-new-orleans-contracts'
        self.document_cloud_client = DocumentCloud()

        engine = create_engine(CONNECTION_STRING)
        self.sql_session = sessionmaker(bind=engine)

    def get_home(self):
        '''
        Gather data necessary for the homepage (/contracts/).
        Queries DocumentCloud project.

        :returns: dict. A dict with data for dropdowns and dates.
        '''

        # Find the last updated date for footer
        updated_date = time.strftime("%b. %-d, %Y")
        updated_date = updated_date.replace('Mar.', 'March')  # AP Style
        updated_date = updated_date.replace('Apr.', 'April')
        updated_date = updated_date.replace('May.', 'May')
        updated_date = updated_date.replace('Jun.', 'June')
        updated_date = updated_date.replace('Jul.', 'July')

        data = {}
        data['number_of_documents'] = self.pagelength
        # data['total_number_of_documents'] = self._find_number_of_documents(
        #     search_term)
        data['updated_date'] = updated_date

        # Dropdown menus
        data['vendors'] = self._get_vendors()
        data['departments'] = self._get_departments()
        data['officers'] = self._get_officers()

        # Get a list of contracts by querying our project on DocumentCloud
        data['documents'] = self._query_document_cloud(
            self.dc_contracts_query, page=1)

        return data

    def get_search_page(self, request):
        '''
        Gets the data necessary for the search page (/contracts/search/).

        :param request: The search parameters supplied by the user.
        :type request: dict
        :returns: dict. Two dicts: one for newly gather data, and the other \
        an altered version of the incoming search parameters.
        '''

        # Extract search parameters (text input and dropdown selections)
        search_input_data = self._parse_query_string(request)

        # Transform query parameters into string for DocumentCloud API.
        search_term = self._translate_web_query_to_doc_cloud_query(
            search_input_data)
        log.debug(search_term)

        # Get a list of contracts by querying DocumentCloud project.
        documents = self._query_document_cloud(
            search_term, page=search_input_data['current_page'])

        number_of_documents = self._find_number_of_documents(search_term)
        log.debug(number_of_documents)

        # Increment by 1 to correct zero-indexing:
        number_of_pages = (number_of_documents / self.pagelength) + 1
        log.debug('number_of_pages: %d', number_of_pages)

        updated_date = time.strftime("%b. %-d, %Y")
        updated_date = updated_date.replace('Mar.', 'March')  # AP Style
        updated_date = updated_date.replace('Apr.', 'April')
        updated_date = updated_date.replace('May.', 'May')
        updated_date = updated_date.replace('Jun.', 'June')
        updated_date = updated_date.replace('Jul.', 'July')

        output_data = {}

        output_data['departments'] = self._get_departments()  # Dropdown menus
        output_data['officers'] = self._get_officers()
        output_data['vendors'] = self._get_vendors()

        output_data['current_page'] = search_input_data['current_page']
        output_data['documents'] = documents
        output_data['number_of_documents'] = number_of_documents
        output_data['number_of_pages'] = number_of_pages
        output_data['results_language'] = ResultsLanguage(
            search_input_data, number_of_documents).main()
        output_data['search_input'] = search_input_data['search_input']
        output_data['updated_date'] = updated_date

        search_input_dict = {}
        search_input_dict['parameter_input_data'] = search_input_data

        output_data['search_input'] = search_input_dict

        return output_data  # TODO: consolidate this

    @staticmethod
    def get_contracts_page(doc_cloud_id):
        '''
        Get data necessary for the single contract page. This only gets the
        updated date, so it is mostly a placeholder for now.

        :param doc_cloud_id: The single contract's uniquey DocumentCloud ID.
        :type doc_cloud_id: string
        :returns: dict. A dict with the updated date.
        '''

        updated_date = time.strftime("%b. %-d, %Y")

        # Correct for AP Style
        updated_date = updated_date.replace('Mar.', 'March')
        updated_date = updated_date.replace('Apr.', 'April')
        updated_date = updated_date.replace('May.', 'May')
        updated_date = updated_date.replace('Jun.', 'June')
        updated_date = updated_date.replace('Jul.', 'July')

        data = {}
        data['doc_cloud_id'] = doc_cloud_id
        data['updated_date'] = updated_date

        return data

    def get_download(self, doc_cloud_id):
        '''
        ???

        :param doc_cloud_id: The unique ID for this contract in DocumentCloud.
        :type doc_cloud_id: string
        :returns: PDF. The PDF file for this contract (?).
        '''

        docs = self._query_document_cloud('document:"%s"' % doc_cloud_id)
        response = make_response(docs.pop().pdf)
        disposition_header = "attachment; filename=%s.pdf" % doc_cloud_id
        response.headers["Content-Disposition"] = disposition_header

        return response

    @staticmethod
    def _parse_query_string(request):
        '''
        Receives search parameter data and returns as dict.

        :param request: A (Flask object?) containing query string.
        :type request: dict?
        :returns: dict. The query string parameters entered by the user.
        '''

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

        # Change any missing parameters to 0-length string
        for key in data:
            if data[key] is None:
                data[key] = ''

        return data

    # @cache.memoize(timeout=900)
    def _query_document_cloud(self, search_term, page=1):
        '''
        Queries the DocumentCloud API.
        This is it's own method so that queries can be cached via @memoize to
        speed things up.

        :param search_term: The query term to run against DocumentCloud API.
        :type search_term: string
        :param page: The page to receive in return. Useful for pagination. \
        Default: 1.
        :type page: string
        :returns: dict. (?) The output that matches the query.
        '''

        log.debug('search_term: "%s"', search_term)
        log.debug('Page: %d', page)

        output = self.document_cloud_client.documents.search(
            search_term, page=page, per_page=self.pagelength)

        log.debug('len(output): %d', len(output))
        log.debug('_query_document_cloud output:')
        log.debug(output)

        return output

    # @cache.memoize(timeout=900)
    def _query_document_cloud_count(self, search_term):
        '''
        Finds the number of documents in DocumentCloud project that
        match this query.

        :param search_term: The search term for DocumentCloud API query.
        :type search_term: string
        :returns: int. The number of records that match this query.
        '''

        log.debug('search_term: %s', search_term)

        output = self.document_cloud_client.documents.search_count(search_term)

        return output

    # @cache.memoize(timeout=100000)
    def _get_contracts_count(self):
        '''
        Query the count of all contracts in database.

        :returns: int. The total number of contracts in the database.
        '''

        session = self.sql_session()

        total = session.query(
            Contract
        ).count()

        session.close()

        return total

    # @cache.memoize(timeout=100000)  # cache good for a day or so
    def _get_vendors(self):
        '''
        Query all vendors in the database linked to a contract.

        :returns: list. (?) The vendors that are linked to a contract.
        '''

        session = self.sql_session()

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
    def _get_departments(self):
        '''
        Query all departments in the database.

        :returns: list. All departments in our database.
        '''

        session = self.sql_session()

        departments = session.query(
            Department.name
        ).distinct().order_by(
            Department.name
        ).all()

        departments = [department[0].strip() for department in departments]

        session.close()

        return departments

    # @cache.memoize(timeout=100000)  # cache good for a day or so
    def _get_officers(self, vendor=None):
        '''
        Get officers for a given vendor.

        :param vendor: The vendor to check on.
        :type vendor: string
        :returns: list. A list of officers listed under the vendor company in \
        the Secretary of State's database.
        '''

        session = self.sql_session()

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
            officers = session.query(
                VendorOfficer,
                Person,
                Vendor
            ).filter(
                VendorOfficer.personid == Person.id
            ).filter(
                VendorOfficer.vendorid == Vendor.id
            ).filter(
                Vendor.name == vendor.replace("vendor:", "")
            ).all()
            session.close()

            officers = list(set([o[1].name for o in officers]))

            return sorted(officers)

    # @cache.memoize(timeout=100000)
    def _translate_officer_to_vendor(self, officer_term):
        '''
        Translates a request for an officer to a request for a vendor
        associated with a given officer.

        :param officer_term: The name of the officer.
        :type officer_term: string
        :returns: ???
        '''

        session = self.sql_session()

        officer_term = officer_term.replace(
            '"', ""
        ).replace(
            "officers:", ""
        ).strip()

        results = session.query(
            Person,
            VendorOfficer,
            Vendor
        ).filter(
            Person.name == officer_term
        ).filter(
            Person.id == VendorOfficer.personid
        ).filter(
            VendorOfficer.vendorid == Vendor.id
        ).all()  # TODO fix to get .first() working

        output = results.pop()[2].name
        log.info("translating %s to %s", officer_term, output)

        return output

    # @cache.memoize(timeout=100000)
    def _find_number_of_documents(self, search_term):
        '''
        Redirect to the proper function for finding the total number of
        relevant documents for a given search.

        :param search_term: The query's search term.
        :type search_term: string
        :returns: int. The number of matching documents.
        '''

        if search_term == self.dc_contracts_query:  # TODO: Why have this?
            log.debug('if')
            # Get count for local DB
            return self._get_contracts_count()
        else:
            log.debug('else')
            # Get count for DocumentCloud output
            return self._query_document_cloud_count(search_term)

    def _translate_web_query_to_doc_cloud_query(self, data):
        '''
        Translates search input parameters into a request string for the
        DocumentCloud API.

        Uses 'projectid:1542-city-of-new-orleans-contracts' to restrict search
        to a certain project.

        :param data: The query parameters.
        :type data: dict
        :returns: string. The query string ready for the DocumentCloud API.
        '''

        query_builder = QueryBuilder()
        query_builder.add_text(data['search_input'])
        query_builder.add_term(
            self.dc_contracts_query.split(':')[0],
            self.dc_contracts_query.split(':')[1]
        )

        terms = ['vendor', 'department']

        for term in terms:
            query_value = data[term]
            if query_value != "":
                query_builder.add_term(term, query_value.upper())

        if len(data['officer']) > 0:
            officers = [data['officer']]
            vendor = self._translate_officer_to_vendor(officers[0])
            query_builder.add_term("vendor", vendor.upper())

            log.debug('%s  officers:', red_no_emoji)
            log.debug(officers)

        output = query_builder.get_query()

        log.debug('%s  output:', red_no_emoji)
        log.debug(output)

        return output


class QueryBuilder(object):

    '''Build a query for the DocumentCloud API. Uses Apache Lucene syntax.'''

    def __init__(self):
        '''Initialized as blank. Terms are stored in a dictionary.'''

        self.query = {}
        self.text = ""

    def add_term(self, term, value):
        '''
        Add a term to the dictionary. If term is updated it will just
        re-write the dictionary value.
        '''

        self.query[term] = value

    def add_text(self, text):
        '''Add a freetext component to the query (ex. 'playground').'''

        self.text = text

    def get_query(self):
        '''Translate the dictionary into a DocumentCloud query.'''

        output = ""

        for key in self.query.keys():
            output += '%s:"%s" ' % (key, self.query[key])

        output = output + self.text

        return output.strip()
