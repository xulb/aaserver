import asyncio
import collections
import re
from argparse import ArgumentParser

class RconCommand():
    """Class to convert an rcon command and password to QuakeII protocol
    bytestring

    >>> a=rcon.RconCommand('set foo 1','s3ckr1t')
    >>> a.bytestr
    b'\xff\xff\xff\xff rcon "s3ckr1t" set foo 1\x00'
    """
    pfx = b'\xFF\xFF\xFF\xFF rcon '
    def __init__(self, cmd, passwd):
        if passwd and cmd:
            self.bytestr = RconCommand.pfx+b'"'+passwd.encode('ascii')+ \
                           b'" '+cmd.encode('ascii')+b'\x00'
        else:
            raise RuntimeError("cmd and passwd string args required")

class RconCommandFactory():
    """Wrap RconCommand objects

    >>> f=rcon.RconCommandFactory('s3ckr1t')
    >>> f.cmd('set foo 1')
    b'\xff\xff\xff\xff rcon "s3ckr1t" set foo 1\x00'
    >>> type(f.lastCommand)
    <class 'rcon.RconCommand'>
    >>> f.lastCommand.bytestr
    b'\xff\xff\xff\xff rcon "s3ckr1t" set foo 1\x00'
    """
    def __init__(self, passwd):
        if passwd:
            self._passwd = passwd
        else:
            raise RuntimeError("passwd string arg required")
    def cmd(self, cmd):
        if cmd:
            self.lastCommand = RconCommand(cmd, self._passwd)
            return self.lastCommand.bytestr
        else:
            raise RuntimeError("cmd string arg required")

class RconClientProtocol(asyncio.Protocol):
    """asyncio Protocol object for UDP communication with QuakeII server
    """
    WAIT = 0.100
    TIMEOUT = 15
    def __init__(self, loop, address, passwd,log=None):
        self.loop = loop
        self.address = address
        self._passwd = passwd
        self.log = log
        self.transport = None
        # TODO: use an asyncio.Queue here instead
        self.data = collections.deque()
        self.cmdf = RconCommandFactory(self._passwd)

    def do_rcon_cmd(self, cmd):
#        future = asyncio.Future()
        self.loop.run_until_complete(self.send_cmd(cmd))
        future = asyncio.async(self.wait_for_response())
        self.loop.run_until_complete(future)
        ret = ''
        if future.result():
            for bstring in future.result():
                ret += bstring.decode('ascii')
        return ret

    @asyncio.coroutine
    def send_cmd(self, cmd):
#        print("in send_cmd")
        if not self.transport:
            self.log and self.log.critical("send_cmd: no connection (%s:%s)",address)
            raise RuntimeError("transport not defined (no connection?)")
        self.transport.sendto(self.cmdf.cmd(cmd))

    @asyncio.coroutine
    def get_response(self):
#        print("in get_response")
        while not len(self.data):
            yield from asyncio.sleep(RconClientProtocol.WAIT)
        # TODO use asyncio.Queue
        d = []
        d.extend(self.data)
        self.data.clear()
        return d

    @asyncio.coroutine
    def wait_for_response(self,future=None):
        data = yield from asyncio.wait_for(self.get_response(),
                                           RconClientProtocol.TIMEOUT,
                                           loop=self.loop)
#        future.set_result(data)
        return data

        
    
    @asyncio.coroutine
    def _endpt(self):
        connect = self.loop.create_datagram_endpoint(
            lambda: self,
            remote_addr=self.address
        )
        transport,protocol = yield from asyncio.wait_for(connect,RconClientProtocol.TIMEOUT,loop=self.loop)
        1

    def connect(self):
        self.loop.run_until_complete(self._endpt())

    def connection_made(self, transport):
#        print("in connection_made")
        self.transport = transport

    def datagram_received(self, data, addr):
#        print("in datagram_received")
        if not re.match(b'^\xFF\xFF\xFF\xFF',data):
            self.log and self.log.critical("Non-Q2 datagram received")
            raise RuntimeError("Non-Q2 datagram received")
        data = re.sub(b'^\xFF\xFF\xFF\xFF',b'',data)
        data = re.sub(b'^\s*print\s*',b'',data)
        if not data:
            data = b'ACK'
        self.data.appendleft(data);

    def error_received(self, exc):
        raise RuntimeError("UDP error : "+exc)

    def connection_lost(self, exc):
        self.loop.stop()
        raise RuntimeError("Socket closed ["+exc+"]")

    def finish(self):
        self.transport.close()
        self.loop.close()

if __name__ == '__main__':    
    parser = ArgumentParser(description="command line for testing")
    parser.add_argument('host')
    parser.add_argument('port')
    parser.add_argument('passwd')
    args = parser.parse_args()
    address = (args.host,args.port)
    pw = args.passwd
    loop = asyncio.get_event_loop()
    pr = RconClientProtocol(loop,address,pw)
    pr.connect()
    print(pr.do_rcon_cmd('cvarlist'))
    pr.finish()

