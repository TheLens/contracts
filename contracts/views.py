
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
    RESULTS_JS,
    SEARCH_JS,
    PARSERATOR_JS
)


class Views(object):

    '''Render views.'''

    @staticmethod
    def get_home(data):
        '''
        Renders the homepage (/contracts/).

        :param data: Data for the homepage.
        :type data: dict
        :returns: HTML. Rendered and ready for display to the user.
        '''
        response = make_response(
            render_template(
                'index.html',
                vendors=data['vendors'],
                departments=data['departments'],
                officers=data['officers'],
                documents=data['documents'],
                number_of_documents=data['number_of_documents'],
                results_language=data['results_language'],
                updated_date=data['updated_date'],
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
        '''
        Renders the search results page (/contracts/search/).

        :param data: Data in response to the search request.
        :type data: dict
        :param parameter_data: Search parameter that was originally sent.
        :type parameter_data: dict
        :returns: HTML. Rendered and ready for display.
        '''
        log.debug('Current page: %d', data['current_page'])

        response = make_response(
            render_template(
                'search.html',
                parameter_data=parameter_data,
                vendors=data['vendors'],
                departments=data['departments'],
                number_of_documents=data['number_of_documents'],
                results_language=data['results_language'],
                number_of_pages=data['number_of_pages'],
                current_page=data['current_page'],
                documents=data['documents'],
                officers=data['officers'],
                updated_date=data['updated_date'],
                lens_css=LENS_CSS,
                banner_css=BANNER_CSS,
                contracts_css=CONTRACTS_CSS,
                lens_js=LENS_JS,
                results_js=RESULTS_JS,
                search_js=SEARCH_JS
            )
        )

        return response

    @staticmethod
    def get_contract(data):
        '''
        Renders the single contract page (/contracts/contract/).

        :param data: Data for the page.
        :type data: dict
        :returns: HTML. Rendered and ready for display.
        '''

        response = make_response(
            render_template(
                'contract.html',
                data=data,
                lens_css=LENS_CSS,
                banner_css=BANNER_CSS,
                contracts_css=CONTRACTS_CSS,
                lens_js=LENS_JS
            )
        )

        return response

    @staticmethod
    def get_admin_home(data):
        '''
        Renders the admin home page (/contracts/admin/).

        :param data: Data for the page.
        :type data: dict
        :returns: HTML. Rendered and ready for display.
        '''

        response = make_response(
            render_template(
                'admin.html',
                lens_css=LENS_CSS,
                banner_css=BANNER_CSS,
                contracts_css=CONTRACTS_CSS,
                lens_js=LENS_JS,
                parserator_js=PARSERATOR_JS
            )
        )

        return response

    @staticmethod
    def get_parserator(tags=None):
        '''
        Renders the parserator page (/contracts/admin/).

        :param data: Data for the page.
        :type data: dict
        :returns: HTML. Rendered and ready for display.
        '''

        response = make_response(
            render_template(
                'parserator.html',
                doc_cloud_id=tags['doc_cloud_id'],
                tags=tags,
                lens_css=LENS_CSS,
                banner_css=BANNER_CSS,
                contracts_css=CONTRACTS_CSS,
                lens_js=LENS_JS,
                parserator_js=PARSERATOR_JS
            )
        )

        return response
