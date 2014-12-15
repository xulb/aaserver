import sys
sys.path.append('..')
from controller.svr_controller import *
import os
import tkinter as tk
import tkinter.messagebox as msgbox
import pygubu

ui_file = os.path.join(os.path.dirname(os.path.realpath(__file__)),'aaserver.ui')
class AlienArenaApp(pygubu.TkApplication):
    def _create_ui(self):
        self.controller = ServerController(self)
        self.builder = builder = pygubu.Builder()
        builder.add_from_file(ui_file)
        self.svr_dialog = builder.get_object('dialog_open_server',self.master)
        self.svr_dialog.toplevel.wm_positionfrom(who="user")
        self.mainwindow = builder.get_object('aaserver_nbk',self.master)
        self.mainmenu = menu = builder.get_object('menu_main',self.master)
        self.set_menu(menu)
        self.set_title('AA Server')
        builder.connect_callbacks(self)

    def on_menu_item_server_click(self):
        self.svr_dialog.toplevel.deiconify()

    def on_svr_dlg_connect_click(self):
        try:
            self.controller.set_server_from_dialog()
            self.svr_dialog.toplevel.withdraw()
        except Exception as e:
            msgbox.showerror(title="Connection", message=e)

if __name__ == '__main__':
    root = tk.Tk()
    app = AlienArenaApp(root)
    app.run()
