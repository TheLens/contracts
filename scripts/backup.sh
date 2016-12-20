#!/bin/bash

source `which virtualenvwrapper.sh`

workon contracts

# TODO: okay?
echo "Creating backups..."
python contracts/lib/backup.py

deactivate
