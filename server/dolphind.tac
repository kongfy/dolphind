from twisted.web import xmlrpc, server
from twisted.internet import defer, utils
from twisted.application import service, internet


import gc
gc.enable()
gc.set_debug(gc.DEBUG_LEAK)

class Getter(object):
    def _toHTML(self, r):
        """
        This function converts r to HTML.

        It is added to the callback chain by getDummyData in
        order to demonstrate how a callback passes its own result
        to the next callback
        """
        out, err, signalNum = r
        return "Result: %s" % out

    def getDummyData(self, x):
        """
        The Deferred mechanism allows for chained callbacks.
        In this example, the output of gotResults is first
        passed through _toHTML on its way to printData.

        Again this function is a dummy, simulating a delayed result
        using callLater, rather than using a real asynchronous
        setup.
        """
        d = utils.getProcessOutputAndValue('/bin/sleep', args=(['10']))
        d.addCallback(self._toHTML)

        return d

from functools import partial
from collections import deque

class Manager(object):
    def __init__(self, max):
        "docstring"

        self._pending = deque()
        self._token = max

    def _excute(self):
        if self._token <= 0 or len(self._pending) == 0:
            return

        self._token -= 1

        x, d = self._pending.popleft()
        callback = partial(self._finish, d)

        print "excute command, token left : %d" % self._token
        excutor = Getter()
        d = excutor.getDummyData(x)
        d.addCallback(callback)

    def _finish(self, d, r):
        d.callback(r)

        self._token += 1
        self._excute()
        print "finish token %d" % self._token

    def fetchIPMI(self, x):
        d = defer.Deferred()
        self._pending.append((x, d))
        self._excute()
        return d


class Example(xmlrpc.XMLRPC):
    """
    An example object to be published.
    """

    def __init__(self):
        "docstring"
        xmlrpc.XMLRPC.__init__(self)
        self._manager = Manager(2)

    def xmlrpc_echo(self, x):
        """
        Return all passed args.
        """
        return self._manager.fetchIPMI(x)

    def xmlrpc_add(self, a, b):
        """
        Return sum of arguments.
        """
        return a + b

    def xmlrpc_fault(self):
        """
        Raise a Fault indicating that the procedure should not be used.
        """
        raise xmlrpc.Fault(123, "The fault procedure is faulty.")

r = Example()

application = service.Application("dolphind")
service = internet.TCPServer(7080, server.Site(r))
service.setServiceParent(application)

gc.collect()
print "gc.garbage:", len(gc.garbage)

for item in gc.garbage:
    print item
