#Welcome to the Vault!


`/app` -- This is the main public-facing web application. It lets the public search New Orleans city contracts like searching Google. It's just a Flask application, and it follows the structure from the flask tutorials. The front end is built with Foundation. It uses sqlalchemy to connect to postgres. We'd like to refactor it to use Flask views but haven't gotten there yet.


`contracts/datamanagement` -- This stores the tools that collect and publish city contracts. It downloads contracts from the city, uploads them to DocumentCloud and keeps the web application up to date.


#Synching

Doc cloud takes a minute to process the doc. So lensDocCloudSynch.py runs some time after main.sh in order to synch the postgres db with the doc cloud repo.

Test