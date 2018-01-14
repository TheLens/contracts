'''The web app that runs at vault.thelensnola.org/contracts.'''

import time

# from flask.ext.cache import Cache

from contracts.lib.results_language import ResultsLanguage
from contracts.db import (
    Vendor,
    Department,
    Contract,
    Person,
    VendorOfficer
)
from contracts import app_log as log, SESSION
from pythondocumentcloud import DocumentCloud

# cache = Cache(app, config={'CACHE_TYPE': 'simple'})


class Models(object):

    '''doctstring'''

    def __init__(self):
        '''docstring'''
        self.pagelength = 10  # DocumentCloud API default is 10
        self.dc_query = 'projectid:1542-city-of-new-orleans-contracts'
        self.document_cloud_client = DocumentCloud()

        log.debug('%d documents', self.pagelength)

    def __str__(self):
        return '{}'.format(self.__class__.__name__)

    def __repr__(self):
        return '{}()'.format(self.__class__.__name__)

    def get_home(self):
        '''
        Gather data necessary for the homepage (/contracts/).

        :returns: dict. A dict with data for dropdowns and dates.
        '''
        # Find the last updated date for footer
        updated_date = time.strftime("%b. %-d, %Y")

        # Correct for AP Style
        updated_date = updated_date.replace('Mar.', 'March')
        updated_date = updated_date.replace('Apr.', 'April')
        updated_date = updated_date.replace('May.', 'May')
        updated_date = updated_date.replace('Jun.', 'June')
        updated_date = updated_date.replace('Jul.', 'July')

        data = {
            'departments':         self.get_departments(),  # Get a list of departments for dropdown
            'documents':           self.query_document_cloud(self.dc_query, page=1),
            'number_of_documents': self.pagelength,
            'officers':            self.get_officers(),        # Get a list of officers for dropdown
            'results_language':    "Showing {} most recent contracts.".format(self.pagelength),
            'updated_date':        updated_date,
            'vendors':             self.get_vendors()           # Get a list of vendors for dropdown
        }

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
        data = self.parse_query_string(request)

        log.debug('User search parameters: %s', data)

        # Transform query parameters into string for DocumentCloud API.
        search_term = self.translate_web_query_to_dc_query(data)

        # Get a list of contracts by querying our project on DocCloud:
        documents = self.query_document_cloud(search_term, page=data['current_page'])

        # TODO: A second search?
        number_of_documents = self.find_number_of_documents(search_term)
        log.debug('%d documents', number_of_documents)
        log.debug('%d documents', len(documents))

        number_of_pages = (number_of_documents / self.pagelength) + 1  # Zero-indexing

        log.debug('Found {:,} documents across {:,} pages'.format(number_of_documents, number_of_pages))

        updated_date = time.strftime("%b. %-d, %Y")

        # Correct for AP Style
        updated_date = updated_date.replace('Mar.', 'March')
        updated_date = updated_date.replace('Apr.', 'April')
        updated_date = updated_date.replace('May.', 'May')
        updated_date = updated_date.replace('Jun.', 'June')
        updated_date = updated_date.replace('Jul.', 'July')

        output_data = {
            'current_page':        data['current_page'],
            'departments':         self.get_departments(),
            'documents':           documents,
            'number_of_documents': number_of_documents,
            'number_of_pages':     number_of_pages,
            'officers':            self.get_officers(),
            'results_language':    ResultsLanguage(data, number_of_documents).main(),
            'search_input':        data['search_input'],
            'updated_date':        updated_date,
            'vendors':             self.get_vendors()
        }

        return output_data, data

    def get_contracts_page(self, doc_cloud_id):
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

        documents = self.query_document_cloud('document:"%s"' % doc_cloud_id)

        data = {
            'doc_cloud_id': doc_cloud_id,
            'pdf_url':      documents[0].resources.pdf,
            'updated_date': updated_date
        }

        return data

    @staticmethod
    def parse_query_string(request):
        '''
        Receives URL query string parameters and returns as dict.

        :param request: A (Flask object?) containing query string.
        :type request: dict?
        :returns: dict. The query string parameters entered by the user.
        '''
        current_page = request.args.get('page')
        if current_page is None or current_page == '':
            current_page = 1

        data = {
            'search_input': request.args.get('query'),
            'vendor':       request.args.get('vendor'),
            'department':   request.args.get('department'),
            'officer':      request.args.get('officer'),
            'current_page': int(current_page)
        }

        # Change any missing parameters to 0-length string
        for key in data:
            if data[key] is None:
                data[key] = ''

        return data

    # @cache.memoize(timeout=900)
    def query_document_cloud(self, search_term, page=1):
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

        log.debug('DocumentCloud search: %s', search_term)
        log.debug('Showing %d results per page, page %d', self.pagelength, page)

        output = self.document_cloud_client.documents.search(
            search_term, page=page, per_page=self.pagelength)

        log.debug('Found documents: %s', output)

        return output

    # @cache.memoize(timeout=900)
    def query_document_cloud_count(self, search_term):
        '''
        Finds the number of documents in DocumentCloud project that
        match this query.

        :param search_term: The search term for DocumentCloud API query.
        :type search_term: string
        :returns: int. The number of records that match this query.
        '''
        return self.document_cloud_client.documents.search_count(search_term)

    @staticmethod
    def translate_to_doc_cloud_form(documents):
        '''
        In the database each row for contracts has an ID which is different
        from the doc_cloud_id on DocumentCloud. This just translates rows so
        that their ID is equal to the doc_cloud_id. It's a bit awkward and
        should probably be refactored away at some point.

        :param documents: A list of documents (from where?).
        :type documents: list
        :returns: list. A list of documents, with corrected IDs (how?).
        '''
        for document in documents:
            document.id = document.doc_cloud_id

        return documents

    # @cache.memoize(timeout=900)
    def get_contracts(self, offset=0, limit=None):
        '''
        Query the database in reverse chronological order. Specify the number
        of recent contracts with offset and limit values.

        :param offset: The number of pages to offset database query.
        :type offset: int
        :param limit: The number of records to return.
        :type limit: int
        :returns: list. (?) The contracts that matched the query.
        '''
        # sn = sessionmaker(bind=self.engine)
        # session = sn()

        offset *= self.pagelength

        contracts = (SESSION.query(Contract)
                     .order_by(Contract.dateadded.desc())
                     .offset(offset)
                     .limit(limit)
                     .all())

        SESSION.close()

        contracts = self.translate_to_doc_cloud_form(contracts)

        log.debug('Contracts: %s', contracts)

        return contracts

    # @cache.memoize(timeout=100000)
    def get_contracts_count(self):
        '''
        Query the count of all contracts in database.

        :returns: int. The total number of contracts in the database.
        '''
        # sn = sessionmaker(bind=self.engine)
        # session = sn()

        count = SESSION.query(Contract).count()

        SESSION.close()

        return count

    # @cache.memoize(timeout=100000)  # cache good for a day or so
    def get_vendors(self):
        '''
        Query all vendors in the database linked to a contract.

        :returns: list. (?) The vendors that are linked to a contract.
        '''

        # sn = sessionmaker(bind=self.engine)
        # session = sn()

        vendors = (SESSION.query(Vendor.name)
                   .filter(Vendor.id == Contract.vendorid)
                   .distinct()
                   .order_by(Vendor.name))

        SESSION.close()

        return [vendor[0].strip() for vendor in vendors]

    # @cache.memoize(timeout=100000)  # cache good for a day or so
    def get_departments(self):
        '''
        Query all departments in the database.

        :returns: list. All departments in our database.
        '''

        # sn = sessionmaker(bind=self.engine)
        # session = sn()

        departments = (SESSION.query(Department.name)
                       .distinct()
                       .order_by(Department.name)
                       .all())

        SESSION.close()

        return [department[0].strip() for department in departments]

    # @cache.memoize(timeout=100000)  # cache good for a day or so
    def get_officers(self, vendor=None):
        '''
        Get officers for a given vendor.

        :param vendor: The vendor to check on.
        :type vendor: string
        :returns: list. A list of officers listed under the vendor company in \
        the Secretary of State's database.
        '''

        # sn = sessionmaker(bind=self.engine)
        # session = sn()

        officers = []

        if vendor is None:
            officers = (SESSION.query(VendorOfficer, Person)
                        .filter(VendorOfficer.personid == Person.id)
                        .order_by(Person.name))
        else:
            vendor = vendor.replace("vendor:", "")
            officers = (SESSION.query(VendorOfficer, Person, Vendor)
                        .filter(VendorOfficer.personid == Person.id)
                        .filter(VendorOfficer.vendorid == Vendor.id)
                        .filter(Vendor.name == vendor)
                        .all())

        SESSION.close()

        return sorted(list(set([o[1].name for o in officers])))

    # @cache.memoize(timeout=100000)
    def translate_officer_to_vendor(self, officer_term):
        '''
        Translates a request for an officer to a request for a vendor
        associated with a given officer.

        :param officer_term: The name of the officer.
        :type officer_term: string
        :returns: ???
        '''

        # sn = sessionmaker(bind=self.engine)
        # session = sn()

        officer_term = officer_term.replace('"', "").replace("officers:", "").strip()

        results = (SESSION.query(Person, VendorOfficer, Vendor)
                   .filter(Person.name == officer_term)
                   .filter(Person.id == VendorOfficer.personid)
                   .filter(VendorOfficer.vendorid == Vendor.id)
                   .all())  # todo fix to get .first() working

        output = results.pop()[2].name
        log.info("Translating %s to %s", officer_term, output)

        SESSION.close()

        return output

    # @cache.memoize(timeout=100000)
    def find_number_of_documents(self, search_term):
        '''
        Redirect to the proper function for finding the total number of
        relevant documents for a given search.

        :param search_term: The query's search term.
        :type search_term: string
        :returns: int. The number of matching documents.
        '''
        if search_term == self.dc_query:
            # Get count for local DB:
            return self.get_contracts_count()
        else:
            # Get count for DocumentCloud output:
            return self.query_document_cloud_count(search_term)

    def translate_web_query_to_dc_query(self, data):
        '''
        Translates search input parameters into a request string for the
        DocumentCloud API, which utilizes the Apache Lucene syntax.

        Use 'projectid:1542-city-of-new-orleans-contracts' to restrict search
        to our project.

        :param data: The query parameters.
        :type data: dict
        :returns: string. The query string ready for the DocumentCloud API.
        '''
        query_builder = QueryBuilder()
        query_builder.add_text(data['search_input'])
        query_builder.add_term(
            self.dc_query.split(':')[0],
            self.dc_query.split(':')[1]
        )

        terms = ['vendor', 'department']

        for term in terms:
            query_value = data[term]
            if query_value != "":
                query_builder.add_term(term, query_value.upper())

        if len(data['officer']) > 0:
            officers = [data['officer']]
            log.debug('Officers: %s', officers)

            vendor = self.translate_officer_to_vendor(officers[0])
            query_builder.add_term("vendor", vendor.upper())

        return query_builder.get_query()


class QueryBuilder(object):
    '''
    Build a query for the DocumentCloud API.
    '''

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
        '''
        Add a freetext component to the query (ex. 'playground').
        '''
        self.text = text

    def get_query(self):
        '''
        Translate the dictionary into a DocumentCloud query.
        '''
        output = ""

        for key in self.query.keys():
            # TODO: Is trailing space for Lucene syntax?
            output += '%s:"%s" ' % (key, self.query[key])

        output = output + self.text

        return output.strip()
