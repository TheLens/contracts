
"""
This script runs the daily downloader.
"""

from contracts.lib.models import check_page

if __name__ == '__main__':
    pages = range(1, 11)

    for page in pages:
        check_page(page)
