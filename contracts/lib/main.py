
"""
This script runs the daily downloader.
"""

from contracts.lib.lens_doc_cloud_sync import (
    match_lens_db_to_document_cloud
)
from contracts.lib.models import check_page

if __name__ == '__main__':
    match_lens_db_to_document_cloud()

    pages = range(1, 11)

    for page in pages:
        check_page(page)
