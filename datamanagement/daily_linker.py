import datetime
import re
import dateutil.parser
from contracts.lib.vaultclasses import Vendor, Department, Contract, Person, VendorOfficer, VendorOfficerCompany, Company
from address import AddressParser, Address
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
import ConfigParser
from ethics_classes import EthicsRecord
from bs4 import BeautifulSoup
from selenium import webdriver
from address import AddressParser, Address

Base = declarative_base()

from contracts.settings import Settings

SETTINGS = Settings()


last_names = [l.strip("\n").split(" ")[0] for l in tuple(open("dist.all.last.txt", "r"))]
first_male = [l.strip("\n").split(" ")[0] for l in tuple(open("dist.male.first.txt", "r"))]
first_female = [l.strip("\n").split(" ")[0] for l in tuple(open("dist.female.first.txt", "r"))]
first_names = first_female + first_male

ap = AddressParser()

# an Engine, which the Session will use for connection
engine = create_engine(SETTINGS.connection_string)

# create a configured "Session" class
Session = sessionmaker(bind=engine)
# create a Session
session = Session()

driver = webdriver.PhantomJS(executable_path='/usr/local/bin/phantomjs', port=65000)

known_people = [t.strip("\n").replace(".", "") for t in tuple(open("known_people.txt", "r"))] # a list of known people
known_companies = [t.strip("\n").replace(".", "") for t in tuple(open("known_companies.txt", "r"))]

class Option:
    def __init__(self, name, org_type, city):
        self.name = name
        self.type = org_type
        self.city = city

def addAddress(street, city, state, zipcode, sourcefile):
    #convert address from pyaddress to the address model from our db
    indb = session.query(Address).filter(Address.street==street, Address.city==city, Address.state==state, Address.zipcode==zipcode).count()
    if indb==0:
        address = Address(street,city,state, zipcode,sourcefile)
        session.add(address)
        session.commit()

def hasKnownPersonSuffix(name):
    nameregexes = [', JR$',', JR\.?', '^REV', '^MR', '^MRS', 'MRS\. ', '^REV\. ' ,'^DR\. ' , ' JR\.$', ' SR$', ' JR$', ', PROFESSOR,', 'MBA$' , 'MSW$' , ', DEAN,' ,  ', MPH', ' M\.D\.', 'MR\. ', ', SR\.?$', ", P\.?E\.?" ,", PH\.D\.", " III$", "D\.?M\.?D\.?", "II$", "AIA$",', IV$', ", M\.S\.C\.$", ', DMD', ', D\.?V\.?M\.?', ', PHD', ', RSM', ', DVM', 'DR ']
    for n in nameregexes:
        reg = re.compile(n)
        if reg.search(name): #people with Jr ect at the end of the name are people
            return True
    return False
 

def hasKnownCompanySuffix(name):
    companyregexes = [', INC\.?$', ', L\.?L\.?C\.?$', ', INC\.?' , 'L.L.C.$', ', L\.L\.C\.' ,' LLP$', ', L\.L\.C\.$', "CORPORATION", "ASSOCIATION", ' & ' ]
    for n in companyregexes:
        reg = re.compile(n)
        if reg.search(name): #people with Jr ect at the end of the name are people
            return True
    return False


def isCommonFirstAndLastNameAndHasInitial(name):
    if len(name.split(" ")) == 2:
        return False
    if (name.split(" ")[0] in first_names) and name.split(" ")[2] in last_names and len(name.split(" ")[1])==1:
        return True
    if (name.split(" ")[0] in first_names) and name.split(" ")[2] in last_names:
        if len(name.split(" ")[1])==1:
            return True

        return True
    return False


def isOnListOfKnownPeople(name):
    if name in known_people:
        return True
    return False


def isOnListOfKnownCompanies(name):
    if name in known_companies:
        return True
    return False

def is_this_a_person(name_of_thing):
    if hasKnownPersonSuffix(name_of_thing):
        return True
    if isCommonFirstAndLastNameAndHasInitial(name_of_thing):
        return True
    if isOnListOfKnownPeople(name_of_thing):
        return True
    return False


def is_this_a_company(name_of_thing):
    if hasKnownCompanySuffix(name_of_thing):
        return True
    if isOnListOfKnownCompanies(name_of_thing):
        return True
    return False


def addname(name):
    name=name.replace(".","").strip()
    if is_this_a_person(name): #people with Jr ect at the end of the name are people
        indb = session.query(Person).filter(Person.name == name).count()
        if indb==0:
            person = Person(name)
            session.add(person)
            session.commit()
            return
        if indb == 1:
            return
    if is_this_a_company(name):
        indb = session.query(Company).filter(Company.name == name).count()
        if indb == 0:
            company = Company(name)
            session.add(company)
            session.commit()
            return
        if indb == 1:
            return
    print "coult not link {}".format(name)

def addvendor(vendor_name):
    indb = session.query(Vendor).filter(Vendor.name == vendor_name).count()
    if indb == 0:
        vendor = Vendor(vendor_name.replace(".", ""))
        session.add(vendor)
        session.commit()

