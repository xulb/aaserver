import tkinter as tk

class Console():
    promptstr = '>'
    def __init__(self, textwidget, controller=None):
        self.tw = textwidget
        self.controller = controller
        self.tw.event_add('<<Submit>>','Return','KeyRelease-Return')
        self.tw.bind('<<Submit>>',self.submit)
        self._oldtext=''
        self.clear()

    def clear(self):
        self.tw.delete('1.0',tk.END)
        self.display_prompt()
        
    def submit(self,event):
        cmd = self.get_command()
        if cmd:
            resp = self.do_request(cmd)
            self.display_response(resp=resp)
        self.display_prompt()

    def get_command(self):
        return self.tw.get("PROMPT",tk.END)

    def do_request(self,cmd):
        resp=''
        if self.controller:
            pass
        return resp

    def display_prompt(self):
        self.tw.insert(tk.END,"\n%s" % self.promptstr)
        self.tw.mark_set("PROMPT",tk.END)
        self.tw.mark_gravity("PROMPT",tk.RIGHT)

    def display_response(self,resp=''):
        if resp:
            self.tw.insert("\n"+resp)
        self.display_prompt()
    
    def save(self):
        self._oldtext = self.tw.get('1.0',tk.END)

    def restore(self):
        if not self._oldtext:
            return
        else:
            self.tw.delete('1.0',tk.END)
            self.tw.insert(tk.END,self._oldtext)
            self.tw.edit_reset()
            self._oldtext=''
            self.display_prompt()
