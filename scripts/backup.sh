#!/bin/bash

source `which virtualenvwrapper.sh`

workon contracts

# TODO: okay?
echo "Creating backups..."
python $PYTHONPATH/contracts/lib/backup.py

deactivate
