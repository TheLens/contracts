#!/bin/bash

source `which virtualenvwrapper.sh`

workon contracts

python contracts/lib/check_city.py

deactivate
