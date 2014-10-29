# -*- coding: utf-8 -*-

"""
Config module used to load the config file.

CFG : globle Config() instance.
"""

__authors__ = [
    '"Fanyu Kong" <me@kongfy.com>',
]

from ConfigParser import ConfigParser
from common import singleton

@singleton.singleton
class Config(object):
    """
    Config class, used to load 'config.ini' when program start.
    should be global singleton when program is running.
    """

    def __init__(self):
        self._config = ConfigParser()
        self._config.read(CONFIGFILE)

    def __getitem__(self, key):
        return dict(self._config.items(key))

CONFIGFILE = 'config.ini'    # name of config file
CFG = Config()               # singleton CFG instance
