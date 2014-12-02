# -*- coding: utf-8 -*-

"""
Database model, contain a global database connection pool

DBPOOL : global database connection pool for dolphin
"""

from twisted.enterprise import adbapi

from common import config

DBPOOL = adbapi.ConnectionPool("MySQLdb",
                               host=config.CFG['database']['host'],
                               port=int(config.CFG['database']['port']),
                               user=config.CFG['database']['user'],
                               passwd=config.CFG['database']['passwd'],
                               db=config.CFG['database']['db'],
                               cp_reconnect=True)
