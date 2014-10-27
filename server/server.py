from twisted.web import xmlrpc, server
from twisted.internet import reactor, defer, utils

import gc
gc.enable()
gc.set_debug(gc.DEBUG_LEAK)

class Getter(object):
    def __init__(self, id):
        "docstring"

        self._id = id

    def _toHTML(self, r):
        """
        This function converts r to HTML.

        It is added to the callback chain by getDummyData in
        order to demonstrate how a callback passes its own result
        to the next callback
        """
        out, err, signalNum = r
        return "Result: %s" % out

    def _finish(self, r):
        return (self._id, r)

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
        d.addCallback(self._finish)

        return d

class Manager(object):
    def __init__(self, max):
        "docstring"

        self._working = {};
        self._pending = [];
        self._token = max;
        self._id = 0;

    def _excute(self):
        if self._token <= 0 or len(self._pending) == 0:
            return

        self._token -= 1
        id = self._id
        self._id = self._id + 1

        x, d = self._pending.pop()
        self._working[id] = (x, d)

        print "excute id %s token %d" % (id, self._token)
        excutor = Getter(id)
        d = excutor.getDummyData(x)
        d.addCallback(self._finish)

    def _finish(self, r):
        id, r = r
        _, d = self._working.pop(id)
        d.callback(r)

        self._token += 1
        self._excute()
        print "finish token %d" % self._token

    def fetchIPMI(self, x):
        d = defer.Deferred()
        self._pending.insert(0, (x, d))
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

if __name__ == '__main__':
    r = Example()
    reactor.listenTCP(7080, server.Site(r))
    reactor.run()

    gc.collect()
    print "gc.garbage:", len(gc.garbage)

    for item in gc.garbage:
        print item
