import sys
from pdb import set_trace
sys.path.extend(['.','..'])
from empire.controller.svr_controller import *
from empire.view.console import *
from empire.model.dmflags import *
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
        self.console = {}
        self.current_svr_addr = None
        self.builder = builder = pygubu.Builder()
        builder.add_from_file(resource_filename('empire.view','aaserver.ui'))
        self.svr_dialog = self._getobj('dialog_open_server').toplevel
        self.dmf_dialog = self._getobj('dialog_dmflags').toplevel
        self.plr_dialog = self._getobj('dialog_player_details').toplevel
        for f in dmf_vars:
            obj = f.replace('f_','chk_')
            self._getobj(obj).configure(command=self._update_dmflags_value)
        self.mainwindow = self._getobj('aaserver_nbk')
        top = self.master.winfo_toplevel()
        top.rowconfigure(0,weight=1)
        top.columnconfigure(0,weight=1)
        self._getobj('plyr_frame').columnconfigure(0,weight=1)
        self._getobj('plyr_frame').columnconfigure(1,weight=1)

        self.plr_dialog.rowconfigure(0,weight=1)
        self.plr_dialog.columnconfigure(0,weight=1)
        self.mainmenu = menu = self._getobj('menu_main')
        builder.connect_callbacks(self)
        # following needed to get scroll to show up
 #       self._getobj('plyr_scframe')._clipper.config(width=400,height=150)
        self.set_title('AAEmpire')
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
                self._add_controller_and_console(addr,pwd)
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
        self._menu_dirty = False

    def _find_rcf(self):
        if self.rcf:
            return self.rcf
        else :
            global rc_paths
            rcf = ''
            for p in rc_paths:
                f = os.path.join(p,".aaempirerc")
                if os.path.exists(f):
                    rcf = f
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
            if (self.current_svr_addr in self.console):
                self.console[self.current_svr_addr].save()
            self.current_svr_addr = addr
            self._add_controller_and_console(addr,'',from_dlg=1)
            self._update_view()
            self.svr_dialog.withdraw()
            self.set_title('AAEmpire - '+self.controller[addr].name)
        except Exception as e:
            msgbox.showerror(parent=self.svr_dialog,
                             title="Connection", message=e)
            self.set_title('AAEmpire')

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
            self.master.winfo_toplevel().update_idletasks()
            (w,h,x,y) = _get_geometry(self.master)
            self.dmf_dialog.deiconify()
            self.dmf_dialog.wait_visibility(self.dmf_dialog)
            (wd,hd,xd,yd) = _get_geometry(self.dmf_dialog)
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

    def _add_controller_and_console(self,addr,pwd,from_dlg=0):
        if addr not in self.controller:
            self.controller[addr] = ServerController(self)
            self.console[addr] = Console(self._getobj('console_tab_frame'),
                controller=self.controller[addr])
            if from_dlg:
                self.controller[addr].set_server_from_dialog()
            else:
                self.controller[addr]._set_server_and_connect(addr,pwd)
            self._menu_dirty=True
            self._getobj('menu_item_server').add_command(
                label=addr,
                command=self._set_server_from_menu(addr))


    def _update_view(self):
        self._update_current_map()
        self._construct_player_table()
        self._update_console()

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
        for pl in players:
            lbls_name.append(tk.Label(pl_frame, width=20, height=2, text=pl.stripped_name,relief='ridge'))
            lbls_addr.append(tk.Label(pl_frame, width=20, height=2,text=pl.address,relief='ridge'))
        for (n,a,pl) in zip(lbls_name,lbls_addr,players):
            n.grid(in_=pl_frame,column=0,sticky=tk.N+tk.E+tk.W)
            ninfo= n.grid_info()
            a.grid(row=ninfo['row'],column=1,sticky=tk.N+tk.W+tk.E)
            n.unbind('<ButtonRelease-1>')
            n.bind('<ButtonRelease-1>',self._show_player_detail_dlg(pl))
            a.unbind('<ButtonRelease-1>')
            a.bind('<ButtonRelease-1>',self._show_player_detail_dlg(pl))
        # necessary to get scrollbar to show and work:
        self._getobj('plyr_scframe').reposition() 

    def _update_current_map(self):
        addr = self.current_svr_addr
        if not addr:
            return
        current_map = self.controller[addr].get_current_map()
        self._getvar('current_map').set(current_map)

    def _update_console(self):
        addr = self.current_svr_addr
        if not addr:
            return
        con = self.console[addr]
        con_frame = self._getobj('console_tab_frame')
        for c in con_frame.winfo_children():
            c.grid_remove()
        con.tw.grid(sticky=tk.N+tk.S+tk.E+tk.W)
        

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

    def _update_player_detail_dlg(self,plyr):
        self._getvar("msg_pd_player").set(plyr.stripped_name)
        for item in ['host','port','ping','score']:
            self._getvar("msg_pd_%s" % item).set(getattr(plyr,item,None))
        self._getobj("btn_pd_kick").configure(command=self._kick_player(plyr))

    def _show_player_detail_dlg(self,plyr):
        def player_dlg(ev):
            nonlocal plyr
            nonlocal self
            self._update_player_detail_dlg(plyr)
            self.master.winfo_toplevel().update_idletasks()
#           self.plr_dialog.transient(self.master.winfo_toplevel())
            self.plr_dialog.deiconify()
            self.plr_dialog.wait_visibility(self.plr_dialog)
            (wd,hd,xd,yd) = _get_geometry(self.plr_dialog)
            (w,h,x,y) = _get_geometry(self.master)
            _set_geometry(self.plr_dialog, wd, hd, x+25, y+25)
        return player_dlg


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
            if (self.current_svr_addr in self.console):
                self.console[self.current_svr_addr].save()
            self.current_svr_addr=addr
            self.controller[addr]._update_server_info()
            self.set_title('AAEmpire - '+self.controller[addr].name)
            self._update_view()
        return set_svr
        

def _get_geometry(tl_obj):
    return map(int, re.split('[x+]',tl_obj.geometry()))

def _set_geometry(tl_obj,w,h,x,y):
    tl_obj.geometry("%dx%d+%d+%d" % (w,h,x,y))

if __name__ == '__main__':
    root = tk.Tk()
    app = AlienArenaApp(root)
    app.run()
