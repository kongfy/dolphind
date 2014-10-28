from twisted.internet import defer
from twisted.python import log

from functools import partial
from collections import deque

from common import singleton
from common import utils
from common.config import CFG

from ipmihandler import excutor

LOGTAG = 'ipmihandler.manager'

@singleton.singleton
class Manager(object):
    def __init__(self):
        self._pending = deque()
        self._token = int(CFG['server']['max_concurrent'])

    def _excute(self):
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
        self._token += 1
        log.msg('Success : %s, token left : %d' % (success, self._token),
                system=LOGTAG)
        self._excute()
        return

    def _failed(self, d, err):
        d.errback(err)
        return False

    def _succeed(self, d, res):
        d.callback(res)
        return True

    def fetchIPMI(self, host, user, passwd):
        if not utils.is_valid_ip_address_v4(host):
            return defer.fail(ValueError("ERROR : Invalid IP address."))

        d = defer.Deferred()
        self._pending.append(((host, user, passwd), d))
        self._excute()
        return d
