
"""
The web app that runs at vault.thelensnola.org/contracts.
"""

from flask import render_template, make_response
from contracts import (
    log,
    LENS_CSS,
    BANNER_CSS,
    CONTRACTS_CSS,
    DOWNLOAD_JS,
    LENS_JS,
    RESULTS_JS,
    SEARCH_JS
)


class Views(object):

    '''Render views.'''

    @staticmethod
    def get_home(data):
        '''Render home page.'''

        vendors = data['vendors']
        departments = data['departments']
        officers = data['officers']
        updated_date = data['updated_date']

        response = make_response(
            render_template(
                'index.html',
                vendors=vendors,
                departments=departments,
                officers=officers,
                updated_date=updated_date,
                lens_css=LENS_CSS,
                banner_css=BANNER_CSS,
                contracts_css=CONTRACTS_CSS,
                lens_js=LENS_JS,
                search_js=SEARCH_JS
            )
        )

        return response

    @staticmethod
    def get_search_page(data, parameter_data):
        '''Render search results page.'''

        log.debug('start of get_search_page')
        log.debug('current_page: %d', data['current_page'])

        vendors = data['vendors']
        departments = data['departments']
        number_of_documents = data['number_of_documents']
        number_of_pages = data['number_of_pages']
        current_page = data['current_page']
        documents = data['documents']
        officers = data['officers']
        updated_date = data['updated_date']
        results_language = data['results_language']

        response = make_response(
            render_template(
                'search.html',
                parameter_data=parameter_data,
                vendors=vendors,
                departments=departments,
                number_of_documents=number_of_documents,
                results_language=results_language,
                number_of_pages=number_of_pages,
                current_page=current_page,
                documents=documents,
                officers=officers,
                updated_date=updated_date,
                lens_css=LENS_CSS,
                banner_css=BANNER_CSS,
                contracts_css=CONTRACTS_CSS,
                download_js=DOWNLOAD_JS,
                lens_js=LENS_JS,
                results_js=RESULTS_JS,
                search_js=SEARCH_JS
            )
        )

        log.debug('end of get_search_page')

        return response

    @staticmethod
    def get_contract(data):
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
                download_js=DOWNLOAD_JS,
                lens_js=LENS_JS
            )
        )

        return response
