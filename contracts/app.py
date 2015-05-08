"""
The web app that runs at vault.thelensnola.org/contracts
"""
# import sys
from flask import Flask, request
from sqlalchemy import create_engine
# from flask.ext.cache import Cache
from documentcloud import DocumentCloud
from contracts.models import Models
from contracts.views import Views
from contracts import (
    CONNECTION_STRING,
    log
)

# settings = Settings()

PAGELENGTH = 8

app = Flask(__name__)  # , template_folder=templates)
# cache = Cache(app, config={'CACHE_TYPE': 'simple'})
documentCloudClient = DocumentCloud()

engine = create_engine(CONNECTION_STRING)

dc_query = 'projectid: "1542-city-of-new-orleans-contracts"'


@app.route('/contracts/', methods=['GET'])
def intro():
    """
    Intro page for the web app
    """

    log.debug('index')

    data = Models().get_home()

    view = Views().get_home(data)

    return view


@app.route('/contracts/download/<string:docid>', methods=['POST', 'GET'])
def download(docid):
    """
    Download a requested contract
    """

    data = Models().get_download(docid)

    # view = Views().get_download(data)

    return data


@app.route('/contracts/vendors/<string:q>', methods=['POST'])
def vendors(q=None):
    """
    Get requested vendors from a query string and return a template.
    Needs to be refactored using the flask query parser
    """

    data = Models().get_vendors_page(q)

    view = Views().get_vendors(data)

    return view


@app.route('/contracts/officers/<string:q>', methods=['POST'])
def officers(q=None):
    """
    Get requested officers. to do: say more.
    """

    data = Models().get_officers_page(q)

    view = Views().get_officers(data)

    return view


@app.route('/contracts/departments/<string:q>', methods=['POST'])
def departments(q=None):
    """
    Get requested departments
    """

    data = Models().get_departments_page(q)

    view = Views().get_departments(data)

    return view


@app.route('/contracts/contract/<string:doc_cloud_id>', methods=['GET'])
def contract(doc_cloud_id):
    """
    Request for a given contract
    """

    data = Models().get_contracts_page(doc_cloud_id)

    view = Views().get_contracts(data)

    return view


@app.route('/contracts/search', methods=['POST', 'GET'])
def query_docs():
    """
    The main contract search.
    """

    log.debug('search')

    data = Models().get_search_page()

    if request.method == 'GET':
        view = Views().get_search_page(data)

    if request.method == 'POST':
        view = Views().post_search_page(data)

    return view


if __name__ == '__main__':
    app.run(
        port=5000,
        use_reloader=True,
        debug=True
    )
