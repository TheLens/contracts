# New Orleans government contracts and documents

[http://vault.thelensnola.org/contracts/](http://vault.thelensnola.org/contracts/)

A permanent collection of New Orleans government contracts and financial disclosure forms that is fully searchable and updated daily. You can search by keyword, contractor, city department or company officer, and can download PDF copies of the contracts. Unlike the city's contract portal, our collection is ongoing and includes both present and past contracts.

Not sure how to read a government contract? Our city hall reporter, Charles Maldonado, wrote a detailed guide [here](http://thelensnola.org/2014/05/29/how-to-read-a-government-contract/). You can read more about this project [here](http://thelensnola.org/search-new-orleans-government-contracts/) and [here](http://thelensnola.org/2014/06/12/the-lens-launches-the-vault-to-bring-greater-openness-to-government-contracting/).

[![Build Status](https://travis-ci.org/TheLens/contracts.svg?branch=master)](https://travis-ci.org/TheLens/contracts) [![Coverage Status](https://coveralls.io/repos/TheLens/contracts/badge.svg)](https://coveralls.io/r/TheLens/contracts)

* Issues and suggestions: https://github.com/TheLens/contracts/issues
* Test coverage: https://coveralls.io/r/TheLens/contracts
* Tests: https://travis-ci.org/TheLens/contracts

### How it works

The primary things to focus on are:

* Local (server) database
* Local contract repository
* The Lens' DocumentCloud project (remote), which acts as both a database and a repository.

__Daily processes__

Every day, a cron job runs `__main.sh__`, which in turn runs `main.py`. That script checks the city's purchasing site.

For each new contract found, a copy is downloaded to TK.

That/those files are uploaded to our DocumentCloud project and our database is updated to reflect the changes.

TK TK

__Front end__

TK

Queries on the front end only interact with TK (DocCloud, our database, our local storage?)

__Back end__

TK

### Setup

__Dependencies__

* [DocumentCloud](https://www.documentcloud.org/)
* [pip](http://pip.readthedocs.org/en/stable/installing/)
* [PostgreSQL](http://www.postgresql.org/)
* Python 2.7
* [python-documentcloud](http://python-documentcloud.readthedocs.org/en/latest/)
* [virtualenvwrapper](https://virtualenvwrapper.readthedocs.org/en/latest/)
* Python packages listed in `requirements.txt`

1.) Make a new virtual environment project. Using [virtualenvwrapper](https://virtualenvwrapper.readthedocs.org/en/latest/) from the command line:
```bash
mkvirtualenv contracts
```

2.) Download a copy of this repo.
```bash
git clone https://github.com/TheLens/contracts.git
```

3.) Install dependencies using [pip](http://pip.readthedocs.org/en/stable/installing/).
```bash
cd contracts
pip install -r requirements.txt
```

4.) Add your environment variables (see below).

5.) Start cron jobs by copying the contents of `crontab` into your user's crontab file.

__Environment variables__

Add these as part of your virtual environment (`~/.virtualenvs/contracts/bin/postactivate`).

```bash
export DATABASE_USERNAME=...
export DATABASE_PASSWORD=...
export EMAIL_FROM=...                # (Sender account)
export EMAIL_TO_LIST=...             # (Recipient accounts)
export GMAIL_USERNAME=...            # (Sender account)
export GMAIL_PASSWORD=...            # (Recipient accounts)
export DOCUMENT_CLOUD_USERNAME=...
export DOCUMENT_CLOUD_PASSWORD=...
export CONTRACTS_ADMIN_USERNAME=...  # (Admin. pages, i.e. parserator)
export CONTRACTS_ADMIN_PASSWORD=...
```

### Uploading a collection of documents

Use the [`dcupload`](https://github.com/onyxfish/dcupload) library by Chris Groskopf for one-time uploads of document collections.

```bash
dcupload [options] <files_directory>

Options:
    --username
    --password
    --access
    --source
    --project
```

### Credit

Abe Handler developed The Vault and Thomas Thoren (tthoren@thelensnola.org) now maintains the project.
