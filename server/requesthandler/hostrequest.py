# -*- coding: utf-8 -*-

"""
IPMI request for a single host
"""

__authors__ = [
    '"Fanyu Kong" <me@kongfy.com>',
]

from twisted.internet import defer
from twisted.python import log

import datetime
import json

from common import db
from common import exception
from ipmihandler import manager

LOGTAG = __name__

class HostRequest(object):
    """
    IPMI request for a single host
    """

    def __init__(self,
                 hostrequest_id,
                 ip_addr,
                 username,
                 password,
                 start_time,
                 end_time,
                 status,
                 detail,
                 request_id):

        self._hostrequest_id = hostrequest_id
        self._ip_addr = ip_addr
        self._username = username
        self._password = password
        self._start_time = start_time
        self._end_time = end_time
        self._status = status    # 0-ready, 1-running, 2-finish, 3-failed
        self._detail = detail
        self._request_id = request_id
        self._manager = manager.Manager()
        self.d = None

    def _ipmi_succeed(self, res):
        """
        Get called when ipmitool succeed.
        """

        self._status = 2
        d = db.DBPOOL.runInteraction(self._writeback, res)
        d.addCallbacks(self._db_succeed, self._db_failed)
        d.addErrback(self._failed)

    def _ipmi_failed(self, err):
        """
        Get called when ipmitool failed.
        """

        self._status = 3
        sql = 'UPDATE ipmi_requesthost SET status = %s, end_time = %s, detail = %s WHERE id = %s'
        detail = '%s : %s' % (err.value.code, err.value.message)
        # ignore sql result
        db.DBPOOL.runOperation(sql, [self._status,
                                     datetime.datetime.now(),
                                     detail,
                                     self._hostrequest_id])

        return err

    # <<<=============== write back to database ================>>> #

    def _data_convertor(self, ipmi_info):
        """
        """

        return [[sel_id, sel_type, level, desc, json.dumps(info),
                 self._request_id, self._hostrequest_id]
                for sel_id, sel_type, level, desc, info in ipmi_info]

    def _writeback(self, transaction, ipmi_info):
        """
        write ipmitool's output to database

        :param transaction: adbapi.Transaction object
        :param ipmi_info:   data
        :returns:           the number of rows that the last
                            execute*() produced or affected
        """

        sql = 'INSERT INTO ipmi_info(sel_id, sel_type, sel_level, sel_desc, sel_info, request_id, host_id) VALUES (%s, %s, %s, %s, %s, %s, %s)'
        transaction.executemany(sql, self._data_convertor(ipmi_info))

        sql = 'UPDATE ipmi_requesthost SET status = %s, end_time = %s WHERE id = %s'
        transaction.execute(sql, [self._status,
                                  datetime.datetime.now(),
                                  self._hostrequest_id])

        return transaction.rowcount

    def _db_succeed(self, rowcount):
        """
        Get called when database update successful.
        """

        log.msg("INFO : %s rows affected." % rowcount, system=LOGTAG)
        if self.d is None:
            log.msg("WARNING : Nowhere to put results.", system=LOGTAG)
            return

        d = self.d
        self.d = None
        d.callback(self._hostrequest_id)

    def _db_failed(self, err):
        """
        Get called when database update failed.

        :param err: error
        """

        self._status = 3
        log.err(err)

        return err

    def _failed(self, err):
        """
        Get called whatever failed.

        :param err: error
        """

        if self.d is None:
            log.msg("WARNING : Nowhere to put results.", system=LOGTAG)
            return

        d = self.d
        self.d = None
        d.errback(err)

    def start(self):
        """
        entry point.

        returns: a deferred object
        """

        # validate host
        if self._status != 0:
            return defer.fail(exception.IllegalHostError())

        self._status = 1
        sql = 'UPDATE ipmi_requesthost SET status = %s, start_time = %s WHERE id = %s'
        # ignore sql result
        db.DBPOOL.runOperation(sql, [self._status,
                                     datetime.datetime.now(),
                                     self._hostrequest_id])

        d = self._manager.commit_job(self._ip_addr,
                                     self._username,
                                     self._password)

        d.addCallbacks(self._ipmi_succeed,
                       self._ipmi_failed)
        d.addErrback(self._failed)

        self.d = defer.Deferred()
        return self.d
