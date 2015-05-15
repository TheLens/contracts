[![Build Status](https://travis-ci.org/TheLens/contracts.svg?branch=master)](https://travis-ci.org/TheLens/contracts) [![Documentation Status](https://readthedocs.org/projects/city-of-new-orleans-contracts/badge/?version=latest)](https://readthedocs.org/projects/city-of-new-orleans-contracts/?badge=latest) [![Coverage Status](https://coveralls.io/repos/TheLens/contracts/badge.svg)](https://coveralls.io/r/TheLens/contracts)

# New Orleans contracts

[vault.thelensnola.org/contracts](http://vault.thelensnola.org/contracts)

An archive of the City of New Orleans' contracts, updated daily. 

## Back end

#### `contracts/logs`

Stores the application logs. Used mainly for debugging.

#### `contracts/datamanagement`

This stores the tools that collect and publish city contracts. It downloads posted contracts from the city, uploads them to DocumentCloud and does some backend housekeeping to keep the Lens' web application and the DocumentCloud repo in sync.

#### `contracts/datamanagement/federal`

These scripts get federal data (via the sunlight foundation). This data is not used in the app yet.

#### `contracts/lib`

This stores the classes that are used in the application. vaultclasses.py has the models that map to the underlying database via sql alchemy.

#### `app.ini`

A standard uwsgi configuration file for our server.

## Front end

#### `/contracts/app.py`

This is the main public-facing web application. It lets the public search City of New Orleans contracts that are posted to the city's purchasing portal. It's just a Flask application, and it follows the structure from the Flask tutorials. The front end is built with Foundation. It uses SQL Alchemy to connect to a PostgreSQL database.

#### `/contracts/models.py`

The logic behind `app.py`, including database queries.

#### `/contracts/views.py`

Renders the data provided by `models.py` and returns to `app.py` for the user.

## Synchronization

DocumentCloud takes a minute to process the documents. So `lens_doc_cloud_sync.py` runs some time after `main.sh` in order to sync the database with the DocumentCloud repo.

## Testing

#### `test_pep8.py`

Ensures that all Python files conform to the PEP8 coding standards.

#### `test_pylint.py`

Ensures that no Python files have any errors, according to the `pylint` package.
