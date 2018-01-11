#!/bin/bash

source `which virtualenvwrapper.sh`

workon contracts

python $PYTHONPATH/contracts/lib/sync_local_database_document_cloud.py

deactivate
