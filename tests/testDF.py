import unittest
from dmflags import *

class DMFlagsTest(unittest.TestCase):
    def testDMFlagsObject(self):
        df = DMFlags()
        self.assertIsInstance(df,DMFlags)
        self.assertEqual(df.value,0)
    def testDMFlagsSet(self):
        df = DMFlags([DF.NO_HEALTH,DF.SPAWN_FARTHEST,
                              DF.ALLOW_EXIT,DF.QUADFIRE_DROP,
                              DF.BOT_FUZZYAIM])
        self.assertTrue(df.is_set(DF.BOT_FUZZYAIM))
        self.assertFalse(df.is_set(DF.BOTS))
    def testDMFlagsSetWithInts(self):
        df = DMFlags([1,2,0x00000100,0x00000800,0x00200000])
        self.assertTrue(df.is_set(DF.BOT_LEVELAD))
        self.assertTrue(df.is_set(DF.NO_ITEMS))
        self.assertTrue(df.is_set(DF.NO_ARMOR))
        self.assertFalse(df.is_set(DF.SAME_LEVEL))
        self.assertFalse(df.is_set(DF.ALLOW_EXIT))
    def testDMFlagsSetWithSingleValue(self):
        df = DMFlags(2385176)
        self.assertEqual(df.value, 2385176)
        self.assertFalse(df.is_set(DF.BOTS))
        self.assertFalse(df.is_set(DF.SKINTEAMS))
        self.assertTrue(df.is_set(DF.INFINITE_AMMO))
        self.assertTrue(df.is_set(DF.BOTCHAT))
        


if __name__ == '__main__':
    unittest.main()
