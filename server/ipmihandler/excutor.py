from twisted.internet import utils
from twisted.python import log

LOGTAG = 'ipmihandler.excutor'

class Getter(object):
    def _toHTML(self, r):
        """
        """
        out, err, signalNum = r
        return "Result: %s" % out

    def getIPMI(self, host, user, passwd):
        """
        """
        cmd = '/bin/sleep'
        log.msg('CMD : %s' % cmd, system=LOGTAG)
        d = utils.getProcessOutputAndValue('/bin/sleep', args=(['10']))
        d.addCallback(self._toHTML)

        return d
