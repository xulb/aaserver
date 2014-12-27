from model.aaserver import *
from unittest.mock import Mock

mockServer = Mock(spec=AAServer)
mockServer.current_players = [
    Player('Xulb','111.222.333.444'),
    Player('[OS]^1Bis^2ki^7','999.33.2.1'),
    Player('>>Sander','5.4.3.23')
]
mockServer.name = 'mock'
mockServer.admin = 'Xulb'

class ServerController:
    def __init__(self,app):
        self.app = app
        self.address = None
        self.passwd = None
    def _getvar(self,var):
        return self.app.builder.get_variable(var)
    def _set_server_and_connect(self, address, passwd):
        self.address = address
        self.passwd = passwd
        if passwd!='mock':
            self.server = AAServer(address, passwd)
        else :
            self.server = mockServer
        self.name = self.server.name
        self.admin = self.server.admin

    def set_server_from_dialog(self):
        addr = tuple(
            self._getvar('open_svr_addr').get().split(':'))
        passwd =self._getvar('open_svr_pass').get()
        self._set_server_and_connect(addr,passwd)
        self._getvar('server_name').set(self.name)
        self._getvar('svr_addr').set(":".join(self.address))
        
    def get_current_players(self):
        self.server._poll_status()
        return self.server.current_players

#msg_servername
#msg_svraddr
#msg_mapname
        
