from model.aaserver import *
from model.dmflags import *
from unittest.mock import Mock
import tkinter.messagebox as msgbox

mockServer = Mock(spec=AAServer)
mockServer.current_players = [
    Player('Xulb','111.222.333.444'),
    Player('[OS]^1Bis^2ki^7','999.33.2.1'),
    Player('>>Sander','5.4.3.23')
]
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
    def _set_server_and_connect(self, address, passwd):
        self.address = address
        self.passwd = passwd
        if passwd!='mock':
            self.server = AAServer(address, passwd)
        else :
            self.server = mockServer
        self.name = self.server.name
        self.admin = self.server.admin
        self.maplist = " ".join(self.server.maplist)

    def set_server_from_dialog(self):
        addr = tuple(
            self._getvar('open_svr_addr').get().split(':'))
        passwd =self._getvar('open_svr_pass').get()
        self._set_server_and_connect(addr,passwd)
        self._getvar('server_name').set(self.name)
        self._getvar('svr_addr').set(":".join(self.address))
        self._getobj('cmb_maps').configure(values=self.maplist)
        
    def get_current_players(self):
        self.server._poll_status()
        return self.server.current_players

    def start_map_from_combobox(self):
        the_map = self._getvar('selected_map').get()
        if (msgbox.askokcancel("Start Map", "Start map %s?" % the_map)):
            self.server.startmap(the_map)
        
    def get_dmflags(self):
        return self.server.dmflags

    def set_dmflags(self,dmf):
        self.server.set_dmflags(dmf)
        

#msg_servername
#msg_svraddr
#msg_mapname
        
