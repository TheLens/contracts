import ConfigParser

class Settings():

    def __init__(self):
    	self.CONFIG_LOCATION = "app.cfg"
        self.server = self.get_from_config('server')
        self.databasepassword = self.get_from_config('databasepassword')
        self.user = self.get_from_config('user')
        self.corpus_loc = self.get_from_config('corpus_loc')
        self.database = self.get_from_config('database')
        self.doc_cloud_user = self.get_from_config('doc_cloud_user')
        self.doc_cloud_password = self.get_from_config('doc_cloud_password')

    def get_from_config(self, field):
        config = ConfigParser.RawConfigParser()
        config.read(self.CONFIG_LOCATION)
        return config.get('Section1', field)