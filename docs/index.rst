.. City of New Orleans contracts documentation master file, created by
   sphinx-quickstart on Mon May 18 17:34:07 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

City of New Orleans contracts
=============================

http://vault.thelensnola.org/contracts

A permanent collection of the City of New Orleans contracts that is fully searchable and updated daily. You can search by keyword, contractor or city department and download a copy of the contract. Unlike the city's contract portal, our collection is ongoing and includes both present and past contracts.

Find out how to read a contract `here <http://thelensnola.org/2014/05/29/how-to-read-a-government-contract/>`__ and read more about this project `here <http://thelensnola.org/search-new-orleans-government-contracts/>`__ and `here <http://thelensnola.org/2014/06/12/the-lens-launches-the-vault-to-bring-greater-openness-to-government-contracting/>`__.

What follows is the technical documentation to help understand and maintain our open-source project.

The three main areas
--------------------

The primary things to focus on are our local (server) database, our local contract repository and our DocumentCloud project (remote), which acts as both a database and a repository.

Daily processes
---------------

Every day, a cron job runs :code:`__main.sh__`. This calls on :code:`check_city.py`, which checks the city's purchasing site. For each of ....  for any new contracts :code:`utilities.py`.

Packages
--------

.. toctree::
   :maxdepth: 2
   :name: mastertoc

   contracts
   lib
   parserator
   pythondocumentcloud
   tests

Modules
-------

* :ref:`modindex`
