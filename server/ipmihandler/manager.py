# -*- coding: utf-8 -*-

"""
Management for all the ipmitool command.
"""

__authors__ = [
    '"Fanyu Kong" <me@kongfy.com>',
]

from twisted.internet import defer
from twisted.python import log

from functools import partial
from collections import deque

from common import singleton
from common import utils
from common import exception
from common.config import CFG
from ipmihandler import excutor

LOGTAG = __name__

@singleton.singleton
class Manager(object):
    """
    Manager class handles all the ipmi request.
    """

    def __init__(self):
        # queue for pending ipmi task
        self._pending = deque()
        # how many tack can be run concurrently
        self._token = int(CFG['server']['max_concurrent'])

    def _excute(self):
        """
        Run an pending task if you can.
        """

        if self._token <= 0 or len(self._pending) == 0:
            return

        self._token -= 1

        info, d = self._pending.popleft()
        callback = partial(self._succeed, d)
        errback = partial(self._failed, d)

        log.msg('Excute command, token left : %d' % self._token, system=LOGTAG)
        worker = excutor.Excutor(*info)
        d = worker.start()
        d.addCallbacks(callback, errback)
        d.addCallback(self._release)

    def _release(self, success):
        """
        When a work done, release it's token.

        :param success: if the work succeeded
        """

        self._token += 1
        log.msg('Success : %s, token left : %d' % (success, self._token),
                system=LOGTAG)
        self._excute()
        return

    def _failed(self, d, err):
        """
        Errback method for excutor(worker).

        :param d:   the deferred object should be called
        :param err: error during excutor's routine
        """

        d.errback(err)
        return False

    def _succeed(self, d, res):
        """
        Callback method for excutor(worker).

        :param d:   the deferred object should be called
        :param res: output of ipmitool
        """

        d.callback(res)
        return True

    def commit_job(self, host, user, passwd):
        """
        Add an ipmi job to manager

        :param host:   ipmi target's IPv4 address
        :param user:   ipmi username
        :param passwd: ipmi password
        :returns:      a deferred object
        """

        if not utils.is_valid_ip_address_v4(host):
            return defer.fail(exception.InvalidIPAddr())

        d = defer.Deferred()
        self._pending.append(((host, user, passwd), d))
        self._excute()
        return d
