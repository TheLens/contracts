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


def getOffSet(q):
    """
    Parses the offset from the query. 
    Should be refactored away to use the flask request parsers
    """
    try:
        offsetterm = list([t for t in q.split("&&") if "offset" in t])
        offsetterm = offsetterm.pop()
        offset = int(offsetterm.split(":")[1])
        return offset
    except:
        return None


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


@cache.memoize(timeout=100000)
def getTerm(searchterm, key):
    """
    Used to parse a query. Should be replaced by native flask methods
    """   
    p = key + ':\"[^\r\n\"]+\"'
    terms = re.findall(p, searchterm)
    if len(terms) == 1:
        return terms.pop().replace(key + ":", "").replace('"', "")
    else:
        return ""


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
    updateddate = time.strftime("%m/%d/%Y")
    return render_template('intro_child.html',
                           vendors=vendors, departments=departments, offset=0,
                           totaldocs=totaldocs, pages=pages, page=1, docs=docs,
                           officers=officers, query=dc_query,
                           title="New Orleans city contracts",
                           updated=updateddate, url="contracts")


@app.route('/contracts/advanced')
def advanced(name=None):
    """
    Intro page for advanced search
    """
    offset = 0
    docs = getContracts(0, PAGELENGTH)
    totaldocs = getContracts_Count()
    pages = int(totaldocs/PAGELENGTH) + 1
    # pages = getPages(docs, offset)
    vendors = getVendors()
    departments = getDepartments()
    officers = getOfficers()
    return render_template('advanced.html', 
                           vendors=vendors,
                           departments=departments,
                           offset=0,
                           totaldocs=totaldocs,
                           pages=pages,
                           page=1, docs=docs,
                           officers=officers, query=dc_query)


@app.route('/contracts/next', methods=['POST'])
def next():
    """
    Respond to the next button
    """

    searchterm = request.args.get('query')
    offset = int(request.args.get('offset'))

    if offset < 1:
        offset = 0

    pages = int(getPages(searchterm))

    if offset > pages:
        offset = pages

    if searchterm == 'projectid: "1542-city-of-new-orleans-contracts"':
        docs = getContracts(offset, PAGELENGTH)
    else:
        docs = queryDocumentCloud(searchterm)
        docs = docs[offset*PAGELENGTH:((offset+1)*PAGELENGTH)]

    totaldocs = getTotalDocs(getTotalDocs)
    pages = pages + 1  # increment 1 to get rid of 0 indexing
    page = offset + 1  # increment 1 to get rid of 0 indexing
    status = getStatus(page, pages, searchterm)
    officers = []  # blank on later searches
    vendor = ""
    return render_template('documentcloud.html', 
                           docs=docs,
                           status=status,
                           offset=offset,
                           totaldocs=totaldocs,
                           page=page,
                           pages=pages,
                           officers=officers,
                           vendor=vendor,
                           query=searchterm)


@app.route('/contracts/contract/<string:doc_cloud_id>', methods=['GET'])
def contract(doc_cloud_id):
    """
    Request for a given contract
    """
    doc_cloud_id = re.sub(".html$", "", doc_cloud_id)
    return render_template('contract_child.html', doc_cloud_id=doc_cloud_id, title="New Orleans city contracts")


@app.route('/contracts/search/<string:q>', methods=['POST'])
def query_docs(q):
    """
    The main contract search
    """
    print q
    # if something goes wrong, just set offset to 0
    q = q.replace("offset:undefined", "offset:0")

    searchterm = str('projectid: "1542-city-of-new-orleans-contracts"' + " " + q).split("&&")[0].strip()

    print searchterm
    vendor = getTerm(searchterm, 'vendor')
    officers = getTerm(searchterm, 'officers')
    department = getTerm(searchterm, 'department')
    offset = getOffSet(q)

    if offset is None:
        return "Server error. Please contact The Lens"

    if len(officers) > 0:
        officers = [officers]
        vendor = translateToVendor(officers[0])
        searchterm = searchterm.replace("officers:", "")
        searchterm.replace('"' + officers[0] + '"', "")
        searchterm = searchterm + ' vendor:"' + vendor + '"'

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
    status = getStatus(page, pages, searchterm)
    return render_template('documentcloud.html', 
                           status=status,
                           docs=docs,
                           offset=offset,
                           totaldocs=totaldocs,
                           page=page,
                           pages=pages,
                           officers=officers,
                           vendor=vendor,
                           query=searchterm)

if __name__ == '__main__':
    app.run()
