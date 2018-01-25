# City of New Orleans contracts

[https://vault.thelensnola.org/contracts](https://vault.thelensnola.org/contracts)

[![Build Status](https://travis-ci.org/TheLens/contracts.svg?branch=master)](https://travis-ci.org/TheLens/contracts)

- Issues: https://github.com/TheLens/contracts/issues
- Tests: https://travis-ci.org/TheLens/contracts

A permanent collection of the City of New Orleans contracts that is fully searchable and updated daily. You can search by keyword, contractor, city department or company officer and can download PDF copies of the contracts. Unlike the city's contract portal, our collection is ongoing and includes both present and past contracts.

Not sure how to read a government contract? Our city hall reporter wrote a [detailed guide](http://thelensnola.org/2014/05/29/how-to-read-a-government-contract/). Read more about this project:

- [http://thelensnola.org/search-new-orleans-government-contracts/](http://thelensnola.org/search-new-orleans-government-contracts/)
- [http://thelensnola.org/2014/06/12/the-lens-launches-the-vault-to-bring-greater-openness-to-government-contracting/](http://thelensnola.org/2014/06/12/the-lens-launches-the-vault-to-bring-greater-openness-to-government-contracting/).

## Setup

Requirements

- Python 2.7
- DocumentCloud account

Make a virtual environment.

```bash
mkvirtualenv contracts
```

Pull down this repo.

```bash
git clone git@github.com:TheLens/contracts.git
```

Install dependencies.

```bash
pip install -r requirements.txt
```

Set environment variables.

```bash
export DOCUMENT_CLOUD_USERNAME=username
export DOCUMENT_CLOUD_PASSWORD=password
```

Set up the cron job in [`crontab`](crontab).

On the host server, symlink [`confs/contracts.conf`](confs/contracts.conf) to `/etc/init` so Upstart automatically runs the application on startup.

```bash
ln -s confs/contracts.conf /etc/initcontracts.conf
```

## Credit

- Abe Handler
- Thomas Thoren (tthoren@thelensnola.org)
