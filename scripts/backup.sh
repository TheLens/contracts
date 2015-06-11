#!/bin/bash

source `which virtualenvwrapper.sh`

workon contracts

# TODO: okay?
echo "Creating backups..."
python $PYTHONPATH/contracts/lib/backup.py

# Database dump
pg_dump contracts > /backups/contracts/database/$(date +%Y-%m-%d).sql
pg_dump campaigncontributions > /backups/campaign-contributions/$(date +%Y-%m-%d).sql

# Copy files to S3
aws s3 sync /backups/contracts/ s3://lensnola/backups/
aws s3 sync /backups/campaign-contributions/ s3://lensnola/backups/

deactivate
