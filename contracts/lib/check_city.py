# * coding: utf8 *

'''
Utility functions for gathering and organizing published contracts from the
city's purchasing website.

This script is run every day and checks the 10 most recent pages on the city's
purchasing website. This should capture everything, but the city occassionally
uploads older contracts, which means some contracts do not fall within these 10
pages.
'''

import re
import time
import urllib2
from random import shuffle
from bs4 import BeautifulSoup
from contracts.lib.lens_database import LensDatabase
from contracts.lib.purchase_order import PurchaseOrder
from contracts.lib.lens_repository import LensRepository
from contracts.lib.document_cloud_project import DocumentCloudProject
from contracts import log


class CheckCity(object):

    '''Methods for checking on the city's purchasing website.'''

    # TODO: Refactor this, and probably break into smaller methods.
    def check_pages(self):
        '''
        Runs a scan for each of the 10 most recent pages on the city's
        purchasing website.

        :params pages: A range of page numbers to check.
        :type pages: list.
        '''

        number_of_pages = self._find_number_of_pages()

        number_new_pages = 10

        new_pages = range(1, number_new_pages + 1)
        old_pages = range(number_new_pages + 1, number_of_pages + 1)

        log.info('Shuffling new and old pages')

        shuffle(new_pages)
        shuffle(old_pages)

        # Want to visit all 10 pages per day. Run five times with 2 pages each
        new_page_selection = 2

        log.info('Selecting {} of the {} new pages'.format(
            new_page_selection, number_new_pages))

        for i, new_page in enumerate(new_pages):
            log.info('Page {}'.format(new_page))

            need_to_scrape = LensDatabase().check_if_need_to_scrape(new_page)

            if not need_to_scrape:
                continue

            self._scan_index_page(new_page)

            LensDatabase().update_scrape_log(new_page)

            if i == new_page_selection:  # i starts at 1
                break

            time.sleep(60)  # TODO

        # 13 pages 5x per day 7x per week = ~450 pages per week
        old_page_selection = 13

        log.info('Selecting {} of the {} older pages'.format(
            old_page_selection, number_of_pages - number_new_pages))

        for i, old_page in enumerate(old_pages):
            log.debug('Page {}'.format(old_page))

            need_to_scrape = LensDatabase().check_if_need_to_scrape(old_page)

            if not need_to_scrape:
                continue

            self._scan_index_page(old_page)

            LensDatabase().update_scrape_log(old_page)

            if i == old_page_selection:
                break

            time.sleep(60)  # TODO

    def _find_number_of_pages(self):
        '''
        Finds how many pages of contracts there are on the city's
        purchasing site.

        :returns: int. The number of pages.
        '''

        html = self._get_index_page(1)
        soup = BeautifulSoup(html)

        main_table = soup.select('.table-01').pop()

        metadata_row = main_table.find_all(
            'tr', recursive=False
        )[3].findChildren(  # [3] if zerobased, [4] if not
            ['td']
        )

        metadata_row = metadata_row[0].findChildren(
            ['table']
        )[0].findChildren(
            ['tr']
        )[0].findChildren(
            ['td']
        )[0].findChildren(
            ['table']
        )[0].findChildren(
            ['tr']
        )[1]

        href = metadata_row.findChildren(
            ['td']
        )[0].findChildren(
            ['a']
        )[-1].get('href')

        num_of_pages = re.search('[0-9]+', href).group()

        log.debug('Found {} total pages'.format(num_of_pages))

        return int(num_of_pages)

    def _scan_index_page(self, page_number):
        '''
        Run the downloader helper for this page on the purchasing site.

        :param page_number: The page to check on the city's website.
        :type page_number: string
        '''

        html = self._get_index_page(page_number)
        purchase_order_numbers = self._get_purchase_order_numbers(html)

        for i, purchase_order_number in enumerate(purchase_order_numbers):
            log.debug('Purchase order {} ({} of {})'.format(
                purchase_order_number, i + 1, len(purchase_order_numbers)))

            self._check_if_need_to_download_contract(purchase_order_number)
            time.sleep(10)

    @staticmethod
    def _get_purchase_order_numbers(html):
        '''
        Fetches a list of the purchase order numbers for the contracts on a
        given page on the city's purchasing website.

        :param html: The HTML for an index page on the city's purchasing site.
        :type html: string
        :returns: list. The purchase order numbers for the contracts listed \
        on the page.
        '''

        # TODO: Why this pattern? It skips JOB1234123. Is there any need to
        # restrict to only two characters?
        pattern = '(?<=docId=)[A-Z][A-Z][0-9]+'
        output = re.findall(pattern, html)

        return output

    @staticmethod
    def _check_if_need_to_download_contract(purchase_order_number):
        '''
        Determines whether this contract should be downloaded, and also whether
        it needs to be added to our DocumentCloud and local database.

        :param purchase_order_number: The contract's purchase order number.
        :type purchase_order_number: string
        '''
        # Check file repository
        try:
            need_to_download = LensRepository(
                purchase_order_number).check_if_need_to_download()
            if need_to_download:
                LensRepository(purchase_order_number).download_purchase_order()
        except urllib2.HTTPError:
            log.exception('Purchase order not in local archives')

        try:
            purchase_order_object = PurchaseOrder(purchase_order_number)
            purchase_order_object.download_attachments()
        except IndexError:
            log.exception()
            return

        # Check DocumentCloud
        try:
            need_to_upload = DocumentCloudProject().check_if_need_to_upload(
                purchase_order_number)
            if need_to_upload:
                DocumentCloudProject().prepare_then_add_contract(
                    purchase_order_object)
        except urllib2.HTTPError:
            log.exception('Purchase order not on DocumentCloud')

        # Check database
        try:
            contract_exist = LensDatabase().check_if_database_has_contract(
                purchase_order_number)
            if contract_exist is False:
                LensDatabase().add_to_database(purchase_order_object)
        except urllib2.HTTPError:
            log.exception('Purchase order is not in database')

    @staticmethod
    def _get_index_page(page_number):
        '''
        Get a given index page for the city's purchasing website. The pages are
        based on a reverse chronological order sort, which includes expired
        contracts (?).

        :param page_number: The page number.
        :type page_number: string
        :returns: string. The HTML for the index page, which contains a \
                          table of contracts.
        '''

        data = (
            'mode=sort&letter=&currentPage=' + str(page_number) +
            '&querySql=%5B' +
            'PROCESSED%5D75%3A1d%3A4a%3A6d%3A34%3A14%3A5c%3A47%3A30%3A1b' +
            '%3A74%3A16%3A58%3A69%3A1f%3A4c%3A13%3A50%3A4%3A12%3A24%3A6' +
            '0%3A6e%3A1b%3A49%3A2b%3A6e%3A11%3A5f%3A7b%3Aa%3A62%3A30' +
            '%3A3%3A5%3A1f%3A1%3A25%3A43%3A19%3A12%3A1a%3A71%3A6b%3A' +
            '20%3A53%3A11%3A50%3A52%3A46%3A1a%3A69%3A5a%3A79%3A7d%3A45%3' +
            'A44%3A72%3A1e%3A46%3A3a%3A48%3A60%3A76%3A76%3A57%3A6%3A4' +
            '0%3A0%3A7f%3A3d%3A1e%3A68%3A41%3A80%3A3d%3A27%3A44%3A6a%3' +
            'A1e%3A79%3A68%3A58%3A46%3A77%3A25%3A68%3A53%3A7e%3A15%3A1' +
            'c%3A6b%3A6f%3A2b%3A7d%3A41%3A10%3Ab%3Ab%3A23%3A32%3Af%3A62' +
            '%3A48%3A3f%3A5f%3A7d%3A2e%3A7d%3A62%3A41%3A40%3A6b%3A62%3' +
            'A4a%3A2c%3A1d%3A1%3A29%3A41%3A60%3A5e%3A19%3A63%3A55%3A59%' +
            '3A39%3A61%3A54%3A47%3A31%3A79%3A6c%3A1c%3Ab%3A1b%3Ae%3A' +
            '30%3A12%3A5%3A47%3A49%3A49%3A6c%3A1e%3A57%3A52%3A1b%3A63%3A1' +
            'b%3A31%3A9%3A6b%3A4f%3A30%3A5%3A21%3A35%3A0%3A4c%3A20%3A67%' +
            '3A14%3A5a%3A3%3A57%3A4c%3A39%3A1c%3A27%3A1d%3A38%3A19%3A7' +
            '9%3A17%3A78%3A12%3A71%3A7b%3A46%3A3e%3A20%3A3f%3A2c%3A7b' +
            '%3A69%3A1b%3A6d%3A1c%3A78%3A6b%3A7d%3A68%3A15%3A6%3A0%3A49' +
            '%3A31%3A25%3A31%3A68%3A56%3A7d%3A2%3A56%3A5f%3A20%3A60%3' +
            'A76%3A69%3A9%3A2d%3A9%3A2c%3A50%3A2a%3A65%3A7e%3A66%3A7f%3A' +
            '34%3A5a%3A10%3A11%3A79%3A50%3A7b%3A64%3A25%3A7c%3A48%3A40' +
            '%3A7e%3Ae%3A21%3A47%3A5b%3A5e%3A27%3A4d%3A71%3Af%3A56%3' +
            'A1c%3A53%3A5c%3A61%3A0%3A18%3A40%3Ae%3A22%3A3c%3A58%3A55%' +
            '3A5e%3A68%3Ac%3A29%3A74%3A2b%3A62%3A1b%3A2d%3A33%3A48%3A' +
            '37%3A6%3Ad%3A6b%3A22%3A4e%3A44%3A10%3A45%3A43%3A2%3A2b%3A' +
            '17%3A13%3A7d%3A1e%3A56%3A53%3A5d%3A44%3Ad%3A14%3A20%3A71%3' +
            'A1f%3A59%3A7b%3A42%3A5f%3A10%3A43%3A52%3A4e%3A69%3A6e%3' +
            'A75%3A7%3A61%3A4c%3A62%3A6a%3A37%3A23%3A3a%3A5b%3A70%3A72' +
            '%3A1c%3A14%3A63%3A71%3A33%3Aa%3A20%3A16%3A52%3A35%3A10%3A3' +
            '0%3A42%3A34%3A7%3A49%3A10%3A63%3A78%3A13%3A46%3A37%3A24' +
            '%3A2e%3A55%3A48%3A18%3A1c%3A4b%3A7c%3A7d%3A10%3A5%3Aa%3A1' +
            '4%3A8%3A4a%3A1c%3A34%3A47%3A43%3A4f%3A45%3A6b%3A2a%3Aa%3' +
            'A51%3A72%3A5c%3A66%3A33%3A4e%3A18%3A4d%3A27%3A3f%3Ad%3A23' +
            '%3A77%3A2b%3A41%3Ae%3A47%3A14%3A31%3A17%3A22%3A37%3A39%3A66' +
            '%3A3f%3A1b%3A29%3A23%3A5b%3A63%3A54%3A15%3A62%3A76%3A20%' +
            '3A58%3A18%3A7d%3A48%3A57%3A32%3A1a%3A15%3A10%3A79%3A68%3A' +
            '23%3A38%3A40%3A35%3A75%3A33%3A50%3A2%3A13%3A72%3A11%3A1a%3A35' +
            '%3A3b%3A80%3A59%3A4e%3A10%3A3d%3A9%3A6a%3A22%3A4c%3A6d%3' +
            'A1e%3A5%3Ad%3A51%3A78%3A7a%3A1d%3A44%3A3d%3A1d%3A36%3A41%' +
            '3A4d%3A15%3A23%3A5b%3A7f%3A5b%3A6c%3A18%3A2d%3A2%3A41%3A3d' +
            '%3A3b%3A40%3A22%3A14%3A28%3A7%3A50%3A1c%3A28%3A69%3A40%3A1' +
            'f%3A3a%3A7a%3A5%3A76%3A4%3A6c%3A29%3A59%3A77%3A34%3A77%3A7' +
            'c%3A77%3A2a%3A49%3A5a%3A5e%3A4a%3A7b%3A4d%3A79%3A29%3A75%3' +
            'A52%3A57%3A6%3A52%3A33%3A23%3A57%3A15%3A79%3A79%3A8%3A66%3A' +
            '31%3A7f%3A4c%3A35%3A26%3A65%3A59%3A5f%3A3d%3A7c%3A6c%3A7f%3' +
            'A1a%3A1b%3A49%3A18%3A75%3A4f%3A2e%3A32%3A5d%3A66%3A37%3A3' +
            'b%3A78%3A45%3A6a%3A6f%3A3e%3A27%3A44%3A7f%3A40%3A64%3A4c%3' +
            'A6%3A74%3A53%3Ab%3A6b%3A7d%3A28%3A62%3Ae%3A1d%3A32%3A21%3A' +
            '5%3A1a%3A35%3A61%3Ad%3Ac%3A45%3A33%3A24%3A66%3A30%3A65%3A2c%3' +
            'A72%3A78%3A52%3A5a%3A31%3A11%3A15%3A4a%3Aa%3A55%3A31%3A' +
            '9%3A20%3Ac%3A46%3A40%3A46%3Ad%3A7f%3A34%3A57%3A12%3A7b%3A' +
            '55%3A3f%3A68%3A50%3A15%3A21%3A80%3A41%3A35%3A70%3A33%3A' +
            'f%3A42%3A76%3A4f%3A33%3A44%3A29%3A64%3A45%3A12%3A1b%3A1%3' +
            'A7f%3Ac%3A32%3A1f%3A51%3A29%3A1c%3A24%3A6a%3A80%3A1f%3A2' +
            '8%3A7d%3A42%3Aa%3A11%3A77%3A7a%3A9%3Ab%3A4c%3A24%3A5f%3A' +
            '2d%3Ae%3A66%3A3c%3A1%3A2d%3A1a%3A65%3A59%3A2a%3A43%3A8%3A' +
            '30%3A3c%3A6c%3A3%3A2f%3A7f%3A4e%3A5f%3Ab%3A44%3A60%3A38%3' +
            'A7a%3A68%3A63%3A7d%3A7d%3A16%3Aa%3A2b%3A51%3A2e%3A5a%3A6d' +
            '%3A5d%3A5b%3A71%3A29%3A6f%3A26%3A55%3A56%3Ad%3A10%3A65' +
            '%3A2c%3A41%3A5c%3A2b%3A49%3A37%3A6%3Ae%3A6c%3A53%3A62%3A' +
            '6b%3A34%3A3d%3A74%3Af%3A47%3A9%3A5a%3A16%3A1d%3A9%3A36%3' +
            'A3%3A3%3A9%3A69%3A3b%3A24%3A3a%3A42%3A47%3A2a%3A48%3A3a%3' +
            'Ae%3A7d%3A4f%3A79%3Ab%3A2d%3A6%3A3%3A11%3A7%3A7b%3A1b%3A3' +
            '3%3A1c%3Af%3A3c%3A24%3A31%3A4f%3A56%3A54%3A74%3A5e%3A33%3' +
            'A39%3A7c%3A76%3A9%3Ae%3A3a%3A14%3A1d%3A3d%3A47%3A65%3A3' +
            'f%3A3b%3A21%3A79%3A5b%3A1%3A4a%3A55%3A11%3Af%3A80%3A6e%3' +
            'A6b%3A2c%3A10%3A25%3A13%3A74%3A2f%3A9%3A63%3A11%3A16%3A13%3' +
            'A20%3A4d%3A6c%3A4e%3Ab%3A3d%3Af%3A1c%3A73%3A16%3A75%3A46' +
            '%3A76%3A1b%3A38%3A43%3A77%3A73%3A7e%3A66%3A12%3A45%3A29%3' +
            'A42%3A46%3A6e%3A58%3A3e%3A26%3A56%3A56%3A1c%3A6b%3A71%3A2' +
            '%3A33%3A61%3A4%3A1d%3A34%3A2d%3A54%3A68%3A1f%3A14%3A48%3A7f' +
            '%3A68%3A53%3A26%3A2d%3A3f%3A71%3A0%3A7a%3A3b%3A34%3A1b%3A5' +
            '0%3A30%3A35%3A62%3A56%3A18%3A7%3A35%3A6%3A69%3A14%3A6f%3A35' +
            '%3A7b%3A4b%3A2c%3A6d%3A76%3A61%3A20%3A49%3A13%3A42%3A4d%' +
            '3A46%3A5a%3A30%3A6d%3A14%3A4d%3A46%3A6a%3A77%3A2f%3A26%3A44%' +
            '3A3%3A3a%3A26%3A56%3A1d%3A30%3Ae%3A6a%3A80%3A28%3A4a%3' +
            'A5a%3A4c%3A1e%3A4f%3A44%3A50%3A3a%3A78%3A16%3A8%3A56%3A47%3' +
            'A20%3A4c%3A39%3A1%3Ad%3A4b%3A25%3A70%3A22%3A44%3A73%3A' +
            '25%3A1%3A2%3A6e%3A40%3A37%3A56%3A4b%3A25%3A42%3A72%3Ad%3A48' +
            '%3A4e%3A51%3A54%3A3a%3A67%3A64%3A7b%3A51%3A7%3A4f%3A29%3A' +
            '78%3A1b%3A78%3A62%3A6e%3A1c%3A7%3A34%3A39%3A6e%3A62%3' +
            'A21%3A75%3A58%3A6d%3A2b%3A6e%3A6d%3A66%3A0%3A24%3A73%3A7' +
            '7%3A36%3A23%3A76%3A1e%3A1b%3A15%3A44%3A5a%3A3%3A61%3A6e%' +
            '3A44%3A49%3A11%3A38%3A46%3A54%3A37%3A33%3A23%3A2d%3A3f%3A' +
            '37%3A7e%3A50%3A6%3A4e%3A12%3A6e%3A2b%3A24%3A5%3A7e%3A4%3A' +
            '37%3A33%3A18%3A29%3A1a%3Ac%3A18%3A7d%3A52%3A60%3A5f%3A5f%3' +
            'A28%3A62%3A74%3A0%3A52%3Ac%3A24%3A7e%3A43%3A60%3A1c%3A55%3' +
            'Aa%3A1f%3A3%3Ad%3A68%3A2b%3A58%3A2e%3A7e%3A7f%3A27%3A31%3A29%' +
            '3A55%3A2%3A65%3A5%3A5c%3A55%3A65%3A5a%3A5e%3A51%3A7b%3A59' +
            '%3A4%3A55%3A66%3A6c&sortBy=beginDate&sortByIndex=5&sortByDesc' +
            'ending=true&masterFlag=true&module=&searchFor=%2Fexternal%2Fadv' +
            'search%2FsearchContract&searchFor=%2Fadvsearch%2FbuyerSearchCon' +
            'tract&advancedSearchJspName=%2Fexternal%2Fadvsearch%2FadvancedS' +
            'earch.jsp&searchAny=false&poNbr=&poTypeParm=&desc=&buyer=&vendo' +
            'rName=&bidNbr=&typeCode=&catalogId=&expireFromDateStr=&expireTo' +
            'DateStr=&itemDesc=&orgId=&departmentPrefix=&classId=&classItemI' +
            'd=&commodityCode=&includeExpired=on')

        url = 'http://www.purchasing.cityofno.com/bso/' + \
            'external/advsearch/searchContract.sdo'

        req = urllib2.Request(url=url, data=data)
        req.add_header('Pragma', ' nocache')
        req.add_header('Origin', 'http://www.purchasing.cityofno.com')
        req.add_header('AcceptEncoding', 'gzip, deflate')
        req.add_header('ContentType', 'application/xwwwformurlencoded')
        req.add_header('CacheControl', 'nocache')
        req.add_header('Connection', 'keepalive')
        req.add_header('DNT', '1')
        req.add_header(
            'Accept',
            'text/add_contracthtml,application/xhtml+xml,application/xml;' +
            'q=0.9,image/webp,*/*;q=0.8')
        req.add_header(
            'Referer',
            'http://www.purchasing.cityofno.com/bso/external/advsearch/' +
            'searchContract.sdo')

        response = urllib2.urlopen(req)
        output = response.read()
        response.close()

        return output

if __name__ == '__main__':
    log.info("Checking the city's purchasing site for new contracts")
    CheckCity().check_pages()
