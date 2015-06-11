# City of New Orleans contracts

[vault.thelensnola.org/contracts](http://vault.thelensnola.org/contracts)

A permanent collection of the City of New Orleans contracts that is fully searchable and updated daily. You can search by keyword, contractor, city department or company officer, and can download PDF copies of the contracts. Unlike the city's contract portal, our collection is ongoing and includes both present and past contracts.

Not sure how to read a government contract? Our city hall reporter wrote a detailed guide [here](http://thelensnola.org/2014/05/29/how-to-read-a-government-contract/). You can read more about this project [here](http://thelensnola.org/search-new-orleans-government-contracts/) and [here](http://thelensnola.org/2014/06/12/the-lens-launches-the-vault-to-bring-greater-openness-to-government-contracting/).

[![Build Status](https://travis-ci.org/TheLens/contracts.svg?branch=master)](https://travis-ci.org/TheLens/contracts) [![Documentation Status](https://readthedocs.org/projects/city-of-new-orleans-contracts/badge/?version=latest)](https://readthedocs.org/projects/city-of-new-orleans-contracts/?badge=latest) [![Coverage Status](https://coveralls.io/repos/TheLens/contracts/badge.svg)](https://coveralls.io/r/TheLens/contracts)

Documentation: https://city-of-new-orleans-contracts.readthedocs.org/

Issues, suggestions and requests: https://github.com/TheLens/contracts/issues

Tests: https://travis-ci.org/TheLens/contracts

Testing coverage: https://coveralls.io/r/TheLens/contracts


### Setup

Make a new virtual environment (`mkvirtualenv`).

Download a copy of this repo.

Run `python setup.py install` to get started. This will build out the project and download any necessary dependencies using `pip`.

Add your environment variables.

Start cron jobs.

### Environment variables

Add these as part of your virtual environment (`~/.virtualenvs/contracts/bin/postactivate`). Ex. export ENVVAR=myvar

* DATABASE_USERNAME
* DATABASE_PASSWORD
* EMAIL_FROM (the account sending the email alerts)
* EMAIL_TO_LIST (the accounts to send email alerts to)
* GMAIL_USERNAME (the account sending the email alerts)
* GMAIL_PASSWORD (the password for the account sending email alerts)
* DOCUMENT_CLOUD_USERNAME
* DOCUMENT_CLOUD_PASSWORD
* CONTRACTS_ADMIN_USERNAME (for accessing administrative web pages, i.e. parserator)
* CONTRACTS_ADMIN_PASSWORD (administrative web page password)

### Credit

Abe Handler built The Vault and continues to contribute to the project. Thomas Thoren is now the main developer, and can be reached at tthoren@thelensnola.org. 
