import model.rcon as rcon
from model.dmflags import *
import asyncio
import re
import sys

class AAServer(rcon.RconClientProtocol):
    def __init__(self, address, passwd):
        loop = asyncio.get_event_loop()
        super().__init__(loop, address, passwd)
        try:
            self.connect()
        except Exception as e:
            raise RuntimeError("Problem connecting : %s" % e)

    @property
    def maplist(self):
        resp = self.do_rcon_cmd('sv_maplist')
        resp = re.sub('["]|\n','',resp)
        resp = re.sub('\s*sv_maplist\s*is\s*','',resp)
        resp = re.sub('\s+',' ',resp)
        return resp.split(' ')

    @property
    def dmflags(self):
        return DMFlags(self.cvar('dmflags'))
    @property
    def name(self):
        return q2strip(self.cvar('hostname'))
    @property
    def admin(self):
        return q2strip(self.cvar('admin'))

    def cvar(self,cvar,value=None):
        if value or value == 0:
            self.do_rcon_cmd('set %s "%s"' % (cvar,value))
            return value
        else:
            resp = self.do_rcon_cmd(cvar)
            if bad_pass_resp(resp):
                raise RuntimeError(resp)
            resp = resp.rstrip();
            resp = re.sub('^.* is ','',resp)
            resp = re.sub('"','',resp)
            try:
                val = int(resp)
                return val
            except:
                return resp

    def botkickthreshold(self,value=None):
        return self.cvar('sv_botkickthreshold',value)

    def startmap(self, the_map):
        resp = self.do_rcon_cmd("startmap %s" % the_map)
        if (re.match('Cannot find',resp)):
            raise RuntimeError("Map %s not available" % the_map)

    def _poll_status(self):
        resp = self.do_rcon_cmd('status')
        players = []
        hdr = []
        self.current_players = []
        for l in resp.splitlines():
            l = l.rstrip()
            if not l:
                continue
            m = re.match('^map\s+:\s+(\S+)',l)
            if m:
                self.current_map = m.group(1)
                continue
            m = re.match('^num',l)
            if m:
                hdr = l.split()
                continue
            m = re.match('^---',l)
            if m:
                continue
            if hdr: # now on a player status line
#                d = dict(zip(hdr,l.split()))
#                player = Player(d['name'],d['address'])
                player = Player(l)
                self.current_players.append(player)
                continue

    def kick(self, player_or_name):
        name = player_or_name
        if (isinstance(player_or_name,Player)):
            name = player_or_name.name
        self._poll_status()
        candidates = [p for p in self.current_players
                      if name == p.name or name == p.stripped_name]
        if candidates:
            resp = self.do_rcon_cmd("kick %s" % candidates[0].name)
            if re.match('was kicked',resp):
                return True
        return False

    def set_dmflags(self, dmf):
        if not dmf.value:
            raise RuntimeError('No DMFlags set')
        self.cvar('dmflags', dmf.value)

class Player:
    def __init__(self, name_or_status_line, address=None):
        if address:
            self.name = name_or_status_line
            self.stripped_name = q2strip(self.name)
            self.address = address
        else:
            line = name_or_status_line
            items = line.split()
            props = dict( zip( ['num','score','ping','name',
                                'lastmsg','address','qport'],
                               items ) )
            self.name = props['name']
            self.stripped_name = q2strip(props['name'])
            self.address = props['address']
            addr = props['address'].split(':')
            self.host = addr[0]
            self.port = addr[1]
            self.ping = props['ping']
            self.score = props['score']
            self.qport = props['qport']
        
def q2strip(s):
    """
    Strip out color escapes from Quake 2 strings
    """
    ret = ''
    in_esc = False
    for c in s:
        if (in_esc):
            in_esc = False
            continue
        else:
            if (c == '^'):
                in_esc = True
                continue
            else:
                ret += c
    return ret

def bad_pass_resp(resp):
    return re.match('Bad rcon.pass',resp)
if __name__ == '__main__':
    args = dict(['host','port','passwd'],sys.argv[-3:])
    svr = AAServer((args['host'],args['port']),args['passwd'])
    resp = svr.do_rcon_cmd('sv_botkickthreshold')
    svr.kick('[OS]Xulb');
    1

