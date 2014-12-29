#!/usr/bin/python3
import tkinter as tk
from view.app import *

def _get_geometry(tl_obj):
    return map(int, re.split('[x+]',tl_obj.geometry()))

root = tk.Tk()
app = AlienArenaApp(root)
root.wait_visibility(root)
(w,h,x,y) = _get_geometry(root)
root.geometry('%dx%d+%d+%d' % (w,h,(app.ws-w)/2,(app.hs-h)/2))
app.run()
