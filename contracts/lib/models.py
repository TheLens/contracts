"""
Some utility classes.
"""

import re
import urllib2

from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


def get_contract_index_page(pageno):
    '''
    Get a given page in the list of current contracts.
    '''

    data = (
        'mode=sort&letter=&currentPage=' + str(pageno) + '&querySql=%5B' +
        'PROCESSED%5D-75%3A1d%3A4a%3A-6d%3A34%3A14%3A-5c%3A47%3A-30%3A1b' +
        '%3A-74%3A16%3A-58%3A69%3A-1f%3A4c%3A13%3A50%3A-4%3A-12%3A24%3A6' +
        '0%3A-6e%3A-1b%3A49%3A2b%3A-6e%3A-11%3A-5f%3A7b%3A-a%3A-62%3A-30' +
        '%3A3%3A5%3A1f%3A-1%3A-25%3A-43%3A-19%3A-12%3A-1a%3A-71%3A6b%3A-' +
        '20%3A53%3A-11%3A50%3A-52%3A-46%3A-1a%3A69%3A5a%3A79%3A7d%3A45%3' +
        'A-44%3A72%3A1e%3A-46%3A3a%3A48%3A-60%3A-76%3A-76%3A57%3A-6%3A-4' +
        '0%3A0%3A7f%3A-3d%3A1e%3A-68%3A41%3A-80%3A-3d%3A-27%3A-44%3A6a%3' +
        'A-1e%3A-79%3A-68%3A58%3A-46%3A77%3A25%3A68%3A-53%3A7e%3A-15%3A1' +
        'c%3A-6b%3A6f%3A-2b%3A7d%3A41%3A10%3A-b%3Ab%3A23%3A32%3A-f%3A-62' +
        '%3A-48%3A3f%3A5f%3A-7d%3A2e%3A-7d%3A-62%3A41%3A-40%3A-6b%3A62%3' +
        'A4a%3A2c%3A1d%3A-1%3A29%3A-41%3A-60%3A5e%3A19%3A63%3A-55%3A-59%' +
        '3A39%3A61%3A54%3A-47%3A-31%3A-79%3A-6c%3A-1c%3Ab%3A-1b%3A-e%3A-' +
        '30%3A12%3A5%3A47%3A49%3A49%3A6c%3A-1e%3A57%3A52%3A-1b%3A-63%3A1' +
        'b%3A31%3A-9%3A6b%3A4f%3A30%3A-5%3A21%3A35%3A0%3A-4c%3A-20%3A67%' +
        '3A14%3A5a%3A3%3A57%3A-4c%3A-39%3A-1c%3A27%3A-1d%3A-38%3A19%3A-7' +
        '9%3A17%3A-78%3A-12%3A-71%3A-7b%3A46%3A-3e%3A20%3A3f%3A-2c%3A-7b' +
        '%3A69%3A-1b%3A6d%3A1c%3A-78%3A6b%3A7d%3A-68%3A-15%3A-6%3A0%3A49' +
        '%3A-31%3A25%3A-31%3A68%3A56%3A-7d%3A-2%3A-56%3A-5f%3A-20%3A60%3' +
        'A76%3A69%3A-9%3A2d%3A9%3A2c%3A50%3A2a%3A-65%3A7e%3A-66%3A-7f%3A' +
        '34%3A-5a%3A10%3A11%3A79%3A-50%3A-7b%3A-64%3A25%3A-7c%3A48%3A-40' +
        '%3A-7e%3A-e%3A-21%3A47%3A-5b%3A-5e%3A27%3A-4d%3A71%3A-f%3A-56%3' +
        'A1c%3A53%3A-5c%3A-61%3A0%3A-18%3A-40%3Ae%3A22%3A3c%3A-58%3A-55%' +
        '3A5e%3A-68%3Ac%3A-29%3A74%3A-2b%3A62%3A-1b%3A-2d%3A-33%3A48%3A-' +
        '37%3A-6%3Ad%3A6b%3A-22%3A4e%3A-44%3A10%3A45%3A-43%3A-2%3A-2b%3A' +
        '-17%3A13%3A7d%3A-1e%3A-56%3A-53%3A5d%3A44%3Ad%3A14%3A-20%3A71%3' +
        'A-1f%3A-59%3A-7b%3A-42%3A-5f%3A-10%3A-43%3A52%3A4e%3A-69%3A6e%3' +
        'A-75%3A7%3A-61%3A-4c%3A-62%3A6a%3A-37%3A23%3A3a%3A-5b%3A70%3A72' +
        '%3A1c%3A-14%3A63%3A71%3A33%3Aa%3A-20%3A-16%3A52%3A35%3A-10%3A-3' +
        '0%3A-42%3A-34%3A7%3A-49%3A-10%3A-63%3A-78%3A-13%3A-46%3A37%3A24' +
        '%3A2e%3A55%3A48%3A-18%3A-1c%3A-4b%3A-7c%3A-7d%3A10%3A5%3Aa%3A-1' +
        '4%3A-8%3A4a%3A1c%3A-34%3A47%3A-43%3A-4f%3A-45%3A-6b%3A-2a%3Aa%3' +
        'A-51%3A-72%3A5c%3A-66%3A33%3A-4e%3A18%3A4d%3A-27%3A3f%3A-d%3A23' +
        '%3A77%3A-2b%3A-41%3A-e%3A47%3A14%3A31%3A17%3A22%3A37%3A-39%3A66' +
        '%3A-3f%3A-1b%3A29%3A23%3A-5b%3A63%3A-54%3A15%3A-62%3A-76%3A-20%' +
        '3A58%3A-18%3A-7d%3A48%3A-57%3A-32%3A-1a%3A15%3A-10%3A79%3A68%3A' +
        '23%3A38%3A40%3A35%3A75%3A33%3A50%3A-2%3A-13%3A72%3A11%3A1a%3A35' +
        '%3A-3b%3A-80%3A-59%3A4e%3A-10%3A-3d%3A-9%3A6a%3A22%3A4c%3A-6d%3' +
        'A1e%3A5%3Ad%3A51%3A-78%3A-7a%3A-1d%3A44%3A3d%3A-1d%3A-36%3A-41%' +
        '3A-4d%3A15%3A23%3A5b%3A-7f%3A5b%3A-6c%3A-18%3A-2d%3A2%3A41%3A3d' +
        '%3A-3b%3A-40%3A22%3A14%3A-28%3A7%3A50%3A1c%3A28%3A-69%3A40%3A-1' +
        'f%3A3a%3A-7a%3A5%3A76%3A4%3A-6c%3A29%3A59%3A77%3A-34%3A-77%3A-7' +
        'c%3A-77%3A-2a%3A49%3A5a%3A-5e%3A4a%3A-7b%3A4d%3A-79%3A29%3A75%3' +
        'A52%3A57%3A6%3A52%3A33%3A23%3A-57%3A15%3A79%3A79%3A-8%3A-66%3A-' +
        '31%3A7f%3A-4c%3A35%3A26%3A-65%3A59%3A5f%3A3d%3A7c%3A-6c%3A-7f%3' +
        'A-1a%3A1b%3A49%3A-18%3A-75%3A-4f%3A2e%3A32%3A5d%3A-66%3A-37%3A3' +
        'b%3A-78%3A45%3A-6a%3A6f%3A-3e%3A-27%3A44%3A7f%3A40%3A-64%3A4c%3' +
        'A6%3A74%3A-53%3Ab%3A6b%3A-7d%3A28%3A62%3A-e%3A1d%3A-32%3A21%3A-' +
        '5%3A1a%3A35%3A61%3Ad%3Ac%3A-45%3A-33%3A24%3A66%3A30%3A65%3A2c%3' +
        'A-72%3A-78%3A-52%3A5a%3A-31%3A11%3A-15%3A4a%3Aa%3A-55%3A-31%3A-' +
        '9%3A20%3A-c%3A-46%3A-40%3A46%3Ad%3A7f%3A-34%3A57%3A-12%3A-7b%3A' +
        '55%3A-3f%3A-68%3A50%3A15%3A-21%3A-80%3A-41%3A-35%3A-70%3A-33%3A' +
        '-f%3A-42%3A-76%3A4f%3A33%3A-44%3A29%3A64%3A-45%3A12%3A1b%3A-1%3' +
        'A-7f%3Ac%3A-32%3A-1f%3A51%3A-29%3A-1c%3A24%3A6a%3A-80%3A1f%3A-2' +
        '8%3A-7d%3A-42%3Aa%3A11%3A77%3A-7a%3A-9%3Ab%3A-4c%3A-24%3A-5f%3A' +
        '2d%3A-e%3A-66%3A3c%3A-1%3A2d%3A-1a%3A65%3A-59%3A2a%3A-43%3A8%3A' +
        '-30%3A-3c%3A-6c%3A3%3A2f%3A7f%3A-4e%3A-5f%3Ab%3A44%3A60%3A-38%3' +
        'A-7a%3A68%3A-63%3A-7d%3A7d%3A-16%3A-a%3A2b%3A51%3A2e%3A5a%3A-6d' +
        '%3A-5d%3A-5b%3A-71%3A29%3A-6f%3A-26%3A-55%3A-56%3A-d%3A-10%3A65' +
        '%3A-2c%3A-41%3A5c%3A-2b%3A-49%3A-37%3A6%3Ae%3A6c%3A53%3A-62%3A-' +
        '6b%3A-34%3A3d%3A-74%3A-f%3A-47%3A9%3A-5a%3A-16%3A-1d%3A9%3A36%3' +
        'A-3%3A-3%3A-9%3A69%3A-3b%3A-24%3A3a%3A42%3A47%3A2a%3A-48%3A3a%3' +
        'Ae%3A7d%3A-4f%3A79%3A-b%3A-2d%3A-6%3A3%3A11%3A7%3A-7b%3A-1b%3A3' +
        '3%3A1c%3A-f%3A3c%3A24%3A-31%3A-4f%3A-56%3A-54%3A-74%3A5e%3A33%3' +
        'A39%3A-7c%3A76%3A-9%3A-e%3A-3a%3A-14%3A-1d%3A3d%3A-47%3A65%3A-3' +
        'f%3A3b%3A21%3A-79%3A-5b%3A-1%3A-4a%3A55%3A11%3A-f%3A-80%3A-6e%3' +
        'A6b%3A2c%3A10%3A-25%3A13%3A74%3A-2f%3A-9%3A63%3A11%3A-16%3A13%3' +
        'A-20%3A-4d%3A6c%3A-4e%3Ab%3A-3d%3Af%3A-1c%3A-73%3A16%3A-75%3A46' +
        '%3A-76%3A1b%3A38%3A-43%3A77%3A73%3A-7e%3A-66%3A-12%3A-45%3A29%3' +
        'A42%3A46%3A-6e%3A58%3A-3e%3A-26%3A-56%3A56%3A1c%3A6b%3A-71%3A-2' +
        '%3A33%3A-61%3A4%3A-1d%3A34%3A2d%3A54%3A68%3A1f%3A-14%3A48%3A-7f' +
        '%3A68%3A53%3A-26%3A-2d%3A3f%3A-71%3A0%3A7a%3A3b%3A34%3A-1b%3A-5' +
        '0%3A30%3A-35%3A62%3A56%3A-18%3A7%3A35%3A-6%3A69%3A-14%3A6f%3A35' +
        '%3A-7b%3A4b%3A-2c%3A-6d%3A76%3A-61%3A-20%3A-49%3A-13%3A42%3A4d%' +
        '3A46%3A-5a%3A-30%3A6d%3A14%3A4d%3A46%3A6a%3A77%3A2f%3A-26%3A44%' +
        '3A3%3A-3a%3A-26%3A-56%3A1d%3A-30%3A-e%3A-6a%3A-80%3A-28%3A-4a%3' +
        'A5a%3A-4c%3A1e%3A4f%3A44%3A50%3A3a%3A78%3A-16%3A8%3A-56%3A-47%3' +
        'A-20%3A4c%3A-39%3A-1%3A-d%3A4b%3A25%3A-70%3A-22%3A-44%3A-73%3A-' +
        '25%3A-1%3A-2%3A6e%3A-40%3A37%3A56%3A4b%3A25%3A42%3A-72%3Ad%3A48' +
        '%3A4e%3A51%3A54%3A-3a%3A67%3A-64%3A-7b%3A-51%3A7%3A-4f%3A-29%3A' +
        '-78%3A-1b%3A-78%3A-62%3A-6e%3A-1c%3A-7%3A-34%3A-39%3A6e%3A-62%3' +
        'A21%3A-75%3A58%3A-6d%3A-2b%3A-6e%3A-6d%3A66%3A0%3A-24%3A-73%3A7' +
        '7%3A36%3A-23%3A-76%3A-1e%3A1b%3A-15%3A-44%3A5a%3A-3%3A61%3A-6e%' +
        '3A-44%3A49%3A-11%3A38%3A-46%3A54%3A-37%3A-33%3A23%3A2d%3A-3f%3A' +
        '-37%3A-7e%3A50%3A6%3A4e%3A12%3A-6e%3A-2b%3A24%3A-5%3A7e%3A4%3A-' +
        '37%3A33%3A-18%3A29%3A1a%3Ac%3A18%3A-7d%3A-52%3A60%3A-5f%3A-5f%3' +
        'A-28%3A-62%3A74%3A0%3A52%3Ac%3A-24%3A7e%3A-43%3A60%3A-1c%3A55%3' +
        'A-a%3A1f%3A-3%3Ad%3A68%3A2b%3A58%3A2e%3A7e%3A7f%3A27%3A31%3A29%' +
        '3A55%3A2%3A-65%3A5%3A-5c%3A-55%3A-65%3A-5a%3A5e%3A51%3A7b%3A-59' +
        '%3A-4%3A-55%3A66%3A6c&sortBy=beginDate&sortByIndex=5&sortByDesc' +
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
    req.add_header('Pragma', ' no-cache')
    req.add_header('Origin', 'http://www.purchasing.cityofno.com')
    req.add_header('Accept-Encoding', 'gzip, deflate')
    req.add_header('Content-Type', 'application/x-www-form-urlencoded')
    req.add_header(
        'Accept',
        'text/add_contracthtml,application/xhtml+xml,application/xml;' +
        'q=0.9,image/webp,*/*;q=0.8'
    )
    req.add_header('Cache-Control', 'no-cache')
    req.add_header(
        'Referer',
        'http://www.purchasing.cityofno.com/bso/external/advsearch/' +
        'searchContract.sdo'
    )
    req.add_header('Connection', 'keep-alive')
    req.add_header('DNT', '1')

    output = ""
    response = urllib2.urlopen(req)
    output = response.read()
    response.close()

    return output


def get_po_numbers_from_index_page(html):
    '''
    Take an index page of contracts. Return the contract numbers.
    '''

    pattern = '(?<=docId=)[A-Z][A-Z][0-9]+'
    return re.findall(pattern, html)


def valid_po(purchase_order_no):
    """
    A simple method to determine if this is a valid purchase order.
    """

    po_re = r'[A-Z]{2}\d{3,}'
    po_regex = re.compile(po_re)
    if po_regex.match(purchase_order_no):
        return True
    else:
        return False
