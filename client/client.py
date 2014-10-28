from twisted.web.xmlrpc import Proxy
from twisted.internet import reactor
from optparse import OptionParser

from common import config

def printValue(value):
    print repr(value)
    reactor.stop()

def printError(error):
    print 'error', error
    reactor.stop()

def main():
    parser = OptionParser()
    parser.add_option("-H", "--host", dest="host", action="store",
                      default="localhost",
                      help="Remote server address, can be IP address or hostname.",)

    parser.add_option("-U", "--user", dest="user", action="store",
                      default="NULL",
                      help="Remote server username, default is NULL user",)

    parser.add_option("-P", "--passwd", dest="passwd", action="store",
                      default="NULL",
                      help="Remote server password.",)
    options, _ = parser.parse_args()

    cfg = config.Config()
    url = 'http://%s:%s' % (cfg['client']['server'], cfg['client']['port'])
    proxy = Proxy(url)
    proxy.callRemote('simple',
                     options.host,
                     options.user,
                     options.passwd).addCallbacks(printValue, printError)

    reactor.run()

if __name__ == '__main__':
    main()
