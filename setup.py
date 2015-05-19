# -*- coding: utf-8 -*-
import os
from setuptools import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name='contracts',
    version='0.0.1',
    packages=(
        'contracts',
        'contracts.lib',
        'tests',
    ),
    data_files=[
        (".", ["README.md", "requirements.txt"]),
        ("logs", ["logs/contracts.log"]),
        ("scripts", [
            "scripts/main.sh",
            "scripts/sync_with_document_cloud.sh",
            "scripts/updatebackup.sh"])
    ],
    include_package_data=True,
    license='MIT',
    description=(
        "A package for scraping and publishing " +
        "City of New Orleans contracts."),
    long_description=read('README.md'),
    keywords="The Lens contracts",
    url='http://vault.thelensnola.org/contracts/',
    author='The Lens',
    author_email='tthoren@thelensnola.org',
    install_requires=(
        'alabaster',
        'astroid',
        'Babel',
        'beautifulsoup4',
        'coverage',
        'docutils',
        'ecdsa',
        'Fabric',
        'Flask',
        'Flask-Cache',
        'itsdangerous',
        'Jinja2',
        'logilab-common',
        'MarkupSafe',
        'nose',
        'paramiko',
        'pep8',
        'pip',
        'psycopg2',
        'pycrypto',
        'Pygments',
        'pylint',
        'python-coveralls',
        'python-dateutil',
        'pytz',
        'PyYAML',
        'requests',
        'requests-oauthlib',
        'selenium',
        'setuptools',
        'sh',
        'simplejson',
        'six',
        'snowballstemmer',
        'Sphinx',
        'sphinx-rtd-theme',
        'SQLAlchemy',
        'Werkzeug',
    ),
)
