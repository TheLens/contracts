#!/bin/bash

# TODO:
# This will be run multiple times per day in order to spread the views on the
# city's website. Therefore, once-per-day scripts like daily_linker should go in
# their own shell scripts.

source `which virtualenvwrapper.sh`

workon contracts

echo "Checking the city's purchasing site for new contracts..."
python $PYTHONPATH/contracts/lib/check_city.py

echo "Finding links between things..."
python $PYTHONPATH/contracts/lib/daily_linker.py

echo "Sending an email with found links..."
python $PYTHONPATH/contracts/lib/emailer.py

echo "Creating backups..."
python $PYTHONPATH/contracts/lib/backup.py

deactivate
