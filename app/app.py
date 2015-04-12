#!/usr/bin/python
"""
The web app that runs at vault.thelensnola.org/contracts
"""
import sys
import re
import time
import logging
from flask import Flask
from flask import render_template, make_response
from flask import request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from flask.ext.cache import Cache
from contracts.lib.vaultclasses import Vendor
from contracts.lib.vaultclasses import Department
from contracts.lib.vaultclasses import Contract
from contracts.lib.vaultclasses import Person
from contracts.lib.vaultclasses import VendorOfficer
from documentcloud import DocumentCloud
from contracts.settings import Settings

settings = Settings()

PAGELENGTH = 8

app = Flask(__name__, template_folder=settings.templates)
cache = Cache(app, config={'CACHE_TYPE': 'simple'})
documentCloudClient = DocumentCloud()

engine = create_engine(settings.connection_string)

dc_query = 'projectid: "1542-city-of-new-orleans-contracts"'

logging.basicConfig(level=logging.DEBUG, filename=settings.log)

LEVELS = {'debug': logging.DEBUG,
          'info': logging.INFO,
          'warning': logging.WARNING,
          'error': logging.ERROR,
          'critical': logging.CRITICAL}

if len(sys.argv) > 1:
    level_name = sys.argv[1]
    level = LEVELS.get(level_name, logging.NOTSET)
    logging.basicConfig(level=level, filename=settings.log)
else:
    logging.basicConfig(level=logging.DEBUG, filename=settings.log)


@cache.memoize(timeout=900)
def queryDocumentCloud(searchterm):
    """
    This is it's own method so that queries can be cached via @memoize to speed things up
    """
    return documentCloudClient.documents.search(searchterm)


def translateToDocCloudForm(docs):
    """
    In the database each row for contracts has an ID which is different from the 
    doc_cloud_id on document cloud. This just translates rows so that their 
    id is equal to the doc_cloud_id. It's a bit awkward and should probably 
    be refactored away at some point. 
    """
    for d in docs:
        d.id = d.doc_cloud_id
    return docs


@cache.memoize(timeout=900)
def getContracts(offset, limit):
    """
    Simply query the newest contracts
    """
    Session = sessionmaker(bind=engine)
    Session.configure(bind=engine)
    session = Session()
    offset = offset * PAGELENGTH
    contracts = session.query(Contract).\
        order_by(Contract.dateadded.desc()).offset(offset).limit(limit).all()
    session.close()
    contracts = translateToDocCloudForm(contracts)
    return contracts


@cache.memoize(timeout=100000)
def getContracts_Count():
    """
    Query the count of all contracts
    """
    Session = sessionmaker(bind=engine)
    Session.configure(bind=engine)
    session = Session()
    total = session.query(Contract).count()
    session.close()
    return total


@cache.memoize(timeout=100000)  # cache good for a day or so
def getVendors():
    """
    Query all vendors in the database
    """
    Session = sessionmaker(bind=engine)
    Session.configure(bind=engine)
    session = Session()
    vendors = session.query(Vendor.name).distinct().order_by(Vendor.name)
    vendors = sorted(list(set([j[0].strip() for j in vendors])))
    vendors.insert(0, "Vendor (example: Three fold Consultants)".upper())
    session.close()
    return vendors


@cache.memoize(timeout=100000)  # cache good for a day or so
def getDepartments():
    """
    Query all departments in the database
    """
    Session = sessionmaker(bind=engine)
    Session.configure(bind=engine)
    session = Session()
    depts = session.query(Department.name).\
        distinct().order_by(Department.name).all()
    depts = [j[0].strip() for j in depts]
    depts = sorted(list(set(depts)))
    depts.insert(0, "Department (example: Information Technology)".upper())
    session.close
    return depts


@cache.memoize(timeout=100000)  # cache good for a day or so
def getOfficers(vendor=None):
    """
    Get officers for a given vendor
    """
    Session = sessionmaker(bind=engine)
    Session.configure(bind=engine)
    session = Session()
    if vendor is None:
        officers = session.query(VendorOfficer, Person).\
            filter(VendorOfficer.personid == Person.id).order_by(Person.name)
        session.close
        officers = sorted(list(set([o[1].name for o in officers])))
        message = "Company officer (example: Joe Smith) - feature in progress"
        officers.insert(0, message.upper())
        return officers
    else:
        vendor = vendor.replace("vendor:", "")
        officers = session.\
            query(VendorOfficer, Person, Vendor).\
            filter(VendorOfficer.personid == Person.id).\
            filter(VendorOfficer.vendorid == Vendor.id).\
            filter(Vendor.name == vendor).all()
        session.close
        officers = list(set([o[1].name for o in officers]))
        print officers
        return sorted(officers)


@cache.memoize(timeout=100000)
def translateToVendor(officerterm):
    """
    Translates a request for an officer to a request for a vendor
    associated with a given officer
    """
    Session = sessionmaker(bind=engine)
    Session.configure(bind=engine)
    session = Session()
    officerterm = officerterm.replace('"', "").replace("officers:", "").strip()
    results = session.query(Person, VendorOfficer, Vendor).\
        filter(Person.name == officerterm).\
        filter(Person.id == VendorOfficer.personid).\
        filter(VendorOfficer.vendorid == Vendor.id).all()
    # todo fix to get .first() working
    return results.pop()[2].name


@app.route('/contracts/download/<string:docid>', methods=['POST', 'GET'])
def download(docid):
    """
    Download a requested contract
    """
    docs = queryDocumentCloud("document:" + '"' + docid + '"')
    response = make_response(docs.pop().pdf)
    disposition_header = "attachment; filename=" + docid + ".pdf"
    response.headers["Content-Disposition"] = disposition_header
    return response


