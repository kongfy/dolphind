# -*- coding: utf-8 -*-

"""
This is the dolphind server program.
Powered by Twisted framework, you can run dolphind as follow:

# twistd -y dolphind.tac
"""

__authors__ = [
    '"Fanyu Kong" <me@kongfy.com>',
]


from twisted.web import xmlrpc, server
from twisted.application import service, internet
from common.config import CFG

import ipmihandler.manager

class RPC(xmlrpc.XMLRPC):
    """
    dolpind provide service by XML-RPC,
    this is dolphind's service class.
    """

    def __init__(self):
        xmlrpc.XMLRPC.__init__(self)
        self._manager = ipmihandler.manager.Manager()

    def xmlrpc_simple(self, host="127.0.0.1", user="NULL", passwd="NULL"):
        """
        simple rpc interface for dolphind's client.
        run an simple ipmitool command only.

        :param host:   ipmi target's IPv4 address
        :param user:   ipmi username
        :param passwd: ipmi password
        :returns:      a deferred object
        """

        print host, user, passwd
        return self._manager.commit_job(host, user, passwd)

port = int(CFG['server']['port'])
r = RPC()

application = service.Application("dolphind")
service = internet.TCPServer(port, server.Site(r))
service.setServiceParent(application)
