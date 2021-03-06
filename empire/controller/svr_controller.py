from empire.model.aaserver import *
from empire.model.dmflags import *
from unittest.mock import Mock

mockServer = Mock(spec=AAServer)
mockServer.current_players = [
    Player('Xulb','111.222.333.444'),
    Player('[OS]^1Bis^2ki^7','999.33.2.1'),
    Player('>>Sander','5.4.3.23'),
    Player('Xulb','111.222.333.444'),
    Player('[OS]^1Bis^2ki^7','999.33.2.1'),
    Player('>>Sander','5.4.3.23'),
    Player('Xulb','111.222.333.444'),
    Player('[OS]^1Bis^2ki^7','999.33.2.1'),
    Player('>>Sander','5.4.3.23')
]
mockServer.current_map = "dm-ahtcity"
mockServer.dmflags = DMFlags(2385176)
mockServer.name = 'mock'
mockServer.admin = 'Xulb'
mockServer.maplist = "dm8 dm-ahtcity dm-atlantis2k8 dm-babel2k11 dm-blood dm-bloodfactory2k12 dm-bonechewer dm-chasmatic2k9 dm-corrosion dm-crucible2k12 dm-deathray dm-deimos2k9 dm-dismal2k11  dm-dungeon dm-dynamo2k12 dm-egyptian dm-electro dm-eternal  dm-frontier2 dm-furious2k8 dm-gladiator dm-goregrinder dm-hangar-beta dm-horus dm-impact dm-inferno dm-infinic dm-invasion dm-khanate dm-leviathan2k12 dm-liberation dm-mgcity2 dm-module dm-negator dm-neptune dm-nkitrn1 dm-oblivion dm-omega2k8 dm-outpost dm-purgatory  dm-titan2k8 dm-turbo2k8 dm-vesuvius2k11 dm-violator2k11 dm-warmachine2k10 dm-zorn2k11 dm-zion2k9".split()



class ServerController:
    def __init__(self,app):
        self.app = app
        self.address = None
        self.passwd = None
    def _getvar(self,var):
        return self.app.builder.get_variable(var)
    def _getobj(self,obj):
        return self.app.builder.get_object(obj,self.app.master)
    def _set_server_and_connect(self, addr, passwd):
        self.address = tuple(addr.split(':'))
        self.passwd = passwd
        if passwd!='mock':
            self.server = AAServer(self.address, self.passwd)
        else :
            self.server = mockServer
        self.name = self.server.name
        self.admin = self.server.admin
        self.maplist = " ".join(self.server.maplist)

    def set_server_from_dialog(self):
        addr = self._getvar('open_svr_addr').get()
        passwd =self._getvar('open_svr_pass').get()
        passwd = passwd.strip()
        self._set_server_and_connect(addr,passwd)
        self._update_server_info()

    def _update_server_info(self):
        self._getvar('server_name').set(self.name)
        self._getvar('svr_addr').set(":".join(self.address))
        self._getobj('cmb_maps').configure(values=self.maplist)
        
    def get_current_players(self):
        self.server._poll_status()
        return self.server.current_players

    def get_current_map(self):
        self.server._poll_status()
        return self.server.current_map

    def start_map_from_combobox(self):
        the_map = self._getvar('selected_map').get()
        if not the_map:
            return
        self.server.startmap(the_map)
        
    def get_dmflags(self):
        return self.server.dmflags

    def set_dmflags(self,dmf):
        self.server.set_dmflags(dmf)

    def kick_player(self,plyr):
        self.server.kick(plyr)
        
    def send_cmd(self,cmd):
        """
        Send an rcon cmd and return the server response.
        """
        return self.server.do_rcon_cmd(cmd)

#msg_servername
#msg_svraddr
#msg_mapname
        
