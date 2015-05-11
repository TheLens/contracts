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

    log.debug('/')

    data = Models().get_home()

    log.debug('/ data:')
    # log.debug(data)

    view = Views().get_home(data)

    return view


@app.route('/contracts/search/', methods=['GET'])
def query_docs():
    """
    The main contract search.
    """

    log.debug('/search/')

    if request.method == 'GET':
        log.debug('/search/ GET')

        data = Models().get_search_page(request)

        log.debug('/search/ data:')
        # log.debug(data)

        view = Views().get_search_page(data)

        log.debug('/search/ view:')

        return view


@app.route('/contracts/contract/<string:doc_cloud_id>', methods=['GET'])
def contract(doc_cloud_id):
    """
    Request for a given contract.
    """

    log.debug('/contract/')

    data = Models().get_contracts_page(doc_cloud_id)

    view = Views().get_contract(data)

    return view


@app.route('/contracts/download/<string:docid>', methods=['GET', 'POST'])
def download(docid):
    """
    Download a requested contract
    """

    log.debug('/download')

    data = Models().get_download(docid)

    log.debug(data)

    # view = Views().get_download(data)

    return data


if __name__ == '__main__':
    app.run(
        port=5000,
        use_reloader=True,
        debug=True
    )
