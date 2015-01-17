import sys
from pdb import set_trace
sys.path.extend(['.','..'])
from controller.svr_controller import *
from model.dmflags import *
from pkg_resources import resource_filename
import os
import os.path
import tkinter as tk
import tkinter.messagebox as msgbox
import pygubu

# TODO: wrap all controller hits in try/except,
#  throw up an error box if fail.

homedir = os.path.expanduser("~")
rc_paths = [os.path.join(homedir,".local","share","cor-games"),
            os.path.join(homedir,".codered"),
            homedir]

rc_paths.append(os.path.curdir)

class AlienArenaApp(pygubu.TkApplication):
    rcf = ''
    def _getvar(self,var):
        return self.builder.get_variable(var)
    def _getobj(self,obj):
        return self.builder.get_object(obj,self.master)
    def _create_ui(self):
        self.controller = {}
        self.current_svr_addr = None
        self.svr_addrs = []
        self.builder = builder = pygubu.Builder()
        builder.add_from_file(resource_filename('view','aaserver.ui'))
        self.svr_dialog = self._getobj('dialog_open_server').toplevel
        self.dmf_dialog = self._getobj('dialog_dmflags').toplevel
        for f in dmf_vars:
            obj = f.replace('f_','chk_')
            self._getobj(obj).configure(command=self._update_dmflags_value)
        self.mainwindow = self._getobj('aaserver_nbk')
        self.master.winfo_toplevel().resizable(width=False,height=False)
        self.mainmenu = menu = self._getobj('menu_main')
        builder.connect_callbacks(self)
        # following needed to get scroll to show up
        self._getobj('plyr_scframe')._clipper.config(width=380,height=150)
        self.set_title('AA Server Control')
        (self.ws,self.hs) = (self.master.winfo_screenwidth(),
                             self.master.winfo_screenheight())
        self._menu_dirty = False
        self.load_menu_from_rc()




    def load_menu_from_rc(self):
        rcf = self._find_rcf()
        if not rcf:
            return
        rcf = open(rcf)
        for line in rcf:
            if line[0] == '#':
                continue
            hpp = line.split()
            address = (hpp[0],hpp[1])
            addr = ":".join(address)
            pwd = hpp[2]
            if (not (addr and pwd)):
                continue
            try:
                self.controller[addr] = ServerController(self)
                self.controller[addr]._set_server_and_connect(address,pwd)
                self._getobj('menu_item_server').add_command(
                    label=addr,
                    command=self._set_server_from_menu(addr)
                )
            except Exception as e:
                del self.controller[addr]
                msgbox.showerror(parent=self.master,
                                 title="aaempirerc",
                                 message="For {addr}: \n{msg}".format(addr=addr,msg=e))
                self._menu_dirty = True

    def save_menu_to_rc(self):
        rcf = self._find_rcf()
        if not rcf:
            global rc_paths
            for dir in rc_paths:
                if os.path.exists(dir):
                    rcf = os.path.join(dir,".aaempirerc")
                    break
        rcf = open(rcf, "w")
        for s in self.controller:
            hp = s.split(":")
            pw = self.controller[s].passwd
            print( "{host}\t{port}\t{pw}".format( host = hp[0],
                                                  port = hp[1],
                                                  pw = pw ),
                   file=rcf)
        rcf.close()

    def _find_rcf(self):
        if self.rcf:
            return self.rcf
        else :
            global rc_paths
            rcf = ''
            for p in rc_paths:
                rcf = os.path.join(p,".aaempirerc")
                if os.path.exists(rcf):
                    break
            self.rcf = rcf
            return self.rcf

    def _ask_to_save(self):
        if self._menu_dirty:
            if (msgbox.askokcancel(parent=self.mainwindow,
                                   title="Save server list",
                                   message="Save server list to .aaempirerc?")):
                self.save_menu_to_rc()

    def on_menu_item_server_click(self):
        (w,h,x,y) = _get_geometry(self.master)
        self.svr_dialog.deiconify()
        self.svr_dialog.wait_visibility(self.svr_dialog)
        (wd,hd,xd,yd) = _get_geometry(self.svr_dialog)
        _set_geometry(self.svr_dialog, wd, hd, x+25, y+25)

    def on_menu_item_save_click(self):
        self._ask_to_save()

    def on_svr_dlg_connect_click(self):
        try:
            addr = self._getvar('open_svr_addr').get()
            if not addr:
                raise RuntimeError('No address specified')
            self.current_svr_addr = addr
            if addr not in self.svr_addrs:
                self.svr_addrs.append(addr)
                self._menu_dirty=True
                self._getobj('menu_item_server').add_command(label=addr,command=self._set_server_from_menu(addr))
            self.controller[addr] = ServerController(self)
            self.controller[addr].set_server_from_dialog()
            self._construct_player_table()
            self._update_current_map()
            self.svr_dialog.withdraw()
        except Exception as e:
            msgbox.showerror(parent=self.svr_dialog,
                             title="Connection", message=e)

    def on_send_cmd_click(self):
        addr = self.current_svr_addr
        if not addr:
            msgbox.showerror(parent=self.mainwindow,
                             title="No connection", message="No server connected")
        else:
            pass
    def on_start_map_click(self):
        addr = self.current_svr_addr
        if not addr:
            msgbox.showerror(parent=self.mainwindow,
                             title="No connection", message="No server connected")
        if not self._getvar('selected_map').get():
            return
        else :
            if (msgbox.askokcancel(parent=self.mainwindow,
                                   title="Start Map", message="Start new map?")):
                try:
                    self.controller[addr].start_map_from_combobox()
                except RuntimeError as e:
                    if (re.match('Map.*not available',e)):
                        msgbox.showerror(parent=self.mainwindow,
                                         title="Map Error", message=e)
                    else:
                        msgbox.showerror(parent=self.mainwindow,
                                     title="Error", message=e)
        self._getvar('selected_map').set('')

    def on_refresh_click(self):
        self._construct_player_table()
        self._update_current_map()

    def on_set_dmflags_click(self):
        addr = self.current_svr_addr
        if not addr:
            msgbox.showerror(parent=self.mainwindow,
                             title="No connection", message="No server connected")
        else:
            dmf = self.controller[addr].get_dmflags()
            self._update_dmflags_boxes(dmf)
            (w,h,x,y) = _get_geometry(self.master)
            self.dmf_dialog.deiconify()
            self.dmf_dialog.wait_visibility(self.dmf_dialog)
            (wd,hd,xd,yd) = _get_geometry(self.dmf_dialog)
            _set_geometry(self.dmf_dialog, wd, hd, x+24, y+24)
            _set_geometry(self.dmf_dialog, wd, hd, x+25, y+25)

    def on_dmflags_dlg_click(self):
        addr = self.current_svr_addr
        if not addr:
            msgbox.showerror(parent=self.mainwindow,
                             title="No connection", message="No server connected")
            self.dmf_dialog.withdraw()
        else:
            if (msgbox.askokcancel(parent=self.dmf_dialog,
                                   title="Set DMFlags", message="Apply new flag settings?")):
                self.controller[addr].set_dmflags(DMFlags(self._getvar('dmf_value').get()))
                self.dmf_dialog.withdraw()

    def _construct_player_table(self):
        addr = self.current_svr_addr
        if not addr:
            return
        players = self.controller[addr].get_current_players()
        pl_frame = self._getobj('plyr_frame')
        for c in pl_frame.winfo_children():
            c.grid_forget()
        lbls_name=[]
        lbls_addr=[]
        btns_kick=[]
        for pl in players:
            lbls_name.append(tk.Label(pl_frame, width=16, height=2, text=pl.stripped_name,relief='ridge'))
            lbls_addr.append(tk.Label(pl_frame, width=16, height=2,text=pl.address,relief='ridge'))
            btns_kick.append(tk.Button(pl_frame, text='Kick', command=self._kick_player(pl)))
        for (n,a,k) in zip(lbls_name,lbls_addr,btns_kick):
            n.grid(in_=pl_frame,column=0)
            ninfo= n.grid_info()
            a.grid(row=ninfo['row'],column=1)
            k.grid(row=ninfo['row'],column=2)
        # necessary to get scrollbar to show and work:
        self._getobj('plyr_scframe').reposition() 

    def _update_current_map(self):
        addr = self.current_svr_addr
        if not addr:
            return
        current_map = self.controller[addr].get_current_map()
        self._getvar('current_map').set(current_map)

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

    def _kick_player(self,plyr):
        def kick():
            nonlocal plyr
            nonlocal self
            if msgbox.askokcancel(parent=self.mainwindow,
                                  title="Kick",message="Kick %s?" % plyr.stripped_name):
                self.controller[self.current_svr_addr].kick_player(plyr)
        return kick

    def _set_server_from_menu(self,addr):
        def set_svr():
            nonlocal addr
            nonlocal self
            self.current_svr_addr=addr
            self.controller[addr]._update_server_info()
            self._construct_player_table()
            self._update_current_map()
        return set_svr   
        

def _get_geometry(tl_obj):
    return map(int, re.split('[x+]',tl_obj.geometry()))

def _set_geometry(tl_obj,w,h,x,y):
    tl_obj.geometry("%dx%d+%d+%d" % (w,h,x,y))

if __name__ == '__main__':
    root = tk.Tk()
    app = AlienArenaApp(root)
    app.run()
