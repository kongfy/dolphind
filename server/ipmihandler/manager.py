from twisted.internet import defer
from twisted.python import log

from functools import partial
from collections import deque

from common import singleton
from common import config
from ipmihandler import excutor

LOGTAG = 'ipmihandler.manager'

@singleton.singleton
class Manager(object):
    def __init__(self):
        self._pending = deque()
        self._token = int(config.Config()['server']['max_concurrent'])

    def _excute(self):
        if self._token <= 0 or len(self._pending) == 0:
            return

        self._token -= 1

        info, d = self._pending.popleft()
        callback = partial(self._finish, d)

        log.msg('Excute command, token left : %d' % self._token, system=LOGTAG)
        worker = excutor.Getter()
        d = worker.getIPMI(*info)
        d.addCallback(callback)

    def _finish(self, d, r):
        d.callback(r)

        self._token += 1
        log.msg('Finished, token left : %d' % self._token, system=LOGTAG)
        self._excute()

    def fetchIPMI(self, host, user, passwd):
        d = defer.Deferred()
        self._pending.append(((host, user, passwd), d))
        self._excute()
        return d
