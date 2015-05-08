#!/usr/bin/python
"""
The web app that runs at vault.thelensnola.org/contracts
"""
# import sys
import re
import time
from flask import Flask, render_template, make_response, request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
# from flask.ext.cache import Cache
from contracts.lib.vaultclasses import (
    Vendor,
    Department,
    Contract,
    Person,
    VendorOfficer
)
from contracts.lib.models import QueryBuilder
from documentcloud import DocumentCloud
# from contracts.settings import Settings
from contracts import (
    CONNECTION_STRING,
    LENS_CSS,
    BANNER_CSS,
    CONTRACTS_CSS,
    LENS_JS,
    CONTRACTS_JS,
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

    docs = get_contracts(0, PAGELENGTH)
    totaldocs = get_contracts_count()
    pages = int(totaldocs / PAGELENGTH) + 1
    vendors = get_vendors()
    departments = get_departments()
    officers = get_officers()
    status = "Newest city contracts ..."
    updateddate = time.strftime("%m/%d/%Y")
    return render_template(
        'index.html',
        vendors=vendors,
        departments=departments,
        offset=0,
        totaldocs=totaldocs,
        pages=pages,
        page=1,
        status=status,
        docs=docs,
        officers=officers,
        query=dc_query,
        updated=updateddate,
        lens_css=LENS_CSS,
        banner_css=BANNER_CSS,
        contracts_css=CONTRACTS_CSS,
        lens_js=LENS_JS,
        contracts_js=CONTRACTS_JS
    )


@app.route('/contracts/download/<string:docid>', methods=['POST', 'GET'])
def download(docid):
    """
    Download a requested contract
    """
    docs = query_document_cloud("document:" + '"' + docid + '"')
    response = make_response(docs.pop().pdf)
    disposition_header = "attachment; filename=" + docid + ".pdf"
    response.headers["Content-Disposition"] = disposition_header
    return response


@app.route('/contracts/vendors/<string:q>', methods=['POST'])
def vendors(q=None):
    """
    Get requested vendors from a query string and return a template.
    Needs to be refactored using the flask query parser
    """
    if q == "all":
        vendors = get_vendors()
    return render_template('select.html', options=vendors)


@app.route('/contracts/officers/<string:q>', methods=['POST'])
def officers(q=None):
    """
    Get requested officers. to do: say more.
    """
    if q == "all":
        officers = get_officers()
    return render_template('select.html', options=officers)


@app.route('/contracts/departments/<string:q>', methods=['POST'])
def departments(query=None):
    """
    Get requested departments
    """
    if query == "all":
        departments = get_departments()
    else:
        pass
    return render_template('select.html', options=departments)


@app.route('/contracts/contract/<string:doc_cloud_id>', methods=['GET'])
def contract(doc_cloud_id):
    """
    Request for a given contract
    """
    doc_cloud_id = re.sub(".html$", "", doc_cloud_id)
    return render_template(
        'contract.html',
        doc_cloud_id=doc_cloud_id,
        banner_css=BANNER_CSS,
        contracts_css=CONTRACTS_CSS,
        lens_js=LENS_JS,
        contracts_js=CONTRACTS_JS
    )


@app.route('/contracts/search', methods=['POST', 'GET'])
def query_docs():
    """
    The main contract search.
    """

    log.debug('search')

    offset = query_request("page")
    offset = get_offset(offset)
    searchterm = translate_web_query_to_dc_query()

    if searchterm == 'projectid: "1542-city-of-new-orleans-contracts"':
        docs = get_contracts(0, PAGELENGTH)
        docs = translate_to_doc_cloud_form(docs)
    else:
        docs = query_document_cloud(searchterm)
        # extract a window of PAGELENGTH number of docs
        docs = docs[offset * PAGELENGTH:((offset + 1) * PAGELENGTH)]

    totaldocs = get_total_docs(searchterm)

    pages = (totaldocs / PAGELENGTH)
    vendor = query_request("vendor").upper()
    pages = pages + 1  # increment 1 to get rid of 0 indexing
    page = offset + 1  # increment 1 to get rid of 0 indexing

    status = get_status(page, pages, searchterm)
    updateddate = time.strftime("%m/%d/%Y")
    vendors = get_vendors()
    officers = get_officers()
    departments = get_departments()

    log.info('Pages = {}'.format(pages))

    standard_query = 'projectid: "1542-city-of-new-orleans-contracts" '

    if request.method == 'GET':
        return render_template(
            'intro_child.html',
            vendors=vendors,
            departments=departments,
            offset=offset,
            totaldocs=totaldocs,
            status=status,
            pages=pages,
            page=offset + 1,
            docs=docs,
            officers=officers,
            query=searchterm.replace(standard_query, ""),
            updated=updateddate,
            url="contracts",
            banner_css=BANNER_CSS,
            contracts_css=CONTRACTS_CSS,
            lens_js=LENS_JS,
            contracts_js=CONTRACTS_JS
        )
    if request.method == 'POST':
        return render_template(
            'documentcloud.html',
            status=status,
            docs=docs,
            pages=pages,
            page=offset + 1,
            vendor=vendor,
            totaldocs=totaldocs,
            query=searchterm.replace(standard_query, ""),
            banner_css=BANNER_CSS,
            contracts_css=CONTRACTS_CSS,
            lens_js=LENS_JS,
            contracts_js=CONTRACTS_JS
        )

if __name__ == '__main__':
    app.run(
        port=5000,
        use_reloader=True,
        debug=True
    )
