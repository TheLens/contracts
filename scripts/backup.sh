#!/bin/bash

source `which virtualenvwrapper.sh`

workon contracts

### Database dumps ###
pg_dump contracts > /backups/contracts/database/contracts-db-$(date +%Y-%m-%d).sql


### Copy files to S3 ###
# aws s3 cp /backups/contracts/contracts-db-$(date +%Y-%m-%d).sql s3://lensnola/backups/contracts-db-$(date +%Y-%m-%d).sql

aws s3 sync /backups/contracts/ s3://lensnola/backups/

deactivate
