from model.aaserver import *

class ServerController:
    def __init__(self,app):
        self.app = app
        self.address = None
        self.passwd = None
    def _set_server_and_connect(self, address, passwd):
        self.address = address
        self.passwd = passwd
        self.server = AAServer(address, passwd)
    def set_server_from_dialog(self):
        addr = tuple(
            self.app.builder.get_variable('open_svr_addr').get().split(':'))
        passwd =self.app.builder.get_variable('open_svr_pass').get()
        self._set_server_and_connect(addr,passwd)

        
