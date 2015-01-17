#import sys
#sys.path.append('..')
import unittest
from unittest.mock import MagicMock
import model.aaserver as aaserver
import model.rcon as rcon
from tests.testArgs import testArgs

args = testArgs()
address=(args.host,args.port)
bad_address=(args.host,'65000')
passwd=args.passwd

class AAServerTest(unittest.TestCase):
    def setUp(self):
        self.svr = aaserver.AAServer(address, passwd)
    def testIsaRCP(self):
        self.assertIsInstance(self.svr,rcon.RconClientProtocol)
    def testCvar(self):
        self.assertEqual(self.svr.cvar("narb",1), 1)
        self.assertEqual(self.svr.cvar("narb"), 1)
    def testBotkickthreshold(self):
        self.assertEqual(self.svr.botkickthreshold(),
                         self.svr.cvar("sv_botkickthreshold"))

class PlayerTest(unittest.TestCase):
    def testPlayer(self):
        p = aaserver.Player('^1X^7ul^4b','127.0.0.1')
        self.assertEqual(p.name,'^1X^7ul^4b')
        self.assertEqual(p.stripped_name, 'Xulb')
        self.assertEqual(p.address, '127.0.0.1')

class ServerStatusTest(unittest.TestCase):
    def setUp(self):
        self.svr = aaserver.AAServer(address, passwd)
        self.svr.do_rcon_cmd = MagicMock(return_value="""map              : dm-deimos2k9
num score ping name            lastmsg address               qport 
--- ----- ---- --------------- ------- --------------------- ------
  0     0   43 ^7[OS]^1X^7ul^4b              9 72.83.4.170:41193       244
   """)
    
    def testPollStatusParse(self):
        self.svr._poll_status()
        self.assertEqual(self.svr.current_map,'dm-deimos2k9')
        self.assertEqual(len(self.svr.current_players),1)
        for p in self.svr.current_players:
            self.assertEqual(p.stripped_name, '[OS]Xulb')


class Q2StripTest(unittest.TestCase):
        def testOrdinaryString(self):
            self.assertEqual(aaserver.q2strip('ordinary string'),
                             'ordinary string')
        def testEasyString(self):
            self.assertEqual(aaserver.q2strip('^3T^1his^7 is easy'),
                             'This is easy')
        def testHardString(self):
            self.assertEqual(aaserver.q2strip('^Thi^@s is^^^  harder^4'),
                             'his is harder')



if __name__ == '__main__':
    unittest.main()
