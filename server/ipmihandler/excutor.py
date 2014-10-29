from twisted.internet import utils, defer, reactor
from twisted.python import log

from common.config import CFG

LOGTAG = 'ipmihandler.excutor'
FORMAT = 'ipmitool -I lanplus -H %s -U %s -P %s sel list -vv'

def command(host, user, passwd):
    cmd = FORMAT % (host, user, passwd)
    log.msg('CMD : %s' % cmd, system=LOGTAG)
    tmp = cmd.split()
    return tmp[0], tmp[1:]

class Excutor(object):
    def __init__(self, host, user, passwd):
        "docstring"
        self._retry_count = int(CFG['server']['max_retry'])
        self._retry_interval = int(CFG['server']['retry_interval'])
        self._host = host
        self._user = user
        self._passwd = passwd

    def _on_exit(self, result):
        out, err, code = result
        if code != 0:
            raise ValueError('ipmitool exit with code %s' % code)
        return out

    def _explain(self, result):
        """
        """
        if self.d is None:
            log.msg("WARNING : Nowhere to put results.", system=LOGTAG)
            return

        d = self.d
        self.d = None
        d.callback(result)

    def _failed(self, err):
        if self.d is None:
            log.msg("WARNING : Nowhere to put results.", system=LOGTAG)
            return

        d = self.d
        self.d = None
        d.errback(err)

    def _retry_with_delay(self, err):
        """
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
        self._retry(None)

        self.d = defer.Deferred()
        return self.d
