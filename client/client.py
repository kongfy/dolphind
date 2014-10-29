# -*- coding: utf-8 -*-

"""
This is the client program for dolphin, enjoy it.
"""

__authors__ = [
    '"Fanyu Kong" <me@kongfy.com>',
]

from twisted.web.xmlrpc import Proxy
from twisted.internet import reactor
from optparse import OptionParser

from common.config import CFG

def success_callback(value):
    """
    Callback method for rpc calls return successful.

    :param value: return value
    """

    print repr(value)
    reactor.stop()

def error_callback(error):
    """
    Callback method for rpc calls return an error.

    :param error: error from rpc
    """

    print repr(error)
    reactor.stop()

def main():
    """
    client script main method.
    """

    parser = OptionParser()
    parser.add_option("-H", "--host", dest="host", action="store",
                      default="127.0.0.1",
                      help="Remote server IPv4 address.",)

    parser.add_option("-U", "--user", dest="user", action="store",
                      default="NULL",
                      help="Remote server username, default is NULL user",)

    parser.add_option("-P", "--passwd", dest="passwd", action="store",
                      default="NULL",
                      help="Remote server password.",)
    options, _ = parser.parse_args()

    url = 'http://%s:%s' % (CFG['client']['server'], CFG['client']['port'])
    proxy = Proxy(url)
    proxy.callRemote('simple',
                     options.host,
                     options.user,
                     options.passwd).addCallbacks(success_callback, error_callback)

    reactor.run()

if __name__ == '__main__':
    main()
