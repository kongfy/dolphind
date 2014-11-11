# -*- coding: utf-8 -*-

"""
Request from dolphin web
"""

__authors__ = [
    '"Fanyu Kong" <me@kongfy.com>',
]

from twisted.python import log

from common import db
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

    # <<<=============== get request info ================>>>

    def _get_request(self):
        """
        Get request detail info from database
        :returns: a deferred object
        """
        d = db.DBPOOL.runQuery('SELECT * FROM ipmi_request WHERE id = ?',
                               self._request_id)
        d.addCallbacks(self._request_info,
                       self._request_error)
        return d


    def _request_info(self, info):
        """
        Callback for fetching request detail successfully.
        :param info: request detail from database
        """
        # TODO : validate info
        self._get_hosts()

    def _request_error(self, err):
        """
        faild when fetch request detail.
        :param err: error
        """
        # TODO : fill failed request to db
        pass

    # <<<=============== get request hosts ================>>> #

    def _get_hosts(self):
        """
        Get hosts annexed with the request
        returns: a deferred object
        """
        d = db.DBPOOL.runQuery('SELECT * FROM ipmi_requesthost WHERE request_id = ?',
                               self._request_id)
        d.addCallbacks(self._hosts_info,
                       self._hosts_error)
        return d

    def _hosts_info(self, info):
        """
        Callback for fetching hosts
        :param info: host detail to run ipmitool
        """
        count = 2 # TODO
        if count == 0:
            # success to database
            return

        for host in info:
            d = hostrequest.HostRequest(**host).start()
            d.addCallbacks(self._host_succeed,
                           self._host_failed)
            d.addCallback(self._host_done)


    def _hosts_error(self, err):
        """
        Failed when fetching hosts
        :param err: error
        """
        # TODO: fill database with error

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
        self._failed += 1

    def _host_done(self):
        """
        Called when a single host task done
        """
        if self._succeed + self._failed == self._count:
            # TODO: fill success to database
            return

    def start(self):
        """
        entry point.
        """
        self._get_request()
