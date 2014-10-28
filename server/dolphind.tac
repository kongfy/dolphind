from twisted.web import xmlrpc, server
from twisted.application import service, internet
from common import config

import ipmihandler.manager

class RPC(xmlrpc.XMLRPC):
    """
    An example object to be published.
    """

    def __init__(self):
        "docstring"
        xmlrpc.XMLRPC.__init__(self)
        self._manager = ipmihandler.manager.Manager()

    def xmlrpc_simple(self, host="localhost", user="NULL", passwd="NULL"):
        """
        Return all passed args.
        """
        print host, user, passwd
        return self._manager.fetchIPMI(host, user, passwd)

CFG = config.Config()
port = int(CFG['server']['port'])
r = RPC()

application = service.Application("dolphind")
service = internet.TCPServer(port, server.Site(r))
service.setServiceParent(application)
