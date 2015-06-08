#!/bin/bash

source `which virtualenvwrapper.sh`

workon contracts

# Database dump
pg_dump contracts > /backups/contracts/database/contracts-db-$(date +%Y-%m-%d).sql

# Copy files to S3
aws s3 sync /backups/contracts/ s3://lensnola/backups/

deactivate
