#!/bin/bash

source `which virtualenvwrapper.sh`

workon contracts

echo "Finding links between things..."
python contracts/lib/daily_linker.py

echo "Sending an email with found links..."
python contracts/lib/emailer.py

deactivate
