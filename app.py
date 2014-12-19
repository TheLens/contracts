import sys
import math
import pprint
import re
import time
import ConfigParser
sys.path.append('datamanagement')
from flask import Flask
from flask import render_template, make_response, send_from_directory
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from flask.ext.cache import Cache
from vaultclasses import Vendor, Department, Contract, Person, VendorOfficer
from documentcloud import DocumentCloud


CONFIG_LOCATION = 'app.cfg'

def get_from_config(field):
    config = ConfigParser.RawConfigParser()
    config.read(CONFIG_LOCATION)
    return config.get('Section1', field)

PAGELENGTH = 8

app = Flask(__name__)
cache = Cache(app, config={'CACHE_TYPE': 'simple'})
documentCloudClient = DocumentCloud()

server = get_from_config('server')
databasepassword = get_from_config('databasepassword')
user = get_from_config('user')
dc_query = 'projectid: "1542-city-of-new-orleans-contracts"'


@cache.memoize(timeout=900)
def queryDocumentCloud(searchterm):
    return documentCloudClient.documents.search(searchterm)

'''
Note: d.id should be an INT but I am translating it to a
string to match doc.id from python document cloud in the template engine.
'''


def translateToDocCloudForm(docs):
    for d in docs:
        d.id = d.doc_cloud_id
    return docs


@cache.memoize(timeout=900)
def getContracts(offset, limit):
    engine = create_engine('postgresql://abe:' + databasepassword + '@' + server + ':5432/thevault')
    Session = sessionmaker(bind=engine)
    Session.configure(bind=engine)
    session = Session()
    offset = offset * PAGELENGTH
    print offset
    contracts = session.query(Contract).order_by(Contract.dateadded.desc()).offset(offset).limit(limit).all()
    session.close()
    contracts = translateToDocCloudForm(contracts)
    return contracts


@cache.memoize(timeout=100000)
def getContracts_Count():
    engine = create_engine('postgresql://abe:' + databasepassword + '@' + server + ':5432/thevault')
    Session = sessionmaker(bind=engine)
    Session.configure(bind=engine)
    session = Session()
    total = session.query(Contract).count()
    session.close()
    return total


@cache.memoize(timeout=100000)  # cache good for a day or so
def getVendors():
    engine = create_engine('postgresql://abe:' + databasepassword + '@' + server + ':5432/thevault')
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
    engine = create_engine('postgresql://abe:' + databasepassword + '@' + server + ':5432/thevault')
    Session = sessionmaker(bind=engine)
    Session.configure(bind=engine)
    session = Session()
    depts = session.query(Department.name).distinct().order_by(Department.name).all()
    depts = [j[0].strip() for j in depts]
    depts = sorted(list(set(depts)))
    depts.insert(0, "Department (example: Information Technology)".upper())
    session.close
    return depts


@cache.memoize(timeout=100000) #cache good for a day or so
def getOfficers(vendor=None):
    engine = create_engine('postgresql://abe:' + databasepassword + '@' + server + ':5432/thevault')
    Session = sessionmaker(bind=engine)
    Session.configure(bind=engine)
    session = Session()
    if vendor is None:
        officers = session.query(VendorOfficer, Person).filter(VendorOfficer.personid == Person.id).order_by(Person.name)
        session.close
        officers = sorted(list(set([o[1].name for o in officers])))
        officers.insert(0, "Company officer (example: Joe Smith) - feature in progress".upper())
        return officers
    else:
        vendor = vendor.replace("vendor:", "")
        officers = session.query(VendorOfficer, Person, Vendor).filter(VendorOfficer.personid == Person.id).filter(VendorOfficer.vendorid == Vendor.id).filter(Vendor.name==vendor).all()
        session.close
        officers = list(set([o[1].name for o in officers]))
        print officers
        return sorted(officers)


def getOffSet(q):
    try:
        offsetterm = list([t for t in q.split("&&") if "offset" in t])
        offsetterm = offsetterm.pop()
        offset = int(offsetterm.split(":")[1])
        return offset
    except:
        return None

# document cloud has metadata information.
# see what vendor is associated with an officer
# then just search for the vendor


@cache.memoize(timeout=100000)
def translateToVendor(officerterm):
    engine = create_engine('postgresql://abe:' + databasepassword + '@' + server + ':5432/thevault')
    Session = sessionmaker(bind=engine)
    Session.configure(bind=engine)
    session = Session()
    officerterm = officerterm.replace('"', "").replace("officers:", "").strip()
    results = session.query(Person, VendorOfficer, Vendor).filter(Person.name == officerterm).filter(Person.id == VendorOfficer.personid).filter(VendorOfficer.vendorid == Vendor.id).all()  # todo fix to get .first() working
    return results.pop()[2].name


@app.route('/download/<string:docid>', methods=['POST', 'GET'])
def download(docid):
    docs = queryDocumentCloud("document:" + '"' + docid + '"')
    response = make_response(docs.pop().pdf)
    response.headers["Content-Disposition"] = "attachment; filename=" + docid + ".pdf"
    return response


@cache.memoize(timeout=100000)
def getPages(searchterm):
    if searchterm == 'projectid: "1542-city-of-new-orleans-contracts"':
        return int(getContracts_Count()/PAGELENGTH)
    else:
        return int(len(queryDocumentCloud(searchterm))/PAGELENGTH)


@cache.memoize(timeout=100000)
def getTotalDocs(searchterm):
    if searchterm == 'projectid: "1542-city-of-new-orleans-contracts"':
        return getContracts_Count()
    else:
        return int(len(queryDocumentCloud(searchterm)))


