#!/bin/bash

source `which virtualenvwrapper.sh`

workon contracts

python $PYTHONPATH/contracts/lib/check_city.py

deactivate
