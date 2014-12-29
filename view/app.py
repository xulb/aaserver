#!/usr/bin/python3
import sys
sys.path.extend(['.','..'])
from controller.svr_controller import *
from model.dmflags import *
import os
import tkinter as tk
import tkinter.messagebox as msgbox
import pygubu


ui_file = os.path.join(os.path.dirname(os.path.realpath(__file__)),'aaserver.ui')

dmf_vars = {
    'f_nopwr' : 'NO_ITEMS',
    'f_instant' : 'INSTANT_ITEMS',
    'f_quaddrop' : 'QUAD_DROP',
    'f_nohealth' : 'NO_HEALTH',
    'f_weapstay' : 'WEAPONS_STAY',
    'f_infammo' : 'INFINITE_AMMO',
    'f_noarmor' : 'NO_ARMOR',
    'f_samemap' : 'SAME_LEVEL',
    'f_allowexit' : 'ALLOW_EXIT',
    'f_fixfov' : 'FIXED_FOV',
    'f_noffire' : 'NO_FRIENDLY_FIRE',
    'f_teamsmodel' : 'MODELTEAMS',
    'f_teamsskin' : 'SKINTEAMS',
    'f_nobots' : 'BOTS',
    'f_botaim' : 'BOT_FUZZYAIM',
    'f_nobotchat' : 'BOTCHAT',
    'f_botautonode' : 'BOT_AUTOSAVENODES',
    'f_alwaysadv' : 'BOT_LEVELAD',
    'f_respawn' : 'FORCE_RESPAWN',
    'f_farspawn' : 'SPAWN_FARTHEST',
    'f_nofall' : 'NO_FALLING'
}

class AlienArenaApp(pygubu.TkApplication):
    def _getvar(self,var):
        return self.builder.get_variable(var)
    def _getobj(self,obj):
        return self.builder.get_object(obj,self.master)
    def _create_ui(self):
        self.controller = ServerController(self)
        self.builder = builder = pygubu.Builder()
        builder.add_from_file(ui_file)
        self.svr_dialog = self._getobj('dialog_open_server').toplevel
        self.svr_dialog.wm_positionfrom(who="user")
        self.dmf_dialog = self._getobj('dialog_dmflags').toplevel
        self.dmf_dialog.wm_positionfrom(who="user")
        for f in dmf_vars:
            obj = f.replace('f_','chk_')
            self._getobj(obj).configure(command=self._update_dmflags_value)
        self.mainwindow = self._getobj('aaserver_nbk')
        self.mainmenu = menu = self._getobj('menu_main')
        self.set_menu(menu)
        self.set_title('AA Server Control')
        (self.ws,self.hs) = (self.master.winfo_screenwidth(),
                             self.master.winfo_screenheight())
        builder.connect_callbacks(self)


    def on_menu_item_server_click(self):
        self.svr_dialog.deiconify()

    def on_svr_dlg_connect_click(self):
        try:
            self.controller.set_server_from_dialog()
            self.svr_dialog.withdraw()
        except Exception as e:
            msgbox.showerror(title="Connection", message=e)

    def on_send_cmd_click(self):
        pass
    def on_start_map_click(self):
        try:
            self.controller.start_map_from_combobox()
        except RuntimeError as e:
            if (re.match('Map.*not available',e)):
                msgbox.showerror(title="Map Error", message=e)
            else:
                msgbox.showerror(title="Error", message=e)

    def on_refresh_click(self):
        self._construct_player_table()

    def on_set_dmflags_click(self):
        dmf = self.controller.get_dmflags()
        self._update_dmflags_boxes(dmf)
        self.dmf_dialog.deiconify()

    def on_dmflags_dlg_click(self):
        self.controller.set_dmflags(DMFlags(self._getvar('dmf_value').get()))
        self.dmf_dialog.withdraw()

    def _construct_player_table(self):
        players = self.controller.get_current_players()
        pl_frame = self._getobj('plyr_tab_frame')
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
 
    def _update_dmflags_boxes(self,dmf):
        for f in dmf_vars:
            flag = eval('DF.{0}'.format(dmf_vars[f]))
            if dmf.is_set(flag):
                self._getvar(f).set(dmf_vars[f])
            else:
                self._getvar(f).set('')
        self._update_dmflags_value()


    def _update_dmflags_value(self):
        value = 0
        for f in dmf_vars:
            flag = eval('DF.{0}'.format(dmf_vars[f]))
            if self._getvar(f).get() == dmf_vars[f]:
                value += flag.value
        self._getvar('dmf_value').set(value)


if __name__ == '__main__':
    root = tk.Tk()
    app = AlienArenaApp(root)
    app.run()
