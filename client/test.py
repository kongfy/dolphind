# -*- coding: utf-8 -*-

"""
Test script for dolphind web interface,
Just simulate the function call.
"""

__authors__ = [
    '"Fanyu Kong" <me@kongfy.com>',
]

from twisted.web.xmlrpc import Proxy
from twisted.internet import reactor

from optparse import OptionParser
import datetime
from common.config import CFG
import MySQLdb

def success_callback(value):
    """
    Callback method for rpc calls return successful.

    :param value: return value
    """

    reactor.stop()

def error_callback(error):
    """
    Callback method for rpc calls return an error.

    :param error: error from rpc
    """

    print error
    reactor.stop()

def make_task(number, type):
    conn = MySQLdb.connect(host=CFG['database']['host'],
                           port=int(CFG['database']['port']),
                           user=CFG['database']['user'],
                           passwd=CFG['database']['passwd'],
                           db=CFG['database']['db'])

    conn.autocommit(True)
    cur = conn.cursor()

    sql = 'DELETE FROM `ipmi_info`'
    cur.execute(sql)
    sql = 'ALTER TABLE `ipmi_info` AUTO_INCREMENT = 1'
    cur.execute(sql)

    sql = 'DELETE FROM `ipmi_requesthost`'
    cur.execute(sql)
    sql = 'ALTER TABLE `ipmi_requesthost` AUTO_INCREMENT = 1'
    cur.execute(sql)

    sql = 'DELETE FROM `ipmi_request`'
    cur.execute(sql)
    sql = 'ALTER TABLE `ipmi_request` AUTO_INCREMENT = 1'
    cur.execute(sql)

    sql = "INSERT INTO `ipmi_request` (`id`, `start_time`, `end_time`, `status`, `detail`) VALUES (NULL, '0', '0', '0', '')"
    cur.execute(sql)
    tid = int(cur.lastrowid)

    for i in xrange(number):
        sql = "INSERT INTO `ipmi_requesthost` (`id`, `ip_addr`, `username`, `password`, `start_time`, `end_time`, `status`, `detail`, `request_id`) VALUES (NULL, '192.168.0.1', 'root', 'root', '0', NULL, '0', '', '%s')" % tid
        cur.execute(sql)

    cur.close()
    conn.close()

    return tid

def main():
    """
    script main function
    """

    parser = OptionParser()
    parser.add_option("-n", "--number", dest="number", action="store",
                      help="amount of machine to query",)
    parser.add_option("-t", "--type", dest="type", action="store",
                      help="type",)
    options, _ = parser.parse_args()

    tid = make_task(int(options.number), int(options.type))

    url = 'http://%s:%s' % (CFG['client']['server'], CFG['client']['port'])
    proxy = Proxy(url)

    methods = {0 : 'naive',
               1 : 'request',}

    print methods[int(options.type)]

    proxy.callRemote(methods[int(options.type)],
                     tid,
                     'http://127.0.0.1/dolphin/callback').addCallbacks(success_callback, error_callback)

    reactor.run()

if __name__ == '__main__':
    main()