def addAddresses(o):
    name, title, address1, citystatezip, country, extrafield = [l.text for l in o.select("span")]
    if len(re.findall('[0-9]{5}-[0-9]{4}',citystatezip)): #parser fails on 9 digit zip codes
        end = re.findall('[0-9]{5}-[0-9]{4}',citystatezip).pop().split("-")[1].encode("UTF-8")
        citystatezip = citystatezip.replace("-", "").replace(end, "")
    string = address1 + " " + citystatezip
    address = ap.parse_address(string)
    addAddress(address1,citystatezip.split(",")[0], address.state, address.zip, directory + "/page.html")
    #print "Address is: {0} {1} {2} {3} {4}".format(address.house_number, address.street, address.city, address.state, address.zip)


def link(name,vendor):
    '''
    link the vendor to the company
    '''
    name = name.strip("\n").replace(".", "").strip()
    vendorindb = session.query(Vendor).filter(Vendor.name==vendor).first() #get the vendor
    personindb = session.query(Person).filter(Person.name==name).first() #get the person
    co = session.query(Company).filter(Company.name == name)
    companyindb = co.first() #get the company
    if personindb is not None and companyindb is None:
        link = session.query(VendorOfficer).filter(VendorOfficer.vendorid==vendorindb.id).filter(VendorOfficer.personid==personindb.id).count()
        if vendorindb is not None and personindb is not None and link<1:
            print "linking {} to {}".format(str(vendorindb.id), str(personindb.id))
            vendorID = vendorindb.id
            personID = personindb.id
            link = VendorOfficer(vendorindb.id, personindb.id)
            session.add(link)
            session.commit()
            return
    if companyindb is not None and personindb is None:
        link = session.query(VendorOfficerCompany).filter(VendorOfficerCompany.vendorid==vendorindb.id).filter(VendorOfficerCompany.companiesid==companyindb.id).count()
        if vendorindb is not None and companyindb is not None and link<1:
            print "linking {} to {}".format(str(vendorindb.id), str(companyindb.id))
            vendorID = vendorindb.id
            companyid = companyindb.id
            link = VendorOfficerCompany(vendorindb.id, companyindb.id)
            session.add(link)
            session.commit()
            return

def get_options(soup):
    table = [t for t in soup.select("#ctl00_cphContent_grdSearchResults_EntityNameOrCharterNumber").pop().select("tr") if not t.attrs["class"][0] == "RowHeader"]
    options = []
    for t in table:
        try:
            tds = t.select("td")
            company_name = tds[0].text.replace("\n", "")
            company_type = tds[1].text.replace("\n", "")
            company_city = tds[2].text
            option = Option(company_name, company_type, company_city)
            options.append(option)
        except:
            pass
    return options

def find_button_to_click(firm):
    soup = BeautifulSoup(driver.page_source)
    rows = soup.find_all("tr")
    rows = [r for r in rows if "class" in r.attrs.keys()]
    row = [r for r in rows if r.attrs['class'][0] == "RowNormal" or r.attrs['class']== "RowAlt" ]
    if len(row) == 1:
        contents = row.pop().contents
        contents = contents[4]
        t = contents.contents[1].attrs
        return t['id']
    elif len(row) > 1:
        row = [r for r in row if r.text.split("\n")[1].replace(",", "").replace(".", "") == firm]
        contents = row.pop().contents
        contents = contents[4]
        t = contents.contents[1].attrs
        return t['id']


def get_rows_in_city(city):
    city = city.upper()
    soup = BeautifulSoup(driver.page_source)
    rows = soup.find_all("tr")
    rows = [r for r in rows if "class" in r.attrs.keys()]
    rows_normal = [r for r in rows if (r.attrs['class'][0] == "RowNormal")]
    rows_alt = [r for r in rows if r.attrs['class'][0] == "RowAlt"]
    rows = rows_alt + rows_normal
    city_rows = [r for r in rows if city in ''.join(r.findAll(text=True))]
    return [r.contents[4].contents[1] for r in city_rows]   #return the IDs for each button to explore


def get_pages_for_potential_hits(potential_hits):
    pages = []
    for p in potential_hits:
        id = p.attrs['id']
        driver.find_element_by_id(id).click()
        page = driver.page_source
        pages.append(page)
        driver.find_element_by_id("ctl00_cphContent_btnBackToSearchResults").click()
    return pages


