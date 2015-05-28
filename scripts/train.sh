workon contracts # start the venv
rm -rf xml # remove the xml directory
mkdir xml # create a new one

#copy down all of the human labels
aws s3 cp --recursive s3://lensnola/contracts/contract_amounts/human_labels/ xml --acl public-read

# run parserator on the xml files, using the contract parser
parserator train "./xml/*.xml" contract_parser
deactivate