@cache.memoize(timeout=100000)
def getTerm(searchterm, key):
    p = key + ':\"[^\r\n\"]+\"'
    terms = re.findall(p, searchterm)
    if len(terms) == 1:
        return terms.pop().replace(key + ":", "").replace('"', "")
    else:
        return ""


def getStatus(page, total, searchterm):
    status = ""
    if searchterm == 'projectid: "1542-city-of-new-orleans-contracts"':
        return "All city contracts: page " + str(page) + " of " + str(total)
    else:
        return "Page " + str(page) + " of " + str(total)


@app.route('/vendors/<string:q>', methods=['POST'])
def vendors(q=None):
    if q == "all":
        vendors = getVendors()
    else:
        q = q.split("=")[1]   #eventually going to move this to a query-parser class
        terms = [t for t in q.split("&") if len(t)>0]
        vendor = [v.replace("vendor:","") for v in terms if "vendor:" in v].pop()
        print vendor
    return render_template('select.html', options=vendors)


@app.route('/officers/<string:q>', methods=['POST'])
def officers(q=None):
    if q == "all":
        officers = getOfficers()
    return render_template('select.html', options=officers)


@app.route('/departments/<string:q>', methods=['POST'])
def departments(q=None):
    if q == "all":
        departments = getDepartments()
    else:
        pass
    return render_template('select.html', options=departments)


@app.route('/')
def intro(name=None):
    offset = 0
    docs = getContracts(0, PAGELENGTH)
    totaldocs = getContracts_Count()
    pages = int(totaldocs/PAGELENGTH) + 1
    # pages = getPages(docs, offset)
    vendors = getVendors()
    departments = getDepartments()
    officers = getOfficers()
    updateddate = time.strftime("%m/%d/%Y")
    return render_template('intro_child.html', vendors=vendors, departments=departments, offset=0, totaldocs=totaldocs, pages=pages, page=1, docs=docs, officers=officers, query=dc_query, title="New Orleans city contracts", updated=updateddate, url="contracts")


@app.route('/advanced')
def advanced(name=None):
    offset = 0
    docs = getContracts(0, PAGELENGTH)
    totaldocs = getContracts_Count()
    pages = int(totaldocs/PAGELENGTH) + 1
    # pages = getPages(docs, offset)
    vendors = getVendors()
    departments = getDepartments()
    officers = getOfficers()
    return render_template('advanced.html', vendors=vendors, departments=departments, offset=0, totaldocs=totaldocs, pages=pages, page=1, docs=docs, officers=officers, query=dc_query)

@app.route('/next/<string:q>', methods=['POST'])
def next(q):
    print "next"
    searchterm = str(q).split("&&")[0].strip()
    offset = int(str(q).split("&&")[1].replace("offset:", "").strip())
    pages = int(getPages(searchterm))
    print "offset {0}".format(offset)
    if offset < pages:  # dont increment if yer at the end
            offset = offset+1
    print "offset {0}".format(offset)

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
    return render_template('documentcloud.html', docs=docs, status=status, offset=offset, totaldocs=totaldocs, page=page, pages=pages, officers=officers, vendor=vendor, query=searchterm)


@app.route('/previous/<string:q>', methods=['POST'])
def previous(q):
    searchterm = str(q).split("&&")[0]
    offset = getOffSet(q)

    if offset > 0:  # dont decrement if yer at zero
        offset = offset-1

    if searchterm == 'projectid: "1542-city-of-new-orleans-contracts"':
        docs = getContracts(offset, PAGELENGTH)
    else:
        docs = queryDocumentCloud(searchterm)
        docs = docs[offset*PAGELENGTH:((offset+1)*PAGELENGTH)]

    pages = int(getPages(searchterm))
    totaldocs = getTotalDocs(searchterm)
    pages = pages + 1  # increment 1 to get rid of 0 indexing
    page = offset + 1  # increment 1 to get rid of 0 indexing
    status = getStatus(page, pages, searchterm)
    officers = []  # blank on later searches
    vendor = ""
    return render_template('documentcloud.html', docs=docs, offset=offset, status=status, totaldocs=totaldocs, page=page, pages=pages, officers=officers, vendor=vendor, query=searchterm)


@app.route('/contract/<string:doc_cloud_id>', methods=['GET'])
def contract(doc_cloud_id):
    doc_cloud_id = re.sub(".html$", "", doc_cloud_id)
    return render_template('contract_child.html', doc_cloud_id=doc_cloud_id, title="New Orleans city contracts")


@app.route('/search/<string:q>', methods=['POST'])
def query_docs(q):
    q = q.replace("offset:undefined", "offset:0")  # if something goes wrong, just set offset to 0
    searchterm = str('projectid: "1542-city-of-new-orleans-contracts"' + " " + q).split("&&")[0].strip()

    print searchterm
    vendor = getTerm(searchterm, 'vendor')
    officers = getTerm(searchterm, 'officers')
    department = getTerm(searchterm, 'department')
    offset = getOffSet(q)

    if offset is None:
        return "Server error. Please contact The Lens"

    # print '**vendor**' + vendor + '****'
    # print '**officers**'  + officers + '****'
    # print '**department**'  + department + '****'

    if len(officers) > 0:
        officers = [officers]
        vendor = translateToVendor(officers[0])
        searchterm = searchterm.replace("officers:", "").replace('"' + officers[0] + '"', "") + ' vendor:"' + vendor + '"'

    print "vendor {}".format(vendor)

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
    return render_template('documentcloud.html', status=status, docs=docs, offset=offset, totaldocs=totaldocs, page=page, pages=pages, officers=officers, vendor=vendor, query=searchterm)

if __name__ == '__main__':
    app.run()
