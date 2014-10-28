from ConfigParser import ConfigParser
from common import singleton

@singleton.singleton
class Config(object):
    def __init__(self):
        "docstring"
        self._config = ConfigParser()
        self._config.read(CONFIGFILE)

    def __getitem__(self, key):
        return dict(self._config.items(key))

CONFIGFILE = 'config.ini'
CFG = Config()
