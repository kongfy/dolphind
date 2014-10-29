# -*- coding: utf-8 -*-

"""
Real worker for ipmitool
"""

__authors__ = [
    '"Fanyu Kong" <me@kongfy.com>',
]

from twisted.internet import utils, defer, reactor
from twisted.python import log

from common.config import CFG
from common import exception

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
    log.msg('CMD : %s' % cmd, system=LOGTAG)
    tmp = cmd.split()
    return tmp[0], tmp[1:]

class Excutor(object):
    """
    Worker for ipmitool, one instance only handle one ipmitool task.
    """

    def __init__(self, host, user, passwd):
        self._retry_count = int(CFG['server']['max_retry'])
        self._retry_interval = int(CFG['server']['retry_interval'])
        self._host = host
        self._user = user
        self._passwd = passwd
        self.d = None

    def _on_exit(self, result):
        """
        Get called when subprocess exit.

        :param result: (out, err, code) by Twisted
        :returns:      output text combined with stdout & stderr
        :raises:       ValueError
        """

        out, err, code = result
        if code != 0:
            raise exception.RuntimeError()
        return out

    def _explain(self, result):
        """
        Explain the output.

        :param result: output given by _on_exit()
        """
        if self.d is None:
            log.msg("WARNING : Nowhere to put results.", system=LOGTAG)
            return

        d = self.d
        self.d = None
        d.callback(result)

    def _failed(self, err):
        """
        Faild.

        :param err: error...
        """
        if self.d is None:
            log.msg("WARNING : Nowhere to put results.", system=LOGTAG)
            return

        d = self.d
        self.d = None
        d.errback(err)

    def _retry_with_delay(self, err):
        """
        Retry this task after `interval` seconds.

        :param err: error...
        """
        if self._retry_count == 0:
            log.msg('Abort, retry times out.', system=LOGTAG)
            self._failed(err)
            return

        log.msg('Failed, will retry in %s seconds.' % self._retry_interval,
                system=LOGTAG)
        reactor.callLater(self._retry_interval, self._retry, err)

    def _retry(self, err):
        """
        Retry this task.

        :param err: error...
        """
        log.msg("Excutor's retry count down : %s." % self._retry_count,
                system=LOGTAG)

        self._retry_count -= 1
        d = utils.getProcessOutputAndValue(*command(self._host,
                                                    self._user,
                                                    self._passwd))
        d.addCallback(self._on_exit)
        d.addCallbacks(self._explain, self._retry_with_delay)

    def start(self):
        """
        Get to work now!
        """

        self._retry(None)

        self.d = defer.Deferred()
        return self.d
