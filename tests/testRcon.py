import unittest
import model.rcon as rcon
import asyncio
import re
import sys
from testArgs import testArgs

args = testArgs()
address=(args.host,args.port)
bad_address=(args.host,'65000')
passwd=args.passwd

class RconCommandTest(unittest.TestCase):
    def setUp(self):
        self.rconCommand = rcon.RconCommand('set foo 1','s3ckr1t')
    def testRconBytestr(self):
        self.assertEqual(self.rconCommand.bytestr,
                             b'\xff\xff\xff\xff rcon "s3ckr1t" set foo 1\x00')

class RconCommandFactoryTest(unittest.TestCase):
    def setUp(self):
        self.fac = rcon.RconCommandFactory('s3ckr1t')
    def testRconCommand(self):
        self.assertEqual(self.fac.cmd('set foo 1'),
                             b'\xff\xff\xff\xff rcon "s3ckr1t" set foo 1\x00')
        self.assertIsInstance(self.fac.lastCommand,rcon.RconCommand)
        with self.assertRaises(RuntimeError):
            self.fac.cmd('')

class RconClientProtocolTest(unittest.TestCase):
    def setUp(self):
        global address, passwd
        loop = asyncio.get_event_loop()
        self.rcp = rcon.RconClientProtocol(loop, address, passwd)
        self.bad_rcp = rcon.RconClientProtocol(loop, bad_address, passwd)
    def testRcpConnect(self):
        self.rcp.connect()
        self.assertTrue(self.rcp.transport)
    def testRcpDoRconCmd(self):
        self.rcp.connect()
        self.assertTrue(re.match('\"sv_botkickthreshold\" is',
                                 self.rcp.do_rcon_cmd('sv_botkickthreshold')))
        self.assertTrue(re.match('map\s+:',
                                 self.rcp.do_rcon_cmd('status')))
    def testRcpTimeout(self):
        self.bad_rcp.connect()
        with self.assertRaises(Exception):
            self.bad_rcp.do_rcon_cmd('sv_botkickthreshold')

if __name__ == '__main__':
    unittest.main()

