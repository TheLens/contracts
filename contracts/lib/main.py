
"""
This script runs the daily downloader.
"""

import time
from contracts.lib.utilities import Utilities

if __name__ == '__main__':
    pages = range(1, 11)

    for page in pages:
        Utilities().scan_index_page(page)
        time.sleep(60)
