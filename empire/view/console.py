import tkinter as tk
from tkinter.scrolledtext import ScrolledText
from pdb import set_trace
class Console():
    """
    Make a tk.ScrolledText widget behave like a command console.
    """
    promptstr = '> '
    def __init__(self, parent, controller=None):
        self.tw = ScrolledText(parent, font='TkFixedFont',foreground='#0000eb',
                               height=10,width=50,undo=True,maxundo=15)
        self.tw.rowconfigure(0,weight=1)
        self.tw.columnconfigure(0,weight=1)
        self.controller = controller
        self.tw.event_add('<<Submit>>','<KeyPress-Return>')
        self.tw.bind('<<Submit>>',self.submit)
#        self.tw.bind('<Escape>',lambda event: set_trace())
        self._hack_events()
        self._oldtext=''
        self.clear()

    def clear(self):
        self.tw.delete('1.0',tk.END)
        self.display_prompt(noret=1)
        
    def submit(self,event):
        cmd = self.get_command()
        if cmd:
            resp = self.do_request(cmd)
            self.display_response(resp=resp)
        self.display_prompt()
        return "break"

    def get_command(self):
        cmd = self.tw.get('PROMPT',tk.END)
        return cmd

    def do_request(self,cmd):
        resp=''
        if self.controller:
            resp = self.controller.send_cmd(cmd)
        return resp

    def display_prompt(self,noret=0):
        prompt = self.promptstr;
        prompt = prompt if noret else "\n"+prompt
        self.tw.insert(tk.END,prompt)
        # self.prindex = self.tw.index(tk.INSERT)
        self.tw.mark_set(tk.INSERT,tk.END)
        self.tw.mark_set('PROMPT',tk.INSERT)
        self.tw.mark_gravity('PROMPT',tk.LEFT)
        self.tw.see('PROMPT')

    def display_response(self,resp=''):
        if resp:
            self.tw.insert(tk.END,"\n"+resp)
    
    def save(self):
        self._oldtext = self.tw.get('1.0',tk.END)

    def restore(self):
        if not self._oldtext:
            return
        else:
            self.tw.delete('0.0',tk.END)
            self.tw.insert(tk.END,self._oldtext)
            self.tw.edit_reset()
            self._oldtext=''
            self.display_prompt()

    def _hack_events(self):
        tw = self.tw
        def prevchar():
            ins = list( map( int, tw.index(tk.INSERT).split('.') ) )
            if ins[1] == 0:
                ins[0] = ins[0]-1 if ins[0] > 1 else ins[0]
                ins[1] = 100
            else:
                ins[1] = ins[1]-1
            return "%d.%d" % (ins[0],ins[1])
        def prevline():
            ins = list( map( int, tw.index(tk.INSERT).split('.') ) )
            ins[0] = ins[0]-1 if ins[0] > 0 else ins[0]
            return "%d.%d" % (ins[0],ins[1])
        def prevword():
            idx = tw.search('\m.',tk.INSERT,backwards=True,regexp=True)
            print(idx)
            return idx
        def linestart(e):
            tw.mark_set('insert','PROMPT')
            return 'break'
        def cursor_protect(e):
            if (e.widget.compare(tk.INSERT,"<=",'PROMPT')):
                e.widget.mark_set(tk.INSERT,tk.END)
            

        for ev in ['<<PrevChar>>','<<PrevWord>>','<<PrevLine>>']:
            tw.bind(ev, lambda e: 'break' if e.widget.compare(tk.INSERT,"<=",'PROMPT') else '')
        tw.bind('<<PrevChar>>',
                lambda e: 'break' if e.widget.compare(prevchar(),"<=",'PROMPT') else '')
        tw.bind('<<PrevLine>>',
                lambda e: 'break' if e.widget.compare(prevline(),"<=",'PROMPT') else '')
        tw.bind('<<PrevWord>>',
                lambda e: 'break' if e.widget.compare(prevword(),">", tk.INSERT) or e.widget.compare(prevword(),"<=",'PROMPT') else '')
        tw.bind('<BackSpace>', lambda e: 'break' if e.widget.compare(tk.INSERT,"<=",'PROMPT') else '')
        tw.bind('<<LineStart>>', linestart)
        tw.bind('<ButtonRelease-1>',cursor_protect)
        tw.event_add('<<PrevWord>>','<Alt-Key-b>')
        tw.event_add('<<NextWord>>','<Alt-Key-f>')



# text widget events
#('<<Undo>>', '<<Redo>>', '<<PrevWord>>', '<<NextWord>>', '<<Copy>>', '<<SelectAll>>', '<<NextPara>>', '<<NextLine>>', '<<SelectLineEnd>>', '<<LineStart>>', '<<Paste>>', '<<ContextMenu>>', '<<SelectNextWord>>', '<<NextChar>>', '<<Submit>>', '<<SelectPrevLine>>', '<<SelectLineStart>>', '<<ToggleSelection>>', '<<SelectNextPara>>', '<<PrevPara>>', '<<SelectPrevPara>>', '<<NextWindow>>', '<<SelectNextLine>>', '<<PrevWindow>>', '<<SelectNextChar>>', '<<SelectPrevChar>>', '<<Cut>>', '<<PrevLine>>', '<<LineEnd>>', '<<SelectPrevWord>>', '<<PasteSelection>>', '<<SelectNone>>', '<<PrevChar>>')

                    

