
"""
The web app that runs at vault.thelensnola.org/contracts.
"""

from flask import render_template, make_response
from contracts import (
    log,
    LENS_CSS,
    BANNER_CSS,
    CONTRACTS_CSS,
    LENS_JS,
    CONTRACTS_JS
)


class Views(object):

    '''Render views.'''

    def __init__(self):
        '''Initialize any self variables.'''

        pass

    def get_home(self, data):
        '''Render home page.'''

        # documents = data['documents']
        # number_of_documents = data['number_of_documents']
        # number_of_pages = data['number_of_pages']
        vendors = data['vendors']
        departments = data['departments']
        officers = data['officers']
        updated_date = data['updated_date']

        response = make_response(
            render_template(
                'index.html',
                vendors=vendors,
                departments=departments,
                # offset=0,
                # number_of_documents=number_of_documents,
                # number_of_pages=number_of_pages,
                # current_page=1,
                # documents=documents,
                officers=officers,
                updated_date=updated_date,
                lens_css=LENS_CSS,
                banner_css=BANNER_CSS,
                contracts_css=CONTRACTS_CSS,
                lens_js=LENS_JS,
                contracts_js=CONTRACTS_JS
            )
        )

        return response

    def get_search_page(self, data):
        '''Render search results page.'''

        log.debug('start of get_search_page')

        vendors = data['vendors']
        departments = data['departments']
        # offset = data['offset']
        number_of_documents = data['number_of_documents']
        status = data['status']
        number_of_pages = data['number_of_pages']
        current_page = data['current_page']
        documents = data['documents']
        officers = data['officers']
        # query = data['query']
        updated_date = data['updated_date']

        response = make_response(
            render_template(
                'search.html',
                vendors=vendors,
                departments=departments,
                # offset=offset,
                number_of_documents=number_of_documents,
                status=status,
                number_of_pages=number_of_pages,
                current_page=current_page,
                documents=documents,
                officers=officers,
                # query=query,
                updated_date=updated_date,
                lens_css=LENS_CSS,
                banner_css=BANNER_CSS,
                contracts_css=CONTRACTS_CSS,
                lens_js=LENS_JS,
                contracts_js=CONTRACTS_JS
            )
        )

        log.debug('end of get_search_page')

        return response

    def post_search_page(self, data):
        '''Render updated informatino to insert into search results page.'''

        number_of_documents = data['number_of_documents']
        status = data['status']
        number_of_pages = data['number_of_pages']
        current_page = data['current_page']
        docs = data['docs']
        query = data['query']
        vendor = data['vendor']

        response = make_response(
            render_template(
                'search.html',
                status=status,
                docs=docs,
                number_of_pages=number_of_pages,
                current_page=current_page,
                vendor=vendor,
                number_of_documents=number_of_documents,
                query=query,
                lens_css=LENS_CSS,
                banner_css=BANNER_CSS,
                contracts_css=CONTRACTS_CSS,
                lens_js=LENS_JS,
                contracts_js=CONTRACTS_JS
            )
        )

        return response

    def get_contract(self, data):
        '''Render the single contract page.'''

        doc_cloud_id = data['doc_cloud_id']
        updated_date = data['updated_date']

        response = make_response(
            render_template(
                'contract.html',
                doc_cloud_id=doc_cloud_id,
                updated_date=updated_date,
                lens_css=LENS_CSS,
                banner_css=BANNER_CSS,
                contracts_css=CONTRACTS_CSS,
                lens_js=LENS_JS,
                contracts_js=CONTRACTS_JS
            )
        )

        return response
