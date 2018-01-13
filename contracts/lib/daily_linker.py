# pylint: skip-file

"""Finds links between vendors and campaign contributions (?)."""

import csv
import re

from bs4 import BeautifulSoup
from selenium import webdriver

from contracts.db import (
    Vendor,
    Contract,
    Person,
    VendorOfficer,
    VendorOfficerCompany,
    Company,
    EthicsRecord
)
from contracts import (
    log,
    SESSION,
    CAMPAIGN_SESSION,
    PROJECT_DIR,
    TODAY_DATE)


class Option(object):
    """TODO."""

    def __init__(self, name, org_type, city):
        """TODO."""
        self.name = name
        self.type = org_type
        self.city = city


class DailyLinker(object):
    """TODO."""

    def __init__(self):
        """TODO."""
        self.last_names = self._get_last_names()
        self.first_names = self._get_first_names()

        self.driver = webdriver.PhantomJS(
            executable_path='/usr/local/bin/phantomjs', port=65000)

    def try_to_link(self, vendor_name):
        """TODO."""
        search_results = self.search_sos(vendor_name)
        total_hits = self.get_total_hits(search_results)
        if total_hits == 1:
            log.info("Perfect match for %s", vendor_name)
            self.process_direct_hit(search_results, vendor_name)

    def get_daily_contracts(self, today_string=TODAY_DATE):
        """TODO."""
        # defaults to today
        query = (SESSION.query(Contract.doc_cloud_id, Vendor.name)
                 .filter(Contract.dateadded == today_string)
                 .filter(Contract.vendorid == Vendor.id)
                 .all())

        SESSION.close()

        return query

    def _get_last_names(self):
        """TODO."""
        last_names = []

        last_name_path = "%s/data/all-last.csv" % PROJECT_DIR

        with open(last_name_path, "r") as fname:
            reader = csv.reader(fname)
            next(reader, None)  # Skip header row
            for row in reader:
                last_names.append(row[0])

        return last_names

    def _get_first_names(self):
        """TODO."""
        male_first_names = self._get_male_first_names()
        female_first_names = self._get_female_first_names()

        first_names = male_first_names + female_first_names

        return first_names

    def _get_male_first_names(self):
        """TODO."""
        male_first_names = []

        first_male_name_path = "%s/data/male-first.csv" % PROJECT_DIR

        with open(first_male_name_path, "r") as fname:
            reader = csv.reader(fname)
            next(reader, None)  # Skip header row
            for row in reader:
                male_first_names.append(row[0])

        return male_first_names

    def _get_female_first_names(self):
        """TODO."""
        female_first_names = []

        first_female_name_path = "%s/data/female-first.csv" % PROJECT_DIR

        with open(first_female_name_path, "r") as fname:
            reader = csv.reader(fname)
            next(reader, None)  # Skip header row
            for row in reader:
                female_first_names.append(row[0])

        return female_first_names

    @staticmethod
    def _has_known_person_suffix(name):
        """TODO."""
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
            # people with Jr etc at the end of the name are people:
            if reg.search(name):
                return True

        return False

    @staticmethod
    def has_known_company_suffix(name):
        """TODO."""
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
            # People with Jr etc at the end of the name are people:
            if reg.search(name):
                return True

        return False

    def is_common_first_and_last_name_and_has_initial(self, name):
        """TODO."""
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

    def is_this_a_person(self, name_of_thing):
        """TODO."""
        if self._has_known_person_suffix(name_of_thing):
            return True

        if self.is_common_first_and_last_name_and_has_initial(name_of_thing):
            return True

        return False

    def _is_this_a_company(self, name_of_thing):
        """TODO."""
        if self.has_known_company_suffix(name_of_thing):
            return True

        return False

    def add_name(self, name):
        """TODO."""
        name = name.replace(".", "").strip()
        if self.is_this_a_person(name):
            # people with Jr ect at the end of the name are people

            indb = (SESSION.query(Person)
                    .filter(Person.name == name)
                    .count())

            if indb == 0:
                SESSION.add(Person(name))
                SESSION.commit()
                return

            if indb == 1:
                SESSION.close()
                return

        if self._is_this_a_company(name):
            indb = (SESSION.query(Company)
                    .filter(Company.name == name)
                    .count())

            if indb == 0:
                SESSION.add(Company(name))
                SESSION.commit()
                return

            if indb == 1:
                SESSION.close()
                return

        log.info("Could not link %s", name)

        SESSION.close()

    def add_vendor(self, vendor_name):
        """TODO."""
        indb = (SESSION.query(Vendor)
                .filter(Vendor.name == vendor_name)
                .count())

        if indb == 0:
            vendor = Vendor(vendor_name.replace(".", ""))
            SESSION.add(vendor)
            SESSION.commit()
        else:
            SESSION.close()

    def link(self, name, vendor):
        """Link the vendor to the company."""
        name = name.strip("\n").replace(".", "").strip()

        # get the vendor:
        vendorindb = (SESSION.query(Vendor)
                      .filter(Vendor.name == vendor)
                      .first())

        # get the person:
        personindb = (SESSION.query(Person)
                      .filter(Person.name == name)
                      .first())

        co = (SESSION.query(Company)
              .filter(Company.name == name))

        companyindb = co.first()  # get the company
        if personindb is not None and companyindb is None:
            link = (SESSION.query(VendorOfficer)
                    .filter(VendorOfficer.vendorid == vendorindb.id)
                    .filter(VendorOfficer.personid == personindb.id)
                    .count())

            if vendorindb is not None and personindb is not None and link < 1:
                log.info("Linking {0} to {1}",
                         str(vendorindb.id), str(personindb.id))
                link = VendorOfficer(vendorindb.id, personindb.id)
                SESSION.add(link)
                SESSION.commit()
                return

        if companyindb is not None and personindb is None:
            link = (SESSION.query(VendorOfficerCompany)
                    .filter(VendorOfficerCompany.vendorid == vendorindb.id)
                    .filter(VendorOfficerCompany.companiesid == companyindb.id)
                    .count())

            if vendorindb is not None and companyindb is not None and link < 1:
                print("Linking {0} to {1}".format(
                    str(vendorindb.id), str(companyindb.id)
                ))
                link = VendorOfficerCompany(vendorindb.id, companyindb.id)
                SESSION.add(link)
                SESSION.commit()
                return

        SESSION.close()

    def get_options(self, soup):
        """TODO."""
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
        """TODO."""
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
        """TODO."""
        city = city.upper()

        soup = BeautifulSoup(self.driver.page_source)
        rows = soup.find_all("tr")

        rows = [row for row in rows if "class" in row.attrs.keys()]
        rows_normal = [
            row for row in rows if row.attrs['class'][0] == "RowNormal"]
        rows_alt = [row for row in rows if row.attrs['class'][0] == "RowAlt"]
        rows = rows_alt + rows_normal
        city_rows = [
            row for row in rows if city in ''.join(row.findAll(text=True))]

        # return the IDs for each button to explore
        return [r.contents[4].contents[1] for r in city_rows]

    def get_pages_for_potential_hits(self, potential_hits):
        """TODO."""
        pages = []

        for potential_hit in potential_hits:
            p_id = potential_hit.attrs['id']
            self.driver.find_element_by_id(p_id).click()
            page = self.driver.page_source
            pages.append(page)
            self.driver.find_element_by_id(
                "ctl00_cphContent_btnBackToSearchResults"
            ).click()

        return pages

    def search_sos(self, vendor):
        """Search for a vendor."""
        self.driver.get(
            "http://coraweb.sos.la.gov/commercialsearch/commercialsearch.aspx")
        self.driver.find_element_by_id(
            "ctl00_cphContent_txtEntityName").send_keys(vendor)
        self.driver.find_element_by_id(
            "ctl00_cphContent_btnSearchEntity").click()
        page = self.driver.page_source
        return page

    def process_direct_hit(self, raw_html, vendor_name):
        """TODO."""
        vendor_name = vendor_name.strip("\n").replace(".", "")

        log.debug("Adding vendor %s", vendor_name)

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
        """TODO."""
        if "ctl00_cphContent_tblResults" in self.driver.page_source:
            return 1

        text = self.driver.find_element_by_id(
            "ctl00_cphContent_lblTotalResults"
        ).text

        return int(text)  # no hits

    def get_names_from_vendor(self, name):
        """TODO."""
        query = (SESSION.query(Person.name)
                 .filter(Vendor.id == VendorOfficer.vendorid)
                 .filter(Person.id == VendorOfficer.personid)
                 .filter(Vendor.name == name)
                 .all())

        SESSION.close()

        return [str(row[0]) for row in query]

    def get_state_contributions(self, name):
        """TODO."""
        query = (CAMPAIGN_SESSION.query(EthicsRecord)
                 .filter(EthicsRecord.contributorname == name)
                 .all())

        CAMPAIGN_SESSION.close()

        # TODO: Sort output by increasing donation size
        # contributions.sort(lambda x: dateutil.parser.parse(x.receiptdate))

        output = [row.__str__() for row in query]

        output.sort()

        return output

if __name__ == '__main__':
    contracts = DailyLinker().get_daily_contracts()
    for contract in contracts:
        # contract_id = contract[0]
        vendor = contract[1]
        DailyLinker().try_to_link(vendor)
