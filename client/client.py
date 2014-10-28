from twisted.web.xmlrpc import Proxy
from twisted.internet import reactor

def printValue(value):
    print repr(value)
    reactor.stop()

def printError(error):
    print 'error', error
    reactor.stop()

def main():
    proxy = Proxy('http://localhost:7080')
    proxy.callRemote('echo', 3).addCallbacks(printValue, printError)
    print 'remote call return'
    reactor.run()

if __name__ == '__main__':
    main()
