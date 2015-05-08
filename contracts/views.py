
"""
The web app that runs at vault.thelensnola.org/contracts
"""

from flask import render_template, make_response
from contracts import (
    LENS_CSS,
    BANNER_CSS,
    CONTRACTS_CSS,
    LENS_JS,
    CONTRACTS_JS
)


class Views(object):

    '''docstring'''

    def __init__(self):
        '''docstring'''

        pass

    def get_home(self, data):
        '''docstring'''

        docs = data['docs']
        total_docs = data['total_docs']
        pages = data['pages']
        vendors = data['vendors']
        departments = data['departments']
        officers = data['officers']
        updated_date = data['updated_date']

        response = make_response(
            render_template(
                'index.html',
                vendors=vendors,
                departments=departments,
                offset=0,
                totaldocs=total_docs,
                pages=pages,
                page=1,
                docs=docs,
                officers=officers,
                updated=updated_date,
                lens_css=LENS_CSS,
                banner_css=BANNER_CSS,
                contracts_css=CONTRACTS_CSS,
                lens_js=LENS_JS,
                contracts_js=CONTRACTS_JS
            )
        )

        return response

    def get_search_page(self, data):
        '''docstring'''

        vendors = data['vendors']
        departments = data['departments']
        offset = data['offset']
        totaldocs = data['totaldocs']
        status = data['status']
        pages = data['pages']
        page = data['page']
        docs = data['docs']
        officers = data['officers']
        query = data['query']
        updated = data['updated']

        response = make_response(
            render_template(
                'index.html',
                vendors=vendors,
                departments=departments,
                offset=offset,
                totaldocs=totaldocs,
                status=status,
                pages=pages,
                page=page,
                docs=docs,
                officers=officers,
                query=query,
                updated=updated,
                lens_css=LENS_CSS,
                banner_css=BANNER_CSS,
                contracts_css=CONTRACTS_CSS,
                lens_js=LENS_JS,
                contracts_js=CONTRACTS_JS
            )
        )

        return response

    def post_search_page(self, data):
        '''docstring'''

        totaldocs = data['totaldocs']
        status = data['status']
        pages = data['pages']
        page = data['page']
        docs = data['docs']
        query = data['query']
        vendor = data['vendor']

        response = make_response(
            render_template(
                'index.html',
                status=status,
                docs=docs,
                pages=pages,
                page=page,
                vendor=vendor,
                totaldocs=totaldocs,
                query=query,
                lens_css=LENS_CSS,
                banner_css=BANNER_CSS,
                contracts_css=CONTRACTS_CSS,
                lens_js=LENS_JS,
                contracts_js=CONTRACTS_JS
            )
        )

        return response

    def get_contract(self, doc_cloud_id):

        response = make_response(
            render_template(
                'contract.html',
                doc_cloud_id=doc_cloud_id,
                lens_css=LENS_CSS,
                banner_css=BANNER_CSS,
                contracts_css=CONTRACTS_CSS,
                lens_js=LENS_JS,
                contracts_js=CONTRACTS_JS
            )
        )

        return response

    # def get_vendors(self, vendors):
    #     '''docstring'''

    #     response = make_response(
    #         render_template(
    #             'select.html',
    #             options=vendors
    #         )
    #     )

    #     return response

    # def get_officers(self, officers):
    #     '''docstring'''

    #     response = make_response(
    #         render_template(
    #             'select.html',
    #             options=officers
    #         )
    #     )

    #     return response

    # def get_departments(self, departments):
    #     '''docstring'''

    #     response = make_response(
    #         render_template(
    #             'select.html',
    #             options=departments
    #         )
    #     )

    #     return response
