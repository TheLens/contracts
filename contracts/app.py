"""
The web app that runs at http://vault.thelensnola.org/contracts.

It allows the public to search City of New Orleans contracts that are posted
to the city's purchasing portal. It's a Flask application, and it follows the
structure from the Flask tutorials. The front end is built with Foundation.
It uses SQLAlchemy to connect to a PostgreSQL database.
"""

import os
import importlib
from boto.s3.connection import S3Connection
from boto.s3.key import Key
from flask import Flask, request, Response
# from flask.ext.cache import Cache
from functools import wraps
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

app = Flask(__name__)
# cache = Cache(app, config={'CACHE_TYPE': 'simple'})


@app.route('/contracts/', methods=['GET'])
def intro():
    """
    Intro page for the web app.

    :returns: HTML. The homepage (/contracts/).
    """

    log.debug('/')

    data = Models().get_home()

    # log.debug('/ data:')
    # log.debug(data)
    # print(data['documents'][0].id)

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


@app.route('/contracts/admin/', methods=['GET'])
@requires_auth
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
@requires_auth
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


@app.route("/contracts/admin/tokens/<string:docid>", methods=['POST'])
def tokens_dump(docid):
    """
    The UI is sending tagged tokens back to the server.
    Save them to train parserator
    """

    log.debug('/contracts/admin/tokens')

    tagged_strings = set()
    labels = get_labels()
    tagged_sequence = labels
    tagged_strings.add(tuple(tagged_sequence))

    outfile = "%s/%s.xml" % (XML_LOCATION, docid)
    log.debug(outfile)

    try:
        os.remove(outfile)
    except OSError:
        pass

    log.debug("About to append")

    appendListToXMLfile(
        tagged_strings,
        importlib.import_module('parser'),
        outfile
    )

    log.debug("Wrote XML file")

    output = "".join([i for i in open(outfile, "r")])
    conn = S3Connection()
    bucket = conn.get_bucket('lensnola')
    k = Key(bucket)
    k.key = 'contracts/contract_amounts/human_labels/%s.xml' % docid
    k.set_contents_from_string(output)

    log.debug("Wrote to S3")

    return "Wrote to S3"


if __name__ == '__main__':
    app.run(
        use_reloader=RELOADER,
        debug=DEBUG
    )
