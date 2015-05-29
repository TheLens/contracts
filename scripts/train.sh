#!/bin/bash
workon contracts # start the venv
rm -rf data/xml # remove the xml directory
mkdir data/xml # create a new one

#copy down all of the human labels
aws s3 cp --recursive s3://lensnola/contracts/contract_amounts/human_labels/ data/xml --acl public-read

# run parserator on the xml files, using the contract parser
parserator train "data/xml/*.xml" parser/
deactivate
