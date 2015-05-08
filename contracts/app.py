"""
The web app that runs at vault.thelensnola.org/contracts
"""

from flask import Flask, request
# from flask.ext.cache import Cache
from contracts.models import Models
from contracts.views import Views
from contracts import (
    log
)

app = Flask(__name__)  # , template_folder=templates)
# cache = Cache(app, config={'CACHE_TYPE': 'simple'})


@app.route('/contracts/', methods=['GET'])
def intro():
    """
    Intro page for the web app
    """

    log.debug('index')

    data = Models().get_home()

    view = Views().get_home(data)

    return view


@app.route('/contracts/search/', methods=['GET', 'POST'])
def query_docs():
    """
    The main contract search.
    """

    log.debug('/search/')

    data = Models().get_search_page()

    log.debug('data')

    if request.method == 'GET':
        log.debug('/search/ GET')

        view = Views().get_search_page(data)

    if request.method == 'POST':
        log.debug('/search/ POST')

        view = Views().post_search_page(data)

    return view


@app.route('/contracts/contract/<string:doc_cloud_id>', methods=['GET'])
def contract(doc_cloud_id):
    """
    Request for a given contract.
    """

    log.debug('/contract/')

    # data = Models().get_contracts_page(doc_cloud_id)

    view = Views().get_contract(doc_cloud_id)

    return view


@app.route('/contracts/download/<string:docid>', methods=['GET', 'POST'])
def download(docid):
    """
    Download a requested contract
    """

    data = Models().get_download(docid)

    # view = Views().get_download(data)

    return data


# @app.route('/contracts/vendors/<string:q>', methods=['POST'])
# def vendors(q=None):
#     """
#     Get requested vendors from a query string and return a template.
#     Needs to be refactored using the flask query parser
#     """

#     data = Models().get_vendors_page(q)

#     view = Views().get_vendors(data)

#     return view


# @app.route('/contracts/officers/<string:q>', methods=['POST'])
# def officers(q=None):
#     """
#     Get requested officers. to do: say more.
#     """

#     data = Models().get_officers_page(q)

#     view = Views().get_officers(data)

#     return view


# @app.route('/contracts/departments/<string:q>', methods=['POST'])
# def departments(q=None):
#     """
#     Get requested departments
#     """

#     data = Models().get_departments_page(q)

#     view = Views().get_departments(data)

#     return view


if __name__ == '__main__':
    app.run(
        port=5000,
        use_reloader=True,
        debug=True
    )