def pick_from_options(firm):
    if "ctl00_cphContent_lblTotalResults" in driver.page_source:  #results listing page
        text = driver.find_element_by_id("ctl00_cphContent_lblTotalResults").text
        if str(text) == "0":   #no hits
            driver.find_element_by_id("ctl00_cphContent_btnNewSearch").click()
            return "Zero results"
        if int(text) > 0:  #more than one hits
            potential_vendors = set([unicode(v.split("\t")[1].upper()) for v in vendors if v.split("\t")[1] == firm])
            options = get_options(BeautifulSoup(driver.page_source))
            direct_hits = [o.name for o in options if o.name.upper() == firm.upper()]
            if len(direct_hits)==1:       #one of the rows matches perfectly so pick that one
                try:
                    id = find_button_to_click(direct_hits.pop())
                except:
                    return "Ambiguous results"
                driver.find_element_by_id(id).click()
                page = driver.page_source.encode('utf8')
                driver.find_element_by_id("ctl00_cphContent_btnNewSearch").click()
                return page
            ignore_periods_commas_hits = [o.name.replace(".", "").replace(",", "") for o in options if o.name.upper().replace(".", "").replace(",", "") == firm.upper().replace(".", "").replace(",", "")]
            if len(ignore_periods_commas_hits)==1:  #one matches perfectly without periods and commas, so pick that one
                try:
                    id = find_button_to_click(ignore_periods_commas_hits.pop())
                except:
                    return "Ambiguous results"
                driver.find_element_by_id(id).click()
                page = driver.page_source.encode('utf8')
                driver.find_element_by_id("ctl00_cphContent_btnNewSearch").click()
                return page
            if len(direct_hits) == 0:
                potential_vendors = list(set([(v.split("\t")[1], v.split("\t")[2], v.split("\t")[3], v.split("\t")[4], v.split("\t")[5]) for v in vendors if v.split("\t")[1] == firm]))
                if len(potential_vendors) == 1:
                    potential_vendors = potential_vendors.pop()
                    potential_hits = get_rows_in_city(potential_vendors[3])
                    pages = get_pages_for_potential_hits(potential_hits)
                    if len(pages) == 1:
                        pass #check that it is correct
                    else:
                        driver.find_element_by_id("ctl00_cphContent_btnNewSearch").click()
                        return "Ambiguous results"
                else:
                    driver.find_element_by_id("ctl00_cphContent_btnNewSearch").click()
                    return "Ambiguous results"
            driver.find_element_by_id("ctl00_cphContent_btnNewSearch").click()
            return "Ambiguous results"
    driver.find_element_by_id("btnNewSearch").click()
    return "It's complicated"


def search_sos(vendor):
    '''
    Search for a vendor
    '''
    driver.get("http://coraweb.sos.la.gov/commercialsearch/commercialsearch.aspx")
    driver.find_element_by_id("ctl00_cphContent_txtEntityName").send_keys(vendor)
    driver.find_element_by_id("ctl00_cphContent_btnSearchEntity").click()
    page = driver.page_source
    return page


def get_from_config(field):
    config = ConfigParser.RawConfigParser()
    config.read('app.cfg')
    return config.get('Section1', field)


def process_direct_hit(raw_html, vendor_name):
    vendor_name = vendor_name.strip("\n").replace(".", "")
    print "adding {}".format(vendor_name)
    addvendor(vendor_name)
    soup = BeautifulSoup(raw_html)
    try:
        officers = soup.find_all(id="ctl00_cphContent_pnlOfficers")[0].select(".TableBorder")
    except IndexError: #some places have no listed officers. ex 311 networks
        officers = []
    try:
        agents = soup.find_all(id="ctl00_cphContent_pnlAgents")[0].select(".TableBorder")
    except:
        agents = []
    for o in officers:
        name = [l.text for l in o.select("span")].pop(0)
        addname(name)
        link(name,vendor_name)
    #for a in agents:
    #    name = [l.text for l in o.select("span")].pop(0)
    #    addname(name)


def get_total_hits(page):
    if "ctl00_cphContent_tblResults" in driver.page_source:
        return 1
    text = driver.find_element_by_id("ctl00_cphContent_lblTotalResults").text
    return int(text) #no hits
    raise Exception("Error!")


def try_to_link(vendor_name):
    search_results = search_sos(vendor_name)
    total_hits = get_total_hits(search_results)
    if total_hits == 1:
        print "perfect hit for {}".format(vendor_name)
        process_direct_hit(search_results, vendor_name)


def get_from_config(field):
    config = ConfigParser.RawConfigParser()
    config.read(CONFIG_LOCATION)
    return config.get('Section1', field)


def get_daily_contracts(today_string = datetime.datetime.today().strftime('%Y-%m-%d')):  #defaults to today
    contracts = session.query(Contract.doc_cloud_id, Vendor.name).filter(Contract.dateadded == today_string).filter(Contract.vendorid == Vendor.id).all()
    return contracts


def get_state_contributions(name):
    recccs = session.query(EthicsRecord).filter(EthicsRecord.contributorname==name).all()
    recccs.sort(key = lambda x: dateutil.parser.parse(x.receiptdate))
    return recccs


def get_names_from_vendor(name):
    recccs = session.query(Person.name).\
                     filter(Vendor.id == VendorOfficer.vendorid).\
                     filter(Person.id == VendorOfficer.personid).\
                     filter(Vendor.name == name).all()
    return [str(i[0]) for i in recccs]


contracts = get_daily_contracts()

for c in contracts:
    cid = c[0]
    vendor = c[1]
    try_to_link(vendor)

session.close()