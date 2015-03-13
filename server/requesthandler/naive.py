# -*- coding: utf-8 -*-

"""
Naive Request
"""

__authors__ = [
    '"Fanyu Kong" <me@kongfy.com>',
]

import datetime
import json
import subprocess
import interpreter
from common import config
import MySQLdb

LOGTAG = __name__
FORMAT = 'ipmitool -I lanplus -H %s -U %s -P %s sel list -vv'

def command(host, user, passwd):
    """
    Reform the command format for twistd utils input

    :param host:   ipmi target's IPv4 address
    :param user:   ipmi username
    :param passwd: ipmi password
    :returns:      ('ipmitool', ['-I', ...])
    """

    cmd = FORMAT % (host, user, passwd)
    return cmd.split()

class Naive(object):

    def __init__(self, request_id):
        self._request_id = request_id
        self._count = 0    # total number of hosts annexed to this request
        self._succeed = 0  # total number of success host currently
        self._failed = 0   # total number of failed host currently
        self._status = 0   # initialize status, 0-ready 1-running 2-finish 3-failed
        self._conn = MySQLdb.connect(host=config.CFG['database']['host'],
                                     port=int(config.CFG['database']['port']),
                                     user=config.CFG['database']['user'],
                                     passwd=config.CFG['database']['passwd'],
                                     db=config.CFG['database']['db'])

        self._conn.autocommit(True)
        self._cur = self._conn.cursor()

    def _data_convertor(self, ipmi_info, hostrequest_id):
        return [[sel_id, sel_type, sel_datetime, level, severity, desc, json.dumps(info),
                 self._request_id, hostrequest_id]
                for sel_id, sel_type, sel_datetime, level, severity, desc, info in ipmi_info]


    def start(self):
        """
        entry point.
        """

        starttime = datetime.datetime.now()

        #do something
        # ((1L, datetime.datetime(2009, 6, 9, 0, 24, 8), datetime.datetime(2009, 6, 9, 0, 24, 8), 1, 'No detail'),)
        sql = 'SELECT * FROM ipmi_request WHERE id = %s'
        length = self._cur.execute(sql, (self._request_id, ))
        info = self._cur.fetchmany(length)
        (rid, start_time, end_time, status, detail), = info

        # ((2L, '192.168.0.120', 'root', 'MhxzKhl', datetime.datetime(2014, 11, 10, 0, 0), None, 0, '', 1L), ...)
        sql = 'SELECT * FROM ipmi_requesthost WHERE request_id = %s'
        length = self._cur.execute(sql, (self._request_id, ))
        info = self._cur.fetchmany(length)
        self._count = len(info)

        self._status = 1  # running
        sql = 'UPDATE ipmi_request SET status = %s, detail = %s WHERE id = %s'
        self._cur.execute(sql, (self._status, '%s targets found' % self._count, self._request_id))

        for host in info:
            hostrequest_id, ip_addr, username, password, start_time, end_time, status, detail, _ = host
            sql = 'UPDATE ipmi_requesthost SET status = %s, start_time = %s WHERE id = %s'
            self._cur.execute(sql, (1,
                                    datetime.datetime.now(),
                                    hostrequest_id))

            # do work
            p = subprocess.Popen(command(ip_addr, username, password), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = p.communicate()
            ipmi_info = interpreter.interpret(out, err)

            sql = 'INSERT INTO ipmi_info(sel_id, sel_type, sel_timestamp, sel_level, sel_severity, sel_desc, sel_info, request_id, host_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)'
            length = self._cur.executemany(sql, self._data_convertor(ipmi_info, hostrequest_id))

            sql = 'UPDATE ipmi_requesthost SET status = %s, end_time = %s WHERE id = %s'
            self._cur.execute(sql, (2,
                                    datetime.datetime.now(),
                                    hostrequest_id))
            self._succeed += 1

        self._status = 2
        sql = 'UPDATE ipmi_request SET status = %s, end_time = %s, detail = %s WHERE id = %s'
        self._cur.execute(sql, (self._status,
                                datetime.datetime.now(),
                                '%s/%s succeed' % (self._succeed, self._count),
                                self._request_id))

        self._cur.close()
        self._conn.close()

        endtime = datetime.datetime.now()
        interval = endtime - starttime
        print 'Time for %s : %s' % (self._request_id, interval)
