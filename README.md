#Welcome to the Vault!

`/app` -- This is the main public-facing web application. It lets the public search New Orleans city contracts that are posted to the city's purchasing portal. It's just a Flask application, and it follows the structure from the flask tutorials. The front end is built with Foundation. It uses sqlalchemy to connect to postgres. We'd like to refactor it to use Flask views but haven't gotten there yet.

`contracts/datamanagement` -- This stores the tools that collect and publish city contracts. It downloads posted contracts from the city, uploads them to DocumentCloud and does some backend housekeeping to keep the Lens' web application and the DocumentCloud repo in sync.

`contracts/lib` -- This stores the classes that are used in the application. vaultclasses.py has the models that map to the underlying database via sql alchemy.

`app.ini` uwsgi configuration file.

#Synching

Doc cloud takes a minute to process the doc. So lensDocCloudSynch.py runs some time after main.sh in order to synch the postgres db with the doc cloud repo.

Test