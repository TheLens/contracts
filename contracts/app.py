"""
The web app that runs at vault.thelensnola.org/contracts.

It lets the public search City of New Orleans contracts that are posted to the
city's purchasing portal. It's just a Flask application, and it follows the
structure from the Flask tutorials. The front end is built with Foundation.
It uses SQLAlchemy to connect to a PostgreSQL database.
"""

import os
import importlib
from boto.s3.connection import S3Connection
from boto.s3.key import Key
from flask import Flask, request, Response
from functools import wraps
# from flask.ext.cache import Cache
from contracts.models import Models
from contracts.lib.parserator_utils import get_labels
from parserator.data_prep_utils import appendListToXMLfile
from contracts.views import Views
from contracts import (
    log,
    RELOADER,
    DEBUG,
    XML_LOCATION
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


@app.route('/contracts/admin/tags/<string:doc_cloud_id>', methods=['POST'])
def tags(doc_cloud_id):
    """
    The UI is requesting tags for the doc_cloud_id

    :returns: HTML. The single contract page \
    (/contracts/contract/<doc_cloud_id>).
    """

    log.debug('/contract/admin/tags')

    spanified_text = Models().get_tags_for_doc_cloud_id(doc_cloud_id, request)

    return spanified_text

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


def check_auth(username, password):
    """
    Checks if given username and password match correct credentials.

    :param username: The entered username.
    :type username: string
    :param password: The entered password.
    :type password: string
    :returns: bool. True if username and password are correct, False otherwise.
    """

    return (username == os.environ.get('CONTRACTS_ADMIN_USERNAME') and
            password == os.environ.get('CONTRACTS_ADMIN_PASSWORD'))


def authenticate():
    """
    Return error message.
    """

    return Response(
        'Could not verify your access level for that URL.\n'
        'You have to login with proper credentials',
        401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'}
    )


def requires_auth(f):
    """
    Authorization process.
    """

    @wraps(f)
    def decorated(*args, **kwargs):
        '''docstring'''

        auth = request.authorization

        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()

        return f(*args, **kwargs)

    return decorated


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


@app.route('/contracts/admin/', methods=['GET'])
#@requires_auth
def admin():
    """
    The parserator data entry page. The contract ID is specified in the URL.

    :returns: HTML. The single contract page \
    (/contracts/contract/<doc_cloud_id>).
    """

    log.debug('/contract/admin/')

    data = Models().get_admin_home()

    view = Views().get_admin_home(data)

    return view


@app.route('/contracts/admin/<string:doc_cloud_id>', methods=['GET'])
#@requires_auth
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


@app.route("/tokens/<string:docid>", methods=['POST'])
def tokens_dump(docid):
    """
    The UI is sending tagged tokens back to the server.
    Save them to train parserator
    """
    tagged_strings = set()
    labels = get_labels()
    tagged_sequence = labels
    tagged_strings.add(tuple(tagged_sequence))
    outfile = XML_LOCATION + "/" + docid + ".xml"
    try:
        os.remove(outfile)
    except OSError:
        pass
    appendListToXMLfile(tagged_strings,
                        importlib.import_module('contract_parser'),
                        outfile)
    output = "".join([i for i in open(outfile, "r")])
    conn = S3Connection()
    bucket = conn.get_bucket('lensnola')
    k = Key(bucket)
    k.key = 'contracts/contract_amounts/human_labels/' + docid + ".xml"
    k.set_contents_from_string(output)

    return admin()


if __name__ == '__main__':
    app.run(
        use_reloader=RELOADER,
        debug=DEBUG
    )
