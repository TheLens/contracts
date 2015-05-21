"""
The web app that runs at vault.thelensnola.org/contracts.

It lets the public search City of New Orleans contracts that are posted to the
city's purchasing portal. It's just a Flask application, and it follows the
structure from the Flask tutorials. The front end is built with Foundation.
It uses SQLAlchemy to connect to a PostgreSQL database.
"""

import os
from flask import Flask, request
# from flask.ext.cache import Cache
from contracts.models import Models
from contracts.views import Views
from contracts import (
    log,
    RELOADER,
    DEBUG
)

app = Flask(__name__)  # , template_folder=templates)
# cache = Cache(app, config={'CACHE_TYPE': 'simple'})


@app.route('/contracts/', methods=['GET'])
def intro():
    """
    Intro page for the web app.

    :returns: HTML. The homepage (/contracts/).
    """

    log.debug('/')

    log.debug(os.environ)

    data = Models().get_home()

    log.debug('/ data:')
    # log.debug(data)

    view = Views().get_home(data)

    return view


@app.route('/contracts/search/', methods=['GET'])
def query_docs():
    """
    The main contract search page. Search parameters are specified in URL query
    string.

    :returns: HTML. The search page (/contracts/search/).
    """

    log.debug('/search/')

    data, parameter_data = Models().get_search_page(request)

    log.debug('/search/ data:')
    # log.debug(data)

    view = Views().get_search_page(data, parameter_data)

    log.debug('/search/ view:')

    return view


@app.route('/contracts/contract/<string:doc_cloud_id>', methods=['GET'])
def contract(doc_cloud_id):
    """
    The single contract page. The contract ID is specified in the URL.

    :returns: HTML. The single contract page \
    (/contracts/contract/<doc_cloud_id>).
    """

    log.debug('/contract/')

    data = Models().get_contracts_page(doc_cloud_id)

    view = Views().get_contract(data)

    return view


@app.route('/contracts/admin/<string:doc_cloud_id>', methods=['GET'])
def parserator(doc_cloud_id):
    """
    The parserator data entry page. The contract ID is specified in the URL.

    :returns: HTML. The single contract page \
    (/contracts/contract/<doc_cloud_id>).
    """

    log.debug('/contract/admin/')

    tags = Models().get_parserator_page(doc_cloud_id)

    view = Views().get_parserator(tags)

    return view


@app.route('/contracts/admin/tags/<string:doc_cloud_id>', methods=['POST'])
def tags(doc_cloud_id):
    """
    The UI is requesting tags for the doc_cloud_id

    :returns: HTML. The single contract page \
    (/contracts/contract/<doc_cloud_id>).
    """

    log.debug('/contract/admin/tags')

    # to do : deal with cases when there are no tags yet. parserator takes 15 minutes.
    tags = Models().get_tags_for_doc_cloud_id(doc_cloud_id)

    view = Views().get_parserator(tags)

    return view


@app.route('/contracts/download/<string:docid>', methods=['GET', 'POST'])
def download(docid):
    """
    Download a requested contract. This is triggered during 'download' clicks.

    :returns: PDF. The contract's PDF file.
    """

    log.debug('/download')

    data = Models().get_download(docid)

    log.debug(data)

    # view = Views().get_download(data)

    return data


# @cache.memoize(timeout=5000)
@app.route("/contracts/input", methods=['POST'])
def searchbar_input():
    '''
    Receives a POST call from the autocomplete dropdown and returns a dict
    of suggestions. Query is stored in q={} part of URL.

    :param q: The search bar input.
    :type q: string
    :returns: A dict of matching suggestions.
    '''

    term = request.args.get('q')

    log.debug('term: %s', term)

    data = Models().searchbar_input(term)

    return data

if __name__ == '__main__':
    app.run(
        use_reloader=RELOADER,
        debug=DEBUG
    )
