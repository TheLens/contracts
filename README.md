# City of New Orleans contracts

[https://vault.thelensnola.org/contracts](https://vault.thelensnola.org/contracts)

A permanent collection of the City of New Orleans contracts that is fully searchable and updated daily. You can search by keyword, contractor, city department or company officer, and can download PDF copies of the contracts. Unlike the city's contract portal, our collection is ongoing and includes both present and past contracts.

Not sure how to read a government contract? Our city hall reporter wrote a detailed guide [here](http://thelensnola.org/2014/05/29/how-to-read-a-government-contract/). You can read more about this project [here](http://thelensnola.org/search-new-orleans-government-contracts/) and [here](http://thelensnola.org/2014/06/12/the-lens-launches-the-vault-to-bring-greater-openness-to-government-contracting/).

[![Build Status](https://travis-ci.org/TheLens/contracts.svg?branch=master)](https://travis-ci.org/TheLens/contracts) [![Coverage Status](https://coveralls.io/repos/TheLens/contracts/badge.svg)](https://coveralls.io/r/TheLens/contracts)

- Issues, suggestions and feature requests: https://github.com/TheLens/contracts/issues
- Tests: https://travis-ci.org/TheLens/contracts
- Testing coverage: https://coveralls.io/r/TheLens/contracts

### Setup

Make a new virtual environment (`mkvirtualenv`).

Pull down this repo.

Install pip dependencies in `requirements.txt`.

Add your environment variables.

Set up cron jobs.

Symlink `confs/contracts.conf` to `/etc/init` say that Upstart automatically runs app.

### Environment variables

Add these as part of your virtual environment (`~/.virtualenvs/contracts/bin/postactivate`). Ex. export ENVVAR=myvar

```bash
export DOCUMENT_CLOUD_USERNAME=username
export DOCUMENT_CLOUD_PASSWORD=password
DOCUMENT_CLOUD_USERNAME=username
DOCUMENT_CLOUD_PASSWORD=password
```

### Credit

Abe Handler built The Vault and continues to contribute to the project. Thomas Thoren is now the main developer, and can be reached at tthoren@thelensnola.org.
