#!/usr/bin/python3
import sys
sys.path.extend(['.','..'])
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
        self.set_title('AA Server Control')
        builder.connect_callbacks(self)

    def on_menu_item_server_click(self):
        self.svr_dialog.toplevel.deiconify()

    def on_svr_dlg_connect_click(self):
        try:
            self.controller.set_server_from_dialog()
            self.svr_dialog.toplevel.withdraw()
        except Exception as e:
            msgbox.showerror(title="Connection", message=e)

    def on_send_cmd_click(self):
        pass
    def on_start_map_click(self):
        pass

    def on_refresh_click(self):
        self._construct_player_table()

    def _construct_player_table(self):
        players = self.controller.get_current_players()
        pl_frame = self.builder.get_object('plyr_tab_frame',self.master)
        lbls_name=[]
        lbls_addr=[]
        btns_kick=[]
        for pl in players:
            lbls_name.append(tk.Label(pl_frame, width=16, text=pl.stripped_name))
            lbls_addr.append(tk.Label(pl_frame, width=16, text=pl.address))
            btns_kick.append(tk.Button(pl_frame, text='Kick'))
        for (n,a,k) in zip(lbls_name,lbls_addr,btns_kick):
            n.grid(column=0)
            ninfo= n.grid_info()
            a.grid(row=ninfo['row'],column=1)
            k.grid(row=ninfo['row'],column=2)
        

if __name__ == '__main__':
    root = tk.Tk()
    app = AlienArenaApp(root)
    app.run()
