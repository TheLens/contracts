#!/usr/bin/python
"""
Holds the settings so that they are accessible to other classes.
Actual configurations are stored in /configs/contracts.cfg, outside the repo.
In other words: the actual configurations are not posted to github!
"""
import ConfigParser


class Settings():

    def __init__(self):
        """
        Initialize settings from a config file
        """
        self.CONFIG_LOCATION = "/configs/contracts.cfg"
        self.server = self.get_from_config('server')
        self.databasepassword = self.get_from_config('databasepassword')
        self.user = self.get_from_config('user')
        self.corpus_loc = self.get_from_config('corpus_loc')
        self.database = self.get_from_config('database')
        self.doc_cloud_user = self.get_from_config('doc_cloud_user')
        self.doc_cloud_password = self.get_from_config('doc_cloud_password')
        self.root_folder = self.get_from_config('root_folder')
        self.log = self.get_from_config('log_location')
        self.vendors_location = self.corpus_loc + "/vendors/"
        self.purchase_order_location = self.corpus_loc + "/purchaseorders/"
        self.bids_location = self.corpus_loc + "/bids/"
        self.connection_string = 'postgresql://' + \
            self.user + ':' + self.databasepassword + \
            '@' + self.server + ':5432/' + self.database
        self.templates = self.root_folder + "/contracts/templates"

    def get_from_config(self, field):
        config = ConfigParser.RawConfigParser()
        config.read(self.CONFIG_LOCATION)
        return config.get('Section1', field)
