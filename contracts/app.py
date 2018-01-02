"""
The web app that runs at http://vault.thelensnola.org/contracts.

It allows the public to search City of New Orleans contracts that are posted
to the city's purchasing portal. It's a Flask application, and it follows the
structure from the Flask tutorials. The front end is built with Foundation.
It uses SQLAlchemy to connect to a PostgreSQL database.
"""

import os
import sys

from flask import Flask, request
# from flask.ext.cache import Cache

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from contracts.constants import log, RELOADER, DEBUG
from contracts.models import Models
from contracts.views import Views


app = Flask(__name__)
# cache = Cache(app, config={'CACHE_TYPE': 'simple'})


@app.route('/contracts/', methods=['GET'])
def intro():
    """
    Intro page for the web app.

    :returns: HTML. The homepage (/contracts/).
    """
    data = Models().get_home()
    view = Views().get_home(data)
    return view


@app.route('/contracts/search/', methods=['GET'])
def query_docs():
    """
    The main contract search page. Search parameters are specified in URL query
    string.

    :returns: HTML. The search page (/contracts/search/).
    """
    data, parameters = Models().get_search_page(request)
    view = Views().get_search_page(data, parameters)
    return view


@app.route('/contracts/contract/<string:doc_cloud_id>', methods=['GET'])
def contract(doc_cloud_id):
    """
    The single contract page. The contract ID is specified in the URL.

    :returns: HTML. The single contract page \
    (/contracts/contract/<doc_cloud_id>).
    """
    data = Models().get_contracts_page(doc_cloud_id)
    view = Views().get_contract(data)
    return view

if __name__ == '__main__':
    app.run(
        use_reloader=RELOADER,
        debug=DEBUG)
