import datetime
from vaultclasses import Vendor, Department, Contract, Person, VendorOfficer, VendorOfficerCompany, Company
from documentcloud import DocumentCloud
from address import AddressParser, Address
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Date, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
import ConfigParser



CONFIG_LOCATION = '/apps/contracts/app.cfg'


def get_from_config(field):
    config = ConfigParser.RawConfigParser()
    config.read(CONFIG_LOCATION)
    return config.get('Section1', field)

server = get_from_config('server')
databasepassword = get_from_config('databasepassword')
database = get_from_config('database')
user = get_from_config('user')

engine = create_engine('postgresql://abe:' + databasepassword + '@' + server + ':5432/' + database)

def get_daily_contracts(today_string = datetime.datetime.today().strftime('%Y-%m-%d')):  #defaults to today
    Session = sessionmaker(bind=engine)
    Session.configure(bind=engine)
    session = Session()
    contracts = session.query(Contract).filter(Contract.dateadded==today_string).all()
    session.close()
    return contracts

print get_daily_contracts()