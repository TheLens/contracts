#!/bin/bash

source `which virtualenvwrapper.sh`

workon contracts

echo "Finding links between things..."
python $PYTHONPATH/contracts/lib/daily_linker.py

echo "Sending an email with found links..."
python $PYTHONPATH/contracts/lib/emailer.py

deactivate
