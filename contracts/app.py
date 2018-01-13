"""The web app that runs at http://vault.thelensnola.org/contracts.

It allows the public to search City of New Orleans contracts that are posted
to the city's purchasing portal. It's a Flask application, and it follows the
structure from the Flask tutorials. The front end is built with Foundation.
It uses SQLAlchemy to connect to a PostgreSQL database.
"""

from flask import Flask, request
# from flask.ext.cache import Cache

from contracts.models import Models
from contracts.views import Views
from contracts import RELOADER, DEBUG

app = Flask(__name__)
# cache = Cache(app, config={'CACHE_TYPE': 'simple'})  # TODO


@app.route('/contracts/', methods=['GET'])
def home_page():
    """Return the homepage.

    :returns: `flask.wrappers.Response`
    """
    data = Models().get_home()
    view = Views().get_home(data)

    return view


@app.route('/contracts/search/', methods=['GET'])
def search_results():
    """Return search results.

    Search parameters are specified in the URL query string.

    :returns: `flask.wrappers.Response`
    """
    data, parameters = Models().get_search_page(request)
    view = Views().get_search_page(data, parameters)

    return view


@app.route('/contracts/contract/<string:document_cloud_id>', methods=['GET'])
def contract_page(document_cloud_id):
    """Return a single contract.

    The contract ID is specified in the URL.

    :returns: `flask.wrappers.Response`
    """
    data = Models().get_contracts_page(document_cloud_id)
    view = Views().get_contract(data)

    return view

if __name__ == '__main__':
    app.run(use_reloader=RELOADER, debug=DEBUG)
