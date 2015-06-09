
'''Finds links between vendors and campaign contributions (?).'''

import re
import csv
import dateutil.parser
from bs4 import BeautifulSoup
from selenium import webdriver
# from address import AddressParser, Address
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from contracts.db import (
    Vendor,
    Contract,
    Person,
    VendorOfficer,
    VendorOfficerCompany,
    Company,
    EthicsRecord
)
from contracts import log, CONNECTION_STRING, PROJECT_DIR, TODAY_DATE


class Option:

    '''docstring'''

    def __init__(self, name, org_type, city):
        self.name = name
        self.type = org_type
        self.city = city


class DailyLinker(object):

    '''docstring'''

    def __init__(self):
        self.last_names = self._get_last_names()
        self.first_names = self._get_first_names()

        # ap = AddressParser()

        engine = create_engine(CONNECTION_STRING)
        self.sn = sessionmaker(bind=engine)

        self.driver = webdriver.PhantomJS(
            executable_path='/usr/local/bin/phantomjs', port=65000)

        # TODO:
        # known_people = [t.strip("\n").replace(".", "") for t in tuple(
        #     open("known_people.txt", "r"))]  # a list of known people
        # known_companies = [t.strip("\n").replace(".", "") for t in tuple(
        #     open("known_companies.txt", "r"))]

    def try_to_link(self, vendor_name):
        '''docstring'''

        search_results = self.search_sos(vendor_name)
        total_hits = self.get_total_hits(search_results)
        if total_hits == 1:
            print "perfect hit for {}".format(vendor_name)
            self.process_direct_hit(search_results, vendor_name)

    def get_daily_contracts(self, today_string=TODAY_DATE):
        '''docstring'''

        session = self.sn()

        # defaults to today
        contracts = session.query(
            Contract.doc_cloud_id,
            Vendor.name
        ).filter(
            Contract.dateadded == today_string
        ).filter(
            Contract.vendorid == Vendor.id
        ).all()

        session.close()

        return contracts

    def _get_last_names(self):
        '''docstring'''

        last_names = []

        last_name_path = "%s/data/all-last.csv" % PROJECT_DIR

        with open(last_name_path, "r") as fname:
            reader = csv.reader(fname)
            next(reader, None)  # Skip header row
            for row in reader:
                last_names.append(row[0])

        return last_names

    def _get_first_names(self):
        '''docstring'''

        male_first_names = self._get_male_first_names()
        female_first_names = self._get_female_first_names

        first_names = male_first_names + female_first_names

        return first_names

    def _get_male_first_names(self):
        '''docstring'''

        first_male = []
        first_male_name_path = "%s/data/male-first.csv" % PROJECT_DIR

        with open(first_male_name_path, "r") as fname:
            reader = csv.reader(fname)
            next(reader, None)  # Skip header row
            for row in reader:
                first_male.append(row[0])

        return first_male

    def _get_first_female_names(self):
        '''docstring'''

        first_female = []

        first_female_name_path = "%s/data/female-first.csv" % PROJECT_DIR

        with open(first_female_name_path, "r") as fname:
            reader = csv.reader(fname)
            next(reader, None)  # Skip header row
            for row in reader:
                self.first_female.append(row[0])

        return first_female

    @staticmethod
    def has_known_person_suffix(name):
        '''docstring'''

        name_regexes = [
            ', JR$',
            ', JR\.?',
            '^REV',
            '^MR',
            '^MRS',
            'MRS\. ',
            '^REV\. ',
            '^DR\. ',
            ' JR\.$',
            ' SR$',
            ' JR$',
            ', PROFESSOR,',
            'MBA$',
            'MSW$',
            ', DEAN,',
            ', MPH',
            ' M\.D\.',
            'MR\. ',
            ', SR\.?$',
            ", P\.?E\.?",
            ", PH\.D\.",
            " III$",
            "D\.?M\.?D\.?",
            "II$",
            "AIA$",
            ', IV$',
            ", M\.S\.C\.$",
            ', DMD',
            ', D\.?V\.?M\.?',
            ', PHD',
            ', RSM',
            ', DVM',
            'DR '
        ]
        for name_regex in name_regexes:
            reg = re.compile(name_regex)
            # people with Jr ect at the end of the name are people:
            if reg.search(name):
                return True

        return False

    @staticmethod
    def has_known_company_suffix(name):
        '''docstring'''

        company_regexes = [
            ', INC\.?$',
            ', L\.?L\.?C\.?$',
            ', INC\.?',
            'L.L.C.$',
            ', L\.L\.C\.',
            ' LLP$',
            ', L\.L\.C\.$',
            "CORPORATION",
            "ASSOCIATION",
            ' & '
        ]
        for company_regex in company_regexes:
            reg = re.compile(company_regex)
            # people with Jr ect at the end of the name are people:
            if reg.search(name):
                return True

        return False

    def is_common_first_and_last_name_and_has_initial(self, name):
        '''docstring'''

        if len(name.split(" ")) == 2:
            return False

        condition1 = (
            name.split(" ")[0] in self.first_names and
            name.split(" ")[2] in self.last_names and
            len(name.split(" ")[1])
        )
        if condition1 == 1:
            return True

        condition2 = (
            name.split(" ")[0] in self.first_names and
            name.split(" ")[2] in self.last_names
        )
        if condition2:
            if len(name.split(" ")[1]) == 1:
                return True

            return True

        return False

    # def is_on_list_of_known_people(name):
    #     if name in known_people:
    #         return True

    #     return False

    # def is_on_list_of_known_companies(name):
    #     if name in known_companies:
    #         return True

    #     return False

    def is_this_a_person(self, name_of_thing):
        '''docstring'''

        if self.has_known_person_suffix(name_of_thing):
            return True

        if self.is_common_first_and_last_name_and_has_initial(name_of_thing):
            return True

        # if is_on_list_of_known_people(name_of_thing):
        #     return True

        return False

    def is_this_a_company(self, name_of_thing):
        '''docstring'''

        if self.has_known_company_suffix(name_of_thing):
            return True

        # if is_on_list_of_known_companies(name_of_thing):
        #     return True

        return False

    def add_name(self, name):
        '''docstring'''

        session = self.sn()

        name = name.replace(".", "").strip()
        if self.is_this_a_person(name):
            # people with Jr ect at the end of the name are people

            indb = session.query(Person).filter(Person.name == name).count()
            if indb == 0:
                person = Person(name)
                session.add(person)
                session.commit()
                return
            if indb == 1:
                return
        if self.is_this_a_company(name):
            indb = session.query(Company).filter(Company.name == name).count()
            if indb == 0:
                company = Company(name)
                session.add(company)
                session.commit()
                return
            if indb == 1:
                return
        print "coult not link {}".format(name)

        session.close()

    def add_vendor(self, vendor_name):
        '''docstring'''

        session = self.sn()

        indb = session.query(Vendor).filter(Vendor.name == vendor_name).count()
        if indb == 0:
            vendor = Vendor(vendor_name.replace(".", ""))
            session.add(vendor)
            session.commit()

        session.close()

    # def add_address(street, city, state, zipcode):  # , sourcefile):
    #     # convert address from pyaddress to the address model from our db
    #     indb = session.query(
    #         Address
    #     ).filter(
    #         Address.street == street,
    #         Address.city == city,
    #         Address.state == state,
    #         Address.zipcode == zipcode
    #     ).count()

    #     if indb == 0:
    #         address = Address(street, city, state, zipcode)  # , sourcefile)
    #         session.add(address)
    #         session.commit()

    # def add_addresses(o):
    #     name, title, address1, citystatezip, country, extrafield = [
    #         l.text for l in o.select("span")]
    #     if len(re.findall('[0-9]{5}-[0-9]{4}', citystatezip)):
    #         # parser fails on 9 digit zip codes

    #         end = re.findall(
    #             '[0-9]{5}-[0-9]{4}', citystatezip
    #         ).pop().split("-")[1].encode("UTF-8")
    #         citystatezip = citystatezip.replace("-", "").replace(end, "")
    #     string = address1 + " " + citystatezip
    #     address = ap.parse_address(string)
    #     add_address(
    #         address1,
    #         citystatezip.split(",")[0],
    #         address.state,
    #         address.zip,
    #         # directory + "/page.html"
    #     )
    #     # print "Address is: {0} {1} {2} {3} {4}".format(
    #     #    address.house_number, address.street,
    #     #    address.city, address.state, address.zip)

    def link(self, name, vendor):
        '''
        Link the vendor to the company.
        '''

        session = self.sn()

        name = name.strip("\n").replace(".", "").strip()

        # get the vendor:
        vendorindb = session.query(
            Vendor
        ).filter(
            Vendor.name == vendor
        ).first()

        # get the person:
        personindb = session.query(
            Person
        ).filter(
            Person.name == name
        ).first()

        co = session.query(
            Company
        ).filter(
            Company.name == name
        )
        companyindb = co.first()  # get the company
        if personindb is not None and companyindb is None:
            link = session.query(
                VendorOfficer
            ).filter(
                VendorOfficer.vendorid == vendorindb.id
            ).filter(
                VendorOfficer.personid == personindb.id
            ).count()
            if vendorindb is not None and personindb is not None and link < 1:
                print "linking {} to {}".format(
                    str(vendorindb.id), str(personindb.id))
                link = VendorOfficer(vendorindb.id, personindb.id)
                session.add(link)
                session.commit()
                session.close()
                return

        if companyindb is not None and personindb is None:
            link = session.query(
                VendorOfficerCompany
            ).filter(
                VendorOfficerCompany.vendorid == vendorindb.id
            ).filter(
                VendorOfficerCompany.companiesid == companyindb.id
            ).count()
            if vendorindb is not None and companyindb is not None and link < 1:
                print "linking {} to {}".format(
                    str(vendorindb.id), str(companyindb.id))
                link = VendorOfficerCompany(vendorindb.id, companyindb.id)
                session.add(link)
                session.commit()
                session.close()
                return

    def get_options(self, soup):
        '''docstring'''

        table = [t for t in soup.select(
            "#ctl00_cphContent_grdSearchResults_EntityNameOrCharterNumber"
        ).pop().select("tr") if not t.attrs["class"][0] == "RowHeader"]

        options = []

        for row in table:
            try:
                tds = row.select("td")
                company_name = tds[0].text.replace("\n", "")
                company_type = tds[1].text.replace("\n", "")
                company_city = tds[2].text
                option = Option(company_name, company_type, company_city)
                options.append(option)
            except:
                pass

        return options

    def find_button_to_click(self, firm):
        '''docstring'''

        soup = BeautifulSoup(self.driver.page_source)
        rows = soup.find_all("tr")
        rows = [r for r in rows if "class" in r.attrs.keys()]
        row = [r for r in rows if r.attrs[
            'class'][0] == "RowNormal" or r.attrs['class'] == "RowAlt"]

        if len(row) == 1:
            contents = row.pop().contents
            contents = contents[4]
            t = contents.contents[1].attrs
            return t['id']
        elif len(row) > 1:
            row = [r for r in row if r.text.split(
                "\n")[1].replace(",", "").replace(".", "") == firm]
            contents = row.pop().contents
            contents = contents[4]
            t = contents.contents[1].attrs
            return t['id']

    def get_rows_in_city(self, city):
        '''docstring'''

        city = city.upper()
        soup = BeautifulSoup(self.driver.page_source)
        rows = soup.find_all("tr")
        rows = [r for r in rows if "class" in r.attrs.keys()]
        rows_normal = [r for r in rows if (r.attrs['class'][0] == "RowNormal")]
        rows_alt = [r for r in rows if r.attrs['class'][0] == "RowAlt"]
        rows = rows_alt + rows_normal
        city_rows = [r for r in rows if city in ''.join(r.findAll(text=True))]

        # return the IDs for each button to explore
        return [r.contents[4].contents[1] for r in city_rows]

    def get_pages_for_potential_hits(self, potential_hits):
        '''docstring'''

        pages = []

        for p in potential_hits:
            id = p.attrs['id']
            self.driver.find_element_by_id(id).click()
            page = self.driver.page_source
            pages.append(page)
            self.driver.find_element_by_id(
                "ctl00_cphContent_btnBackToSearchResults").click()

        return pages

    # def pick_from_options(self, firm):
    #     if "ctl00_cphContent_lblTotalResults" in self.driver.page_source:
    #         # results listing page

    #         text = self.driver.find_element_by_id(
    #             "ctl00_cphContent_lblTotalResults").text
    #         if str(text) == "0":  # no hits
    #             self.driver.find_element_by_id(
    #                 "ctl00_cphContent_btnNewSearch").click()
    #             return "Zero results"
    #         if int(text) > 0:  # more than one hits
    #             potential_vendors = set([unicode(v.split("\t")[
    #                 1].upper()) for v in vendors if v.split(
    #                     "\t")[1] == firm])
    #             options = self.get_options(
    #                 BeautifulSoup(self.driver.page_source))
    #             direct_hits = [
    #                 o.name for o in options if \
    #                 o.name.upper() == firm.upper()]
    #             if len(direct_hits) == 1:
    #                 # one of the rows matches perfectly so pick that one

    #                 try:
    #                     id = self.find_button_to_click(direct_hits.pop())
    #                 except:
    #                     return "Ambiguous results"
    #                 self.driver.find_element_by_id(id).click()
    #                 page = self.driver.page_source.encode('utf8')
    #                 self.driver.find_element_by_id(
    #                     "ctl00_cphContent_btnNewSearch").click()
    #                 return page
    #             ignore_periods_commas_hits = [o.name.replace(
    #                 ".", "").replace(
    #                 ",", "") for o in options if o.name.upper().replace(
    #                 ".", "").replace(",", "") == firm.upper().replace(
    #                 ".", "").replace(",", "")]
    #             # one matches perfectly without
    #               periods and commas so pick it:
    #             if len(ignore_periods_commas_hits) == 1:
    #                 try:
    #                     id = self.find_button_to_click(
    #                         ignore_periods_commas_hits.pop())
    #                 except:
    #                     return "Ambiguous results"
    #                 self.driver.find_element_by_id(id).click()
    #                 page = self.driver.page_source.encode('utf8')
    #                 self.driver.find_element_by_id(
    #                     "ctl00_cphContent_btnNewSearch").click()
    #                 return page
    #             if len(direct_hits) == 0:
    #                 potential_vendors = list(set([
    #                     (
    #                         v.split("\t")[1],
    #                         v.split("\t")[2],
    #                         v.split("\t")[3],
    #                         v.split("\t")[4],
    #                         v.split("\t")[5]
    #                     ) for v in vendors if v.split("\t")[1] == firm]))
    #                 if len(potential_vendors) == 1:
    #                     potential_vendors = potential_vendors.pop()
    #                     potential_hits = self.get_rows_in_city(
    #                         potential_vendors[3])
    #                     pages = self.get_pages_for_potential_hits(
    #                         potential_hits)
    #                     if len(pages) == 1:
    #                         pass  # check that it is correct
    #                     else:
    #                         self.driver.find_element_by_id(
    #                             "ctl00_cphContent_btnNewSearch").click()
    #                         return "Ambiguous results"
    #                 else:
    #                     self.driver.find_element_by_id(
    #                         "ctl00_cphContent_btnNewSearch").click()
    #                     return "Ambiguous results"
    #             self.driver.find_element_by_id(
    #                 "ctl00_cphContent_btnNewSearch").click()
    #             return "Ambiguous results"
    #     self.driver.find_element_by_id("btnNewSearch").click()
    #     return "It's complicated"

    def search_sos(self, vendor):
        '''
        Search for a vendor.
        '''

        self.driver.get(
            "http://coraweb.sos.la.gov/commercialsearch/commercialsearch.aspx")
        self.driver.find_element_by_id(
            "ctl00_cphContent_txtEntityName").send_keys(vendor)
        self.driver.find_element_by_id(
            "ctl00_cphContent_btnSearchEntity").click()
        page = self.driver.page_source
        return page

    def process_direct_hit(self, raw_html, vendor_name):
        '''docstring'''

        vendor_name = vendor_name.strip("\n").replace(".", "")

        print "adding {}".format(vendor_name)
        log.debug("Adding {}".format(vendor_name))

        self.add_vendor(vendor_name)
        soup = BeautifulSoup(raw_html)

        try:
            officers = soup.find_all(
                id="ctl00_cphContent_pnlOfficers")[0].select(".TableBorder")
        except IndexError:
            # some places have no listed officers. ex 311 networks
            officers = []

        # agents = []

        # try:
        #     agents = soup.find_all(
        #         id="ctl00_cphContent_pnlAgents")[0].select(".TableBorder")
        # except:
        #     agents = []

        for officer in officers:
            name = [l.text for l in officer.select("span")].pop(0)
            self.add_name(name)
            self.link(name, vendor_name)
        # for a in agents:
        #    name = [l.text for l in o.select("span")].pop(0)
        #    add_name(name)

    def get_total_hits(self, page):
        '''docstring'''

        if "ctl00_cphContent_tblResults" in self.driver.page_source:
            return 1
        text = self.driver.find_element_by_id(
            "ctl00_cphContent_lblTotalResults").text
        return int(text)  # no hits
        raise Exception("Error!")

    def get_state_contributions(self, name):
        '''docstring'''

        session = self.sn()

        contributions = session.query(
            EthicsRecord
        ).filter(
            EthicsRecord.contributorname == name
        ).all()

        session.close()

        # contributions.sort(lambda x: dateutil.parser.parse(x.receiptdate))

        output = []

        for contribution in contributions:
            output.append(dateutil.parser.parse(contribution.receiptdate))

        output = output.sort()

        return output

    def get_names_from_vendor(self, name):
        '''docstring'''

        session = self.sn()

        names_query = session.query(
            Person.name
        ).filter(
            Vendor.id == VendorOfficer.vendorid
        ).filter(
            Person.id == VendorOfficer.personid
        ).filter(
            Vendor.name == name
        ).all()

        session.close()

        names = []

        for i in names_query:
            names.append(str(i[0]))

        return names

if __name__ == '__main__':
    contracts = DailyLinker().get_daily_contracts()
    for contract in contracts:
        # contract_id = contract[0]
        vendor = contract[1]
        DailyLinker().try_to_link(vendor)
