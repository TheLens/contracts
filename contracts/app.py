'''
Flask app that routes URL requests to models.py and renders in views.py.
'''

from flask import Flask, request
# from flask.ext.cache import Cache

from contracts.models import Models
from contracts.views import Views
from contracts import RELOADER, DEBUG

app = Flask(__name__)
# cache = Cache(app, config={'CACHE_TYPE': 'simple'})


@app.route('/contracts/', methods=['GET'])
def intro():
    '''
    Intro page for the web app.

    :returns: HTML. The homepage (/contracts/).
    '''

    data = Models().get_home()  # Queries DocumentCloud only.
    view = Views().get_home(data)

    return view


@app.route('/contracts/search/', methods=['GET'])
def query_docs():
    '''
    The main contract search page. Search parameters are specified in URL query
    string.

    :returns: HTML. The search page (/contracts/search/).
    '''

    data = Models().get_search_page(request)
    view = Views().get_search_page(data)

    return view


@app.route('/contracts/contract/<string:document_cloud_id>', methods=['GET'])
def contract(document_cloud_id):
    '''
    The single contract page. The contract ID is specified in the URL.

    :returns: HTML. The single contract page \
    (/contracts/contract/<document_cloud_id>).
    '''

    data = Models().get_contracts_page(document_cloud_id)
    view = Views().get_contract(data)

    return view


@app.route('/contracts/download/<string:document_id>', methods=['GET', 'POST'])
def download(document_id):
    '''
    Download a requested contract. This is triggered during 'download' clicks.

    :returns: PDF. The contract's PDF file.
    '''

    data = Models().get_download(document_id)
    return data

if __name__ == '__main__':
    app.run(
        use_reloader=RELOADER,
        debug=DEBUG
    )