@cache.memoize(timeout=100000)
def getPages(searchterm):
    """
    Get the total number of pages for a given search.
    """
    if searchterm == 'projectid: "1542-city-of-new-orleans-contracts"':
        return int(getContracts_Count()/PAGELENGTH)
    else:
        return int(len(queryDocumentCloud(searchterm))/PAGELENGTH)


@cache.memoize(timeout=100000)
def getTotalDocs(searchterm):
    """
    Get the total number of relevant docs for a given search.
    """   
    if searchterm == 'projectid: "1542-city-of-new-orleans-contracts"':
        return getContracts_Count()
    else:
        return int(len(queryDocumentCloud(searchterm)))


def getStatus(page, total, searchterm):
    """
    Tells the user what search has returned
    """   
    if searchterm == 'projectid: "1542-city-of-new-orleans-contracts"':
        return "All city contracts: page " + str(page) + " of " + str(total)
    else:
        return "Page " + str(page) + " of " + str(total)


@app.route('/contracts/vendors/<string:q>', methods=['POST'])
def vendors(q=None):
    """
    Get requested vendors from a query string and return a template.
    Needs to be refactored using the flask query parser
    """   
    if q == "all":
        vendors = getVendors()
    else:
        # to do: use flasks query parsers
        q = q.split("=")[1]
        terms = [t for t in q.split("&") if len(t) > 0]
        vendor = [v.replace("vendor:", "") for v in terms if "vendor:" in v].pop()
        print vendor
    return render_template('select.html', options=vendors)


@app.route('/contracts/officers/<string:q>', methods=['POST'])
def officers(q=None):
    """
    Get requested officers. to do: say more.
    """
    if q == "all":
        officers = getOfficers()
    return render_template('select.html', options=officers)


@app.route('/contracts/departments/<string:q>', methods=['POST'])
def departments(q=None):
    """
    Get requested departments
    """
    if q == "all":
        departments = getDepartments()
    else:
        pass
    return render_template('select.html', options=departments)


@app.route('/contracts/')
def intro(name=None):
    """
    Intro page for the web app
    """
    offset = 0
    docs = getContracts(0, PAGELENGTH)
    totaldocs = getContracts_Count()
    pages = int(totaldocs/PAGELENGTH) + 1
    vendors = getVendors()
    departments = getDepartments()
    officers = getOfficers()
    status = "Newest city contracts ..."
    updateddate = time.strftime("%m/%d/%Y")
    return render_template('intro_child.html',
                           vendors=vendors,
                           departments=departments,
                           offset=0,
                           totaldocs=totaldocs,
                           pages=pages,
                           page=1,
                           status = status,
                           docs=docs,
                           officers=officers,
                           query=dc_query,
                           title="New Orleans city contracts",
                           updated=updateddate,
                           url="contracts")



@app.route('/contracts/contract/<string:doc_cloud_id>', methods=['GET'])
def contract(doc_cloud_id):
    """
    Request for a given contract
    """
    doc_cloud_id = re.sub(".html$", "", doc_cloud_id)
    return render_template('contract_child.html', doc_cloud_id=doc_cloud_id, title="New Orleans city contracts")


def query_request(field):
    field = request.args.get(field)
    if field is None:
        return ""
    else:
        return field


@app.route('/contracts/search', methods=['POST', 'GET'])
def query_docs():
    """
    The main contract search
    """
    searchterm = 'projectid: "1542-city-of-new-orleans-contracts" ' + request.args.get('query')
    offset = query_request('page')
    if offset == "":
        offset = 0
    if offset < 0:
        offset = 0
    else:
        offset = int(offset) - 1 # a page is one more than an offset

    vendor = query_request('vendor')
    officers = query_request('officer')
    department = query_request('officer')

    if len(officers) > 0:
        officers = [officers]
        vendor = translateToVendor(officers[0])

    if searchterm == 'projectid: "1542-city-of-new-orleans-contracts"':
        docs = getContracts(0, PAGELENGTH)
        docs = translateToDocCloudForm(docs)
    else:
        docs = queryDocumentCloud(searchterm)
        # extract a window of PAGELENGTH number of docs
        docs = docs[offset*PAGELENGTH:((offset+1)*PAGELENGTH)]

    totaldocs = getTotalDocs(searchterm)

    pages = (totaldocs/PAGELENGTH)

    vendor = vendor.upper()
    pages = pages + 1  # increment 1 to get rid of 0 indexing
    page = offset + 1  # increment 1 to get rid of 0 indexing
    status = "Query: " + searchterm.replace('projectid: "1542-city-of-new-orleans-contracts"', "")
    status += " | " + getStatus(page, pages, searchterm)
    updateddate = time.strftime("%m/%d/%Y")
    vendors = getVendors()
    officers = getOfficers()
    departments = getDepartments()
    logging.info('Pages = {}'.format(pages))
    if request.method == 'GET':
        return render_template('intro_child.html',
                               vendors=vendors,
                               departments=departments,
                               offset=offset,
                               totaldocs=totaldocs,
                               status = status,
                               pages=pages,
                               page=offset + 1,
                               docs=docs,
                               officers=officers,
                               query=searchterm.replace('projectid: "1542-city-of-new-orleans-contracts" ',""),
                               title="New Orleans city contracts",
                               updated=updateddate,
                               url="contracts")
    if request.method == 'POST':
        return render_template('documentcloud.html', 
                           status=status,
                           docs=docs,
                           pages=pages,
                           page=offset + 1,
                           vendor=vendor,
                           query=searchterm.replace('projectid: "1542-city-of-new-orleans-contracts" ',""))

if __name__ == '__main__':
    app.run()
