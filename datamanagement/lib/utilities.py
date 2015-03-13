import ConfigParser

CONFIG_LOCATION = '/apps/contracts/app.cfg'

def get_from_config(field):
    config = ConfigParser.RawConfigParser()
    config.read(CONFIG_LOCATION)
    return config.get('Section1', field)
