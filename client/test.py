# -*- coding: utf-8 -*-

"""
Test script for dolphind web interface,
Just simulate the function call.
"""

__authors__ = [
    '"Fanyu Kong" <me@kongfy.com>',
]

from twisted.web.xmlrpc import Proxy
from twisted.internet import reactor

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

    print error
    reactor.stop()

def main():
    """
    script main function
    """
    url = 'http://%s:%s' % (CFG['client']['server'], CFG['client']['port'])
    proxy = Proxy(url)
    proxy.callRemote('request',
                     1,
                     'http://127.0.0.1/dolphin/callback').addCallbacks(success_callback, error_callback)

    reactor.run()

if __name__ == '__main__':
    main()
