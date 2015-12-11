# -*- coding: utf-8 -*-

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

from scripts.document_cloud_project import DocumentCloudProject
from scripts.lens_database import LensDatabase
from scripts.lens_repository import LensRepository
from scripts.purchase_order import PurchaseOrder

from contracts import log


class Main(object):

    '''Methods for checking on the city's purchasing website.'''

    # TODO: Refactor this, and probably break into smaller methods.
    def main(self):
        '''
        Runs a scan for each of the 10 most recent pages on the city's
        purchasing website.

        :params pages: A range of page numbers to check.
        :type pages: list.
        '''

        number_of_pages = self._find_number_of_pages()

        number_of_pages_to_check = 10

        new_pages = range(1, number_of_pages_to_check + 1)
        old_pages = range(number_of_pages_to_check + 1, number_of_pages + 1)

        # Randomize the order of pages
        shuffle(new_pages)
        shuffle(old_pages)

        new_counter = 0
        for new_page in new_pages:
            log.debug('')
            log.debug('========')
            log.debug('Page %d', new_page)
            log.debug('========')
            print (
                '\n' +
                '\n========' +
                '\nPage %s' % new_page +
                '\n========')

            # Check if this page has been scraped recently.
            need_to_scrape = LensDatabase().check_if_need_to_scrape(new_page)

            if not need_to_scrape:
                continue

            # TODO: Comment
            self._scan_index_page(new_page)

            # TODO: Comment
            LensDatabase().update_scrape_log(new_page)
            new_counter += 1

            # Run five times per day, so break after 2 pages in order to reach
            # 10 pages per day.
            if new_counter == 2:
                break

            time.sleep(60)

        old_counter = 0
        for old_page in old_pages:
            log.debug('')
            log.debug('========')
            log.debug('Page %d', new_page)
            log.debug('========')
            print (
                '\n' +
                '\n========' +
                '\nPage %s' % old_page +
                '\n========')

            need_to_scrape = LensDatabase().check_if_need_to_scrape(old_page)

            if not need_to_scrape:
                continue

            self._scan_index_page(old_page)

            LensDatabase().update_scrape_log(old_page)
            old_counter += 1

            # Run five times per day, seven days per week, so break after 13
            # pages in order to reach about 450 pages per week.
            if old_counter == 13:
                break
            time.sleep(60)

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
        )[3].findChildren(  # [3] if zero-based, [4] if not
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

        number_of_pages = re.search(
            '[0-9]+', href).group()

        print 'There were %s pages found on the city\'s purchasing portal.' % (
            number_of_pages)
        log.debug(
            'There were %s pages found on the city\'s purchasing portal.',
            number_of_pages
        )

        return int(number_of_pages)

    def _scan_index_page(self, page_number):
        '''
        Run the downloader helper for this page on the purchasing site.

        :param page_number: The page to check on the city's website.
        :type page_number: string
        '''

        html = self._get_index_page(page_number)
        purchase_order_numbers = self._get_purchase_order_numbers(html)

        for i, purchase_order_number in enumerate(purchase_order_numbers):
            print (
                '\n-----------------------' +
                '\nPurchase order %s' % purchase_order_number +
                '\n-----------------------' +
                '\n(%d of %d)' % (i + 1, len(purchase_order_numbers)))
            log.debug('')
            log.debug('-----------------------')
            log.debug('Purchase order %s', purchase_order_number)
            log.debug('-----------------------')
            log.debug(
                '(%d of %d)' % (i + 1, len(purchase_order_numbers)))

            # TODO: Comment
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

        # href="/bso/external/purchaseorder/poSummary.sdo?docId=JOB264879&" \
        #       releaseNbr=0&parentUrl=contract"
        pattern = '(?<=docId=)(\w+)&'
        output = re.findall(pattern, html)

        return output

    # @staticmethod
    # def _check_if_invalid(html):
    #     '''
    #     Sometimes invalid purchase orders are posted. Check if this is one of
    #     those.

    #     :param html: The individual contract page's HTML.
    #     :type html: string
    #     :returns: boolean. True if an invalid contract page, False if valid.
    #     '''

    #     no_vendor_string = "There are no vendor distributors found " + \
    #                        "for this master blanket/contract"

    #     if no_vendor_string in html:
    #         return True
    #     else:
    #         return False

    @staticmethod
    def _check_if_need_to_download_contract(purchase_order_number):
        '''
        Determines whether this contract should be downloaded, and also whether
        it needs to be added to our DocumentCloud and local database.

        :param purchase_order_number: The contract's purchase order number.
        :type purchase_order_number: string
        '''

        log.info(
            'Checking purchase order %s.',
            purchase_order_number)

        # Check local file repository
        try:
            print '\n*** LensRepository ***'
            log.debug('')
            log.debug('*** LensRepository ***')

            need_to_download = LensRepository(
                purchase_order_number).check_if_need_to_download()
            if need_to_download:
                LensRepository(purchase_order_number).download_purchase_order()
        except urllib2.HTTPError, error:
            log.exception(error, exc_info=True)
            log.exception(
                'Purchase order %s not posted publically',
                purchase_order_number
            )
            print 'Purchase order not posted publically.'

        try:
            print '\n*** PurchaseOrder ***'
            log.debug('')
            log.debug('*** PurchaseOrder ***')

            purchase_order_object = PurchaseOrder(purchase_order_number)
            purchase_order_object.download_attachments()
        except IndexError, error:
            print 'IndexError'
            log.exception(error, exc_info=True)
            log.info('IndexError: %s.', purchase_order_number)
            return

        # Check DocumentCloud project
        try:
            print '\n*** DocumentCloudProject ***'
            log.debug('')
            log.debug('*** DocumentCloudProject ***')

            need_to_upload = DocumentCloudProject().check_if_need_to_upload(
                purchase_order_number)
            if need_to_upload:
                DocumentCloudProject().prepare_then_add_contract(
                    purchase_order_object)
        except urllib2.HTTPError, error:
            log.exception(error, exc_info=True)
            log.exception(
                'Purchase order %s not posted publically',
                purchase_order_number
            )

        # Check local database
        try:
            print '\n*** LensDatabase ***'
            log.debug('')
            log.debug('*** LensDatabase ***')

            contract_exist = LensDatabase().check_if_database_has_contract(
                purchase_order_number)
            if contract_exist is False:
                LensDatabase().add_to_database(purchase_order_object)
        except urllib2.HTTPError, error:
            log.exception(error, exc_info=True)
            log.exception(
                'Purchase order %s is not posted publically.',
                purchase_order_number
            )

    @staticmethod
    def _get_index_page(page_number):
        '''
        Get a given index page for the city's purchasing website. The pages are
        based on a reverse chronological order sort.

        :param page_number: The page number.
        :type page_number: string
        :returns: string. The HTML for the index page, which contains a \
                          table of contracts.
        '''

        url = 'http://www.purchasing.cityofno.com/bso/' + \
            'external/advsearch/searchContract.sdo'

        # Found by checking cURL of page load.
        data = (
            'mode=sort' +
            '&currentPage=' + str(page_number) +
            '&sortBy=beginDate' +
            '&sortByIndex=5' +
            '&sortByDescending=true' +
            '&masterFlag=true' +
            '&searchFor=%2Fexternal%2Fadvsearch%2FsearchContract' +
            '&searchFor=%2Fadvsearch%2FbuyerSearchContract' +
            '&advancedSearchJspName=%2Fexternal%2F' +
            'advsearch%2FadvancedSearch.jsp' +
            '&searchAny=false' +
            '&includeExpired=on')

        req = urllib2.Request(url=url, data=data)

        response = urllib2.urlopen(req)
        output = response.read()
        response.close()

        return output

if __name__ == '__main__':
    print "\nChecking the city's purchasing site for new contracts..."

    Main().main()
