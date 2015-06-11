#!/bin/bash

source `which virtualenvwrapper.sh`

workon contracts

echo "\nChecking the city's purchasing site for new contracts..."
python $PYTHONPATH/contracts/lib/check_city.py

deactivate
