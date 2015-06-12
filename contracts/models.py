
'''
The web app that runs at vault.thelensnola.org/contracts.
'''

import time
import json
import urllib2
import httplib
from flask import make_response
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
# from flask.ext.cache import Cache
from contracts.lib.results_language import ResultsLanguage
from contracts.db import (
    Vendor,
    Department,
    Contract,
    Person,
    VendorOfficer
)
from pythondocumentcloud import DocumentCloud
from contracts import CONNECTION_STRING, log
from contracts.lib.parserator_utils import get_document_page, spanify

# cache = Cache(app, config={'CACHE_TYPE': 'simple'})


class Models(object):

    '''doctstring'''

    def __init__(self):
        '''docstring'''

        self.engine = create_engine(CONNECTION_STRING)
        self.pagelength = 10  # DocumentCloud API default is 10
        self.dc_query = 'projectid:1542-city-of-new-orleans-contracts'
        self.document_cloud_client = DocumentCloud()

    def get_home(self):
        '''
        Gather data necessary for the homepage (/contracts/).

        :returns: dict. A dict with data for dropdowns and dates.
        '''

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
        updated_date = time.strftime("%b. %-d, %Y")

        # Correct for AP Style
        updated_date = updated_date.replace('Mar.', 'March')
        updated_date = updated_date.replace('Apr.', 'April')
        updated_date = updated_date.replace('May.', 'May')
        updated_date = updated_date.replace('Jun.', 'June')
        updated_date = updated_date.replace('Jul.', 'July')

        data['updated_date'] = updated_date
        log.debug(data)

        '''
        Getting 10 most recent contracts
        '''
        documents = self.get_contracts(limit=self.pagelength)
        log.debug(documents)

        # Fixing IDs:
        documents = self.translate_to_doc_cloud_form(documents)
        log.debug(documents)

        number_of_documents = self.pagelength
        log.debug(number_of_documents)

        data['number_of_documents'] = number_of_documents
        data['results_language'] = (
            "Showing %d most recent sales." % number_of_documents)
        data['documents'] = documents

        log.debug('Done collecting home data')

        return data

    def get_search_page(self, request):
        '''
        Gets the data necessary for the search page (/contracts/search/).

        :param request: The search parameters supplied by the user.
        :type request: dict
        :returns: dict. Two dicts: one for newly gather data, and the other \
        an altered version of the incoming search parameters.
        '''

        log.debug('start get_search_page')

        # Extract search parameters (text input and dropdown selections)
        data = self.parse_query_string(request)

        log.debug(data)

        incoming_data = data

        # Transform query parameters into string for DocumentCloud API.
        search_term = self.translate_web_query_to_dc_query(data)

        log.debug(search_term)

        if search_term == self.dc_query:  # If no search input
            log.debug('No search parameters entered.')

            # Get a list of contracts from local DB, without any search filter:
            documents = self.get_contracts(limit=self.pagelength)

            log.debug(documents)

            # Fixing IDs:
            documents = self.translate_to_doc_cloud_form(documents)

            log.debug(documents)
        else:
            log.debug('Some search parameters entered.')

            # Get a list of contracts by querying our project on DocCloud:
            documents = self.query_document_cloud(
                search_term, page=data['current_page'])

            log.debug(documents)

        number_of_documents = self.find_number_of_documents(search_term)

        log.debug(number_of_documents)

        number_of_pages = number_of_documents / self.pagelength

        # Increment by 1 to correct zero-indexing:
        number_of_pages = number_of_pages + 1
        log.debug('number_of_pages: %d', number_of_pages)

        updated_date = time.strftime("%b. %-d, %Y")

        # Correct for AP Style
        updated_date = updated_date.replace('Mar.', 'March')
        updated_date = updated_date.replace('Apr.', 'April')
        updated_date = updated_date.replace('May.', 'May')
        updated_date = updated_date.replace('Jun.', 'June')
        updated_date = updated_date.replace('Jul.', 'July')

        vendors = self.get_vendors()
        officers = self.get_officers()
        departments = self.get_departments()

        output_data = {}

        output_data['search_input'] = data['search_input']
        output_data['vendors'] = vendors
        output_data['departments'] = departments
        output_data['officers'] = officers
        output_data['number_of_documents'] = number_of_documents
        output_data['results_language'] = ResultsLanguage(
            data, number_of_documents).main()
        output_data['number_of_pages'] = number_of_pages
        output_data['current_page'] = data['current_page']
        output_data['documents'] = documents
        output_data['updated_date'] = updated_date

        log.debug('end of get_search_page')
        # log.debug(output_data)
        # log.debug('current_page: %d', output_data['current_page'])

        return output_data, incoming_data  # TODO: consolidate this

    @staticmethod
    def get_contracts_page(doc_cloud_id):
        '''
        Get data necessary for the single contract page. This only gets the
        updated date, so it is mostly a placeholder for now.

        :param doc_cloud_id: The single contract's uniquey DocumentCloud ID.
        :type doc_cloud_id: string
        :returns: dict. A dict with the updated date.
        '''

        data = {}

        updated_date = time.strftime("%b. %-d, %Y")

        # Correct for AP Style
        updated_date = updated_date.replace('Mar.', 'March')
        updated_date = updated_date.replace('Apr.', 'April')
        updated_date = updated_date.replace('May.', 'May')
        updated_date = updated_date.replace('Jun.', 'June')
        updated_date = updated_date.replace('Jul.', 'July')

        data['doc_cloud_id'] = doc_cloud_id
        data['updated_date'] = updated_date

        return data

    def get_admin_home(self):
        '''
        This is a page that shows a contract. If this contract has been
        parsed then the tags will be on s3. If the contract has not been
        parsed then there will be no prefilled tags visible

        :param doc_cloud_id: The single contract's uniquey DocumentCloud ID.
        :type doc_cloud_id: string
        :returns: dict. A dict with the updated date.
        '''

        # check s3 for the tags for a given contract
        # return those tags to the view.

        data = None

        return data

    def get_parserator_page(self, doc_cloud_id):
        '''
        This is a page that shows a contract. If this contract has been
        parsed then the tags will be on s3. If the contract has not been
        parsed then there will be no prefilled tags visible

        :param doc_cloud_id: The single contract's uniquey DocumentCloud ID.
        :type doc_cloud_id: string
        :returns: dict. A dict with the updated date.
        '''

        # check s3 for the tags for a given contract
        # return those tags to the view.

        tags = {'doc_cloud_id': doc_cloud_id}

        return tags

    def do_tags_exist(self, doc_cloud_id):
        # url = (
        #     "https://s3-us-west-2.amazonaws.com/lensnola/contracts/" +
        #     "contract_amounts/computer_labels/%s" % doc_cloud_id
        # )

        c = httplib.HTTPConnection('www.abc.com')
        c.request("HEAD", '')
        if c.getresponse().status == 200:
            return True
        else:
            return False

    def get_tags_for_doc_cloud_id(self, doc_cloud_id, request):
        url = (
            "https://s3-us-west-2.amazonaws.com/lensnola/contracts/" +
            "contract_amounts/computer_labels/%s" % doc_cloud_id
        )

        page = request.args.get('page')
        page_text = get_document_page(doc_cloud_id, page)

        try:
            response = urllib2.urlopen(url)
            computer_generated_tags = response.read()
            computer_generated_tags = json.loads(computer_generated_tags)
        except urllib2.HTTPError, e:
            log.debug("HTTPError error %s" % str(e.code))
            computer_generated_tags = None
        return spanify(page_text, page, computer_generated_tags)

    def get_download(self, doc_cloud_id):
        '''
        ???

        :param doc_cloud_id: The unique ID for this contract in DocumentCloud.
        :type doc_cloud_id: string
        :returns: PDF. The PDF file for this contract (?).
        '''

        docs = self.query_document_cloud('document:"%s"' % doc_cloud_id)
        response = make_response(docs.pop().pdf)
        disposition_header = "attachment; filename=%s.pdf" % doc_cloud_id
        response.headers["Content-Disposition"] = disposition_header

        return response

    @staticmethod
    def parse_query_string(request):
        '''
        Receives URL query string parameters and returns as dict.

        :param request: A (Flask object?) containing query string.
        :type request: dict?
        :returns: dict. The query string parameters entered by the user.
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

        log.debug('query_document_cloud output:')
        log.debug(output)

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

        log.debug(
            'query_document_cloud_count with search_term: %s', search_term)

        output = self.document_cloud_client.documents.search_count(search_term)

        log.debug('output')
        log.debug(output)

        return output

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

        log.debug('translate_to_doc_cloud_form')

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
        '''
        Query the count of all contracts in database.

        :returns: int. The total number of contracts in the database.
        '''

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
        '''
        Query all vendors in the database linked to a contract.

        :returns: list. (?) The vendors that are linked to a contract.
        '''

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
        '''
        Query all departments in the database.

        :returns: list. All departments in our database.
        '''

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
        '''
        Get officers for a given vendor.

        :param vendor: The vendor to check on.
        :type vendor: string
        :returns: list. A list of officers listed under the vendor company in \
        the Secretary of State's database.
        '''

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
            # print officers
            return sorted(officers)

    # @cache.memoize(timeout=100000)
    def translate_officer_to_vendor(self, officer_term):
        '''
        Translates a request for an officer to a request for a vendor
        associated with a given officer.

        :param officer_term: The name of the officer.
        :type officer_term: string
        :returns: ???
        '''

        sn = sessionmaker(bind=self.engine)
        session = sn()

        officer_term = officer_term.replace(
            '"', "").replace("officers:", "").strip()

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
        ).all()  # todo fix to get .first() working

        output = results.pop()[2].name
        log.info("translating %s to %s", officer_term, output)

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

        log.debug('find_number_of_documents')

        if search_term == self.dc_query:
            log.debug('if')
            # Get count for local DB:
            return self.get_contracts_count()
        else:
            log.debug('else')
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

        log.debug('translate_web_query_to_dc_query')

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
            log.debug('\xF0\x9F\x9A\xAB  officers:')
            log.debug(officers)
            vendor = self.translate_officer_to_vendor(officers[0])
            query_builder.add_term("vendor", vendor.upper())

        output = query_builder.get_query()

        log.debug('\xF0\x9F\x9A\xAB  output:')
        log.debug(output)

        return output


class QueryBuilder(object):
    '''
    Build a query for the DocumentCloud API.
    '''

    def __init__(self):
        '''
        Initialized as blank. Terms are stored in a dictionary.
        '''

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
