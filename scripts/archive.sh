#!/bin/bash

source `which virtualenvwrapper.sh`
workon contracts
python $PROJECT_DIRECTORY/scripts/archive.py
deactivate
