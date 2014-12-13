from enum import Enum

class DF(Enum):
    NO_HEALTH = 0x00000001
    NO_ITEMS = 0x00000002
    WEAPONS_STAY = 0x00000004
    NO_FALLING = 0x00000008
    INSTANT_ITEMS = 0x00000010
    SAME_LEVEL = 0x00000020
    SKINTEAMS = 0x00000040
    NO_FRIENDLY_FIRE = 0x00000100
    SPAWN_FARTHEST = 0x00000200
    FORCE_RESPAWN = 0x00000400
    NO_ARMOR = 0x00000800
    ALLOW_EXIT = 0x00001000
    INFINITE_AMMO = 0x00002000
    QUAD_DROP = 0x00004000
    QUADFIRE_DROP = 0x00010000
    BOT_AUTOSAVENODES = 0x00020000
    BOTCHAT = 0x00040000
    BOT_FUZZYAIM = 0x00080000
    BOTS = 0x00100000
    BOT_LEVELAD = 0x00200000
    
class DMFlags():
    def __init__(self, enum_list_or_value=0):
        self.value = 0
        if (isinstance(enum_list_or_value,list)):
            for i in enum_list_or_value:
                self.value += i.value if isinstance(i,Enum) else i
        else:
            self.value += enum_list_or_value
            
    def __str__(self):
        ret = 'Flags: '
        ret += ' '.join([f.name for f in DF if self.is_set(f)])
        return ret


    def is_set(self, flag_constant):
        if( not flag_constant or not isinstance(flag_constant,DF)):
            raise RuntimeError("arg must be present and a DF constant")
        return (self.value & flag_constant.value)
