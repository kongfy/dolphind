# -*- coding: utf-8 -*-

"""
Interpreter for ipmitool's output.
To use this module, please ensure your ipmitool command is running with argument '-vv'
"""

__authors__ = [
    '"Fanyu Kong" <me@kongfy.com>',
]

import itertools

Dispatch_table = {}

def _description(out):
    """
    decode SEL description from output string.

    :param out: string from standard output
    :yeild:     description dictionary
    """

    desc = {}
    flag = False
    for line in out.splitlines():
        if 'SEL Record ID' in line:
            flag = True
            desc = {}

        if len(line) == 0:
            if flag:
                flag = False
                yield desc

        if flag:
            key, sep, value = line.partition(':')
            desc[key.rstrip()] = value.lstrip()

def _entry(err):
    """
    decode SEL raw entry from error string.

    :param err: string from standard error
    :yeild:     raw entry string
    """

    for line in err.splitlines():
        if 'SEL Entry' in line:
            yield line.split(':')[1].lstrip()

def _dispatch(desc, entry):
    """
    dispatch the SEL entry to an interpreter.

    :param desc:  dictionary for SEL description
    :param entry: raw entry for SEL description
    :returns:     (information, level) for given SEL entry
    """

    return (desc, 'ERROR')

def interpret(out, err):
    """
    interpret ipmitool's output

    :param out: string from standard output
    :param err: string from standard error
    :returns:   list of interpreted infomation
    """

    ans = []
    for desc, entry in itertools.izip(_description(out), _entry(err)):
        ans.append(_dispatch(desc, entry))

    return ans

if __name__ == '__main__':
    # unit test
    print interpret('<<OPEN SESSION RESPONSE\n<<  Message tag                        : 0x00\n<<  RMCP+ status                       : no errors\n<<  Maximum privilege level            : admin\n<<  Console Session ID                 : 0xa0a2a3a4\n<<  BMC Session ID                     : 0x0200ac00\n<<  Negotiated authenticatin algorithm : hmac_sha1\n<<  Negotiated integrity algorithm     : hmac_sha1_96\n<<  Negotiated encryption algorithm    : aes_cbc_128\n\n<<RAKP 2 MESSAGE\n<<  Message tag                   : 0x00\n<<  RMCP+ status                  : no errors\n<<  Console Session ID            : 0xa0a2a3a4\n<<  BMC random number             : 0xbc85ebd8a092a8b0ac6b48da4f272569\n<<  BMC GUID                      : 0x44454c4c530010398032c8c04f313332\n<<  Key exchange auth code [sha1] : 0x7473f68c342c9d0d052e429a8ffba517152b51c2\n\n<<RAKP 4 MESSAGE\n<<  Message tag                   : 0x00\n<<  RMCP+ status                  : no errors\n<<  Console Session ID            : 0xa0a2a3a4\n<<  Key exchange auth code [sha1] : 0x3313799a7f2ead1725e7210c\n\nSEL Record ID          : 0001\n Record Type           : 02\n Timestamp             : 09/25/2014 17:41:28\n Generator ID          : 0020\n EvM Revision          : 04\n Sensor Type           : Event Logging Disabled\n Sensor Number         : 72\n Event Type            : Sensor-specific Discrete\n Event Direction       : Assertion Event\n Event Data            : 02ffff\n Description           : Log area reset/cleared\n\nSEL Record ID          : 0002\n Record Type           : 02\n Timestamp             : 10/10/2014 15:10:27\n Generator ID          : 0020\n EvM Revision          : 04\n Sensor Type           : Physical Security\n Sensor Number         : 73\n Event Type            : Sensor-specific Discrete\n Event Direction       : Assertion Event\n Event Data            : 8002ff\n Description           : General Chassis intrusion\n\nSEL Record ID          : 0003\n Record Type           : 02\n Timestamp             : 10/10/2014 15:10:33\n Generator ID          : 0020\n EvM Revision          : 04\n Sensor Type           : Physical Security\n Sensor Number         : 73\n Event Type            : Sensor-specific Discrete\n Event Direction       : Deassertion Event\n Event Data            : 8002ff\n Description           : General Chassis intrusion\n\n', 'IPMI LAN host 192.168.0.120 port 623\r\n\r\n>> Sending IPMI command payload\r\n>>    netfn   : 0x0ªªª6\r\n>>    command : 0x38\r\n>>    data    : 0x8e 0x04 \n\n>> SxENDING AN OPEN SESSION REQUEST\n\r\n>> Console generated random number (16 bytes)\r\n 0e b1 89 b4 bc af 69 f1 ec dc 81 04 6d d0 67 9b\r\n>> SENDING A RAKP 1 MESSAGE\n\r\nsession integrity key input (38 bytes)\r\n 0e b1 89 b4 bc af 69 f1 ec dc 81 04 6d d0 67 9b\r\n bc 85 eb d8 a0 92 a8 b0 ac 6b 48 da 4f 27 25 69\r\n 14 04 72 6f 6f 74\r\nGenerated session integrity key (20 bytes)\r\n 8c a1 a9 ac 02 55 fb be 9c eb ba 57 57 2b ef e6\r\n 7f 89 68 51\r\nGenerated K1 (20 bytes)\r\n a7 bb 21 94 7a d2 ea 67 01 c8 f3 7e 98 03 45 bf\r\n 25 83 93 78\r\nGenerated K2 (20 bytes)\r\n 50 af e9 bc 45 af 89 fc 26 57 32 45 de 37 33 15\r\n 52 4d 1a 8e\r\n>> SENDING A RAKP 3 MESSAGE\n\r\nIPMIv2 / RMCP+ SESSION OPENED SUCCESSFULLY\n\r\n\r\n>> Sending IPMI command payload\r\n>>    netfn   : 0x06\r\n>>    command : 0x3b\r\n>>    data    : 0x04 \n\nSet Session Privilege Level to ADMINISTRATOR\n\r\n\r\n>> Sending IPMI command payload\r\n>>    netfn   : 0x0a\r\n>>    command : 0x40\r\n>>    data    : \n\n\r\n>> Sending IPMI command payload\r\n>>    netfn   : 0x0a\r\n>>    command : 0x42\r\n>>    data    : \n\nSEL Next ID: 0000\r\n\r\n>> Sending IPMI command payload\r\n>>    netfn   : 0x0a\r\n>>    command : 0x43\r\n>>    data    : 0x00 0x00 0x00 0x00 0x00 0xff \n\nSEL Entry: 010002c853245420000410726f02ffff\r\nSEL Next ID: 0002\r\n\r\n>> Sending IPMI command payload\r\n>>    netfn   : 0x0a\r\n>>    command : 0x43\r\n>>    data    : 0x00 0x00 0x02 0x00 0x00 0xff \n\nSEL Entry: 020002e3f6375420000405736f8002ff\r\nSEL Next ID: 0003\r\n\r\n>> Sending IPMI command payload\r\n>>    netfn   : 0x0a\r\n>>    command : 0x43\r\n>>    data    : 0x00 0x00 0x03 0x00 0x00 0xff \n\nSEL Entry: 030002e9f637542000040573ef8002ff\r\n\r\n>> Sending IPMI command payload\r\n>>    netfn   : 0x06\r\n>>    command : 0x3c\r\n>>    data    : 0x00 0xac 0x00 0x02 \n\nClosed Session 0200ac00\n\r\n')
