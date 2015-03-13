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
import interpreter

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

    cmd = 'sleep 0.07'
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
        :raises:       exception.IPMIToolError
        """

        out, err, code = result
        if code != 0:
            raise exception.IPMIToolError()

        out = '<<OPEN SESSION RESPONSE\n<<  Message tag                        : 0x00\n<<  RMCP+ status                       : no errors\n<<  Maximum privilege level            : admin\n<<  Console Session ID                 : 0xa0a2a3a4\n<<  BMC Session ID                     : 0x0200ac00\n<<  Negotiated authenticatin algorithm : hmac_sha1\n<<  Negotiated integrity algorithm     : hmac_sha1_96\n<<  Negotiated encryption algorithm    : aes_cbc_128\n\n<<RAKP 2 MESSAGE\n<<  Message tag                   : 0x00\n<<  RMCP+ status                  : no errors\n<<  Console Session ID            : 0xa0a2a3a4\n<<  BMC random number             : 0xbc85ebd8a092a8b0ac6b48da4f272569\n<<  BMC GUID                      : 0x44454c4c530010398032c8c04f313332\n<<  Key exchange auth code [sha1] : 0x7473f68c342c9d0d052e429a8ffba517152b51c2\n\n<<RAKP 4 MESSAGE\n<<  Message tag                   : 0x00\n<<  RMCP+ status                  : no errors\n<<  Console Session ID            : 0xa0a2a3a4\n<<  Key exchange auth code [sha1] : 0x3313799a7f2ead1725e7210c\n\nSEL Record ID          : 0001\n Record Type           : 02\n Timestamp             : 09/25/2014 17:41:28\n Generator ID          : 0020\n EvM Revision          : 04\n Sensor Type           : Event Logging Disabled\n Sensor Number         : 72\n Event Type            : Sensor-specific Discrete\n Event Direction       : Assertion Event\n Event Data            : 02ffff\n Description           : Log area reset/cleared\n\nSEL Record ID          : 0002\n Record Type           : 02\n Timestamp             : 10/10/2014 15:10:27\n Generator ID          : 0020\n EvM Revision          : 04\n Sensor Type           : Physical Security\n Sensor Number         : 73\n Event Type            : Sensor-specific Discrete\n Event Direction       : Assertion Event\n Event Data            : 8002ff\n Description           : General Chassis intrusion\n\nSEL Record ID          : 0003\n Record Type           : 02\n Timestamp             : 10/10/2014 15:10:33\n Generator ID          : 0020\n EvM Revision          : 04\n Sensor Type           : Physical Security\n Sensor Number         : 73\n Event Type            : Sensor-specific Discrete\n Event Direction       : Deassertion Event\n Event Data            : 8002ff\n Description           : General Chassis intrusion\n\n'


        err = 'IPMI LAN host 192.168.0.120 port 623\r\n\r\n>> Sending IPMI command payload\r\n>>    netfn   : 0x0ªªª6\r\n>>    command : 0x38\r\n>>    data    : 0x8e 0x04 \n\n>> SxENDING AN OPEN SESSION REQUEST\n\r\n>> Console generated random number (16 bytes)\r\n 0e b1 89 b4 bc af 69 f1 ec dc 81 04 6d d0 67 9b\r\n>> SENDING A RAKP 1 MESSAGE\n\r\nsession integrity key input (38 bytes)\r\n 0e b1 89 b4 bc af 69 f1 ec dc 81 04 6d d0 67 9b\r\n bc 85 eb d8 a0 92 a8 b0 ac 6b 48 da 4f 27 25 69\r\n 14 04 72 6f 6f 74\r\nGenerated session integrity key (20 bytes)\r\n 8c a1 a9 ac 02 55 fb be 9c eb ba 57 57 2b ef e6\r\n 7f 89 68 51\r\nGenerated K1 (20 bytes)\r\n a7 bb 21 94 7a d2 ea 67 01 c8 f3 7e 98 03 45 bf\r\n 25 83 93 78\r\nGenerated K2 (20 bytes)\r\n 50 af e9 bc 45 af 89 fc 26 57 32 45 de 37 33 15\r\n 52 4d 1a 8e\r\n>> SENDING A RAKP 3 MESSAGE\n\r\nIPMIv2 / RMCP+ SESSION OPENED SUCCESSFULLY\n\r\n\r\n>> Sending IPMI command payload\r\n>>    netfn   : 0x06\r\n>>    command : 0x3b\r\n>>    data    : 0x04 \n\nSet Session Privilege Level to ADMINISTRATOR\n\r\n\r\n>> Sending IPMI command payload\r\n>>    netfn   : 0x0a\r\n>>    command : 0x40\r\n>>    data    : \n\n\r\n>> Sending IPMI command payload\r\n>>    netfn   : 0x0a\r\n>>    command : 0x42\r\n>>    data    : \n\nSEL Next ID: 0000\r\n\r\n>> Sending IPMI command payload\r\n>>    netfn   : 0x0a\r\n>>    command : 0x43\r\n>>    data    : 0x00 0x00 0x00 0x00 0x00 0xff \n\nSEL Entry: 010002c853245420000410726f02ffff\r\nSEL Next ID: 0002\r\n\r\n>> Sending IPMI command payload\r\n>>    netfn   : 0x0a\r\n>>    command : 0x43\r\n>>    data    : 0x00 0x00 0x02 0x00 0x00 0xff \n\nSEL Entry: 020002e3f6375420000405736f8002ff\r\nSEL Next ID: 0003\r\n\r\n>> Sending IPMI command payload\r\n>>    netfn   : 0x0a\r\n>>    command : 0x43\r\n>>    data    : 0x00 0x00 0x03 0x00 0x00 0xff \n\nSEL Entry: 030002e9f637542000040573ef8002ff\r\n\r\n>> Sending IPMI command payload\r\n>>    netfn   : 0x06\r\n>>    command : 0x3c\r\n>>    data    : 0x00 0xac 0x00 0x02 \n\nClosed Session 0200ac00\n\r\n'

        return (out, err)

    def _explain(self, result):
        """
        Explain the output.

        :param result: out, err given by _on_exit()
        """

        if self.d is None:
            log.msg("WARNING : Nowhere to put results.", system=LOGTAG)
            return

        d = self.d
        self.d = None

        out, err = result
        try:
            ans = interpreter.interpret(out, err)
            d.callback(ans)
        except (Exception), e:
            log.msg('ERROR : %s' % e, system=LOGTAG)
            self._failed(exception.InterpretError())

    def _failed(self, err):
        """
        Faild.

        :param err: error...
        """

        if self.d is None:
            log.msg('WARNING : Nowhere to put results.', system=LOGTAG)
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
