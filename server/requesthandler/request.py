# -*- coding: utf-8 -*-

"""
Request from dolphin web
"""

__authors__ = [
    '"Fanyu Kong" <me@kongfy.com>',
]

from twisted.python import log
from twisted.web import client

import datetime

from common import db
from common import exception
from requesthandler import hostrequest

LOGTAG = __name__

class Request(object):
    """
    Request form dolphin web
    """

    def __init__(self, request_id, callback):
        self._request_id = request_id
        self._callback = callback
        self._count = 0    # total number of hosts annexed to this request
        self._succeed = 0  # total number of success host currently
        self._failed = 0   # total number of failed host currently
        self._status = 0   # initialize status, 0-ready 1-running 2-finish 3-failed

    # <<<=============== get request info ================>>>

    def _get_request(self):
        """
        Get request detail info from database
        :returns: a deferred object
        """

        sql = 'SELECT * FROM ipmi_request WHERE id = %s'
        d = db.DBPOOL.runQuery(sql, [self._request_id])
        d.addCallbacks(self._request_info,
                       self._request_error)
        d.addErrback(self._abort)
        return d


    def _request_info(self, info):
        """
        Callback for fetching request detail successfully.
        :param info: request detail from database
                     example:
                     ((1L, datetime.datetime(2009, 6, 9, 0, 24, 8), datetime.datetime(2009, 6, 9, 0, 24, 8), 1, 'No detail'),)
        """

        if len(info) != 1:
            raise exception.RequestError()

        # validate request
        (rid, start_time, end_time, status, detail), = info
        if status != 0:
            raise exception.RequestError()

        self._get_hosts()

    def _request_error(self, err):
        """
        faild when fetch request detail.
        :param err: error
        """

        log.msg("ERROR : Fetching request detail faild, request_id : %s" % self._request_id,
                system=LOGTAG)
        raise exception.RequestError()

    # <<<=============== get request hosts ================>>> #

    def _get_hosts(self):
        """
        Get hosts annexed with the request
        returns: a deferred object
        """

        sql = 'SELECT * FROM ipmi_requesthost WHERE request_id = %s'
        d = db.DBPOOL.runQuery(sql, [self._request_id])
        d.addCallbacks(self._hosts_info,
                       self._hosts_error)
        d.addErrback(self._abort)
        return d

    def _hosts_info(self, info):
        """
        Callback for fetching hosts
        :param info: host detail to run ipmitool
                     example:
                     ((2L, '192.168.0.120', 'root', 'MhxzKhl', datetime.datetime(2014, 11, 10, 0, 0), None, 0, '', 1L), ...)
        """

        self._count = len(info)
        if self._count == 0:
            raise exception.HostsNotFoundError()

        for host in info:
            d = hostrequest.HostRequest(*host).start()
            d.addCallbacks(self._host_succeed,
                           self._host_failed)
            d.addCallback(self._host_done)

        self._status = 1  # running
        self._update_db('%s targets found' % self._count)


    def _hosts_error(self, err):
        """
        Failed when fetching hosts
        :param err: error
        """

        log.msg("ERROR : Fetching hosts info faild, request_id : %s"
                % self._request_id,
                system=LOGTAG)

        raise exception.HostsError()

    # <<<=============== callbacks for a single host ================>>> #

    def _host_succeed(self):
        """
        Call back for a single host ipmitool
        """

        self._succeed += 1

    def _host_failed(self, err):
        """
        Call back for a single host ipmitool
        :param err: error
        """

        log.msg("ERROR : host faild in request %s : ERROR %s: %s"
                % (self._request_id, err.value.code, err.value.message),
                system=LOGTAG)

        self._failed += 1

    def _host_done(self, *args):
        """
        Called when a single host task done
        """

        if self._succeed + self._failed == self._count:
            self._status = 2
            self._update_db('%s/%s succeed' % (self._succeed, self._failed))

    def _abort(self, err):
        """
        Called when task can not be processed anymore.
        """

        self._status = 3   # failed
        self._update_db('%s : %s' % (err.value.code, err.value.message))

    # <<<=============== update status to database ================>>> #

    def _update_db(self, info):
        """
        update status

        :param info: detail string
        :returns: a deferred object
        """

        if self._status == 1:
            # running
            sql = 'UPDATE ipmi_request SET status = %s, detail = %s WHERE id = %s'
            args = [self._status, info, self._request_id]
        else:
            # finsih or faild
            sql = 'UPDATE ipmi_request SET status = %s, end_time = %s, detail = %s WHERE id = %s'
            args = [self._status, datetime.datetime.now(),
                    info, self._request_id]

        d = db.DBPOOL.runOperation(sql, args)
        d.addCallbacks(self._update_db_finish, self._update_db_failed)
        d.addCallback(self._notify)

        return d

    def _update_db_finish(self, rows):
        """
        get called when successful update database.
        do nothing now.
        """

    def _update_db_failed(self, err):
        """
        get called when failed to update database.
        do nothing but log it.
        """

        log.msg("ERROR : Update status to database failed, request_id : %s"
                % self._request_id,
                system=LOGTAG)

    # <<<=============== callback for dolphin web ================>>> #

    def _notify(self, *ignored):
        """
        Call dolphin web hook
        Seemingly, this method need not to retry, am I right?
        """

        url = self._callback + '?id=%s&status=%s' % (self._request_id, self._status)
        client.getPage(url)

    def start(self):
        """
        entry point.
        """

        self._get_request()
