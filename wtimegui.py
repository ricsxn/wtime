#!/usr/bin/env python
#
# wtimegui - Working time class with GUI
#
import sys
import time
from Tkinter import *
from threading import *
from wtime3 import wtime
import ttk
import tkMessageBox


__author__ = "Riccardo Bruno"
__copyright__ = "2017"
__license__ = "Apache"
__maintainer__ = "Riccardo Bruno"
__email__ = "riccardo.bruno@gmail.com"

flag_ticket_reached = False
flag_time_reached = False
flag_thread_running = False
interval_thread_waitcycles = 5
t=None

winTITLE="wtime GUI"
lblFONT=("Lucida Grande", 12)
lblFGCOLOR='black'

root = Tk()
root.title(winTITLE)

T1Content = StringVar()
T2Content = StringVar()
T2T1Content = StringVar()
T3Content = StringVar()
T4Content = StringVar()
T4T3Content = StringVar()
PauseTimeContent = StringVar()
TotalTimeContent = StringVar()
TimeToReachContent = StringVar()
TimeRemainingContent = StringVar()
TimeRemainingAtContent = StringVar()
TicketRemainContent = StringVar()
TicketRemainAtContent = StringVar()
TicketTimeContent = StringVar()
TimePercentage = StringVar()
TicketPercentage = StringVar()

T1Text = StringVar()
T2Text = StringVar()
T2T1Text = StringVar()
T3Text = StringVar()
T4Text = StringVar()
T4T3Text = StringVar()
PauseTimeText = StringVar()
TotalTimeText = StringVar()
TimeToReachText = StringVar()
TimeRemainingText = StringVar()
TimeRemainingAtText = StringVar()
TicketRemainText = StringVar()
TicketRemainAtText = StringVar()
TicketTimeText = StringVar()

T1Text = "T1 :"
T2Text = "T2 :"
T2T1Text = "T2 - T1 :"
T3Text = "T3 :"
T4Text = "T4 :"
T4T3Text = "T4 - T3 :"
PauseTimeText = "Pause Time :"
TotalTimeText = "Total Time :"
TimeToReachText = "Time to reach :"
TimeRemainingText = "Time remain :"
TimeRemainingAtText = "at :"
TicketRemainText = "Ticket remain :"
TicketRemainAtText = "at :"
TicketTimeText = "Ticket time :"


#style = ttk.Style()
#style.configure('wt.Horizontal.TProgressbar', fieldbackground='maroon')
#style.map("Horizontal.TProgressbar",fieldbackground=[("active", "black"), ("disabled", "red")])
pbarTime = ttk.Progressbar(root, orient=HORIZONTAL, length=64, mode='determinate')
pbarTicket = ttk.Progressbar(root, orient=HORIZONTAL, length=64, mode='determinate')

def btnExit(*args):
    global flag_thread_running
    flag_thread_running = False
    root.destroy()
    sys.exit(0)

def btnRecalc(*args):
    wt = wtime(t1=t1,t2=t2,t3=t3,t4=t4)
    out = wt.calc2()
    wt.printout(out)
    gui_update(out)

def gui_update(out):
    T1Content.set(out["t1"])
    T2Content.set(out["t2"])
    T2T1Content.set(out["t2t1"])
    T3Content.set(out["t3"])
    T4Content.set(out["t4"])
    T4T3Content.set(out["t4t3"])
    PauseTimeContent.set(out["pause time"])
    TotalTimeContent.set(out.get("total time",""))
    TimeToReachContent.set(out.get("time to reach",""))
    TimeRemainingContent.set(out.get("time remaining","reached"))
    TimeRemainingAtContent.set(out.get("time remaining at",""))
    TicketRemainContent.set(out["ticket remaining"])
    TicketRemainAtContent.set(out.get("ticket remaining at",""))
    TicketTimeContent.set(out["ticket time"])
    pbarTime["value"] = out["time remaining perc"]
    pbarTicket["value"] = out["ticket remaining perc"]
    TimePercentage.set("%2d %%" % out["time remaining perc"])
    TicketPercentage.set("%2d %%" % out["ticket remaining perc"])
    
def checkTime():
    global lblTimePerc
    global lblTicketPerc
    global flag_ticket_reached
    global flag_time_reached
    global flag_thread_running
    global interval_thread_waitcycles
    time.sleep(1)
    flag_thread_running = True
    t = currentThread()
    while flag_thread_running:
        if out.get("time remaining perc",100) == 100 and flag_time_reached == False:
            print "You've DONE!!!"
            tkMessageBox.showinfo("wtimegui", "You've DONE!!!",parent=root)
            flag_time_reached = True           
            flag_thread_running = False
            continue
        elif out.get("ticket remaining perc",100) == 100 and flag_ticket_reached == False:
            print "Ticket reached!!!"
            tkMessageBox.showinfo("wtimegui", "Ticket reached!!!",parent=root)
            flag_ticket_reached = True
        btnRecalc()
        for i in range(1,interval_thread_waitcycles):
            if flag_thread_running:
			    time.sleep(1)
            else:
                break


if __name__ == "__main__":
    t1,t2,t3,t4 = wtime.getTimes("wtime3")
    wt = wtime(t1=t1,t2=t2,t3=t3,t4=t4)
    out = wt.calc2()
    wt.printout(out)
    
    gui_update(out)        
    GUI = ( 
       {"label": T1Text,
        "label content": T1Content,
        "row": 0,
        "column": 0},
       {"label": T2Text,
        "label content": T2Content,
        "row": 1,
        "column": 0},
       {"label": T2T1Text,
        "label content": T2T1Content,
        "row": 1,
        "column": 2},
       {"label": T3Text,
        "label content": T3Content,
        "row": 2,
        "column": 0},
       {"label": T4Text,
        "label content": T4Content,
        "row": 3,
        "column": 0},
       {"label": T4T3Text,
        "label content": T4T3Content,
        "row": 3,
        "column": 2},
       {"label": PauseTimeText,
        "label content": PauseTimeContent,
        "row": 4,
        "column": 0},
       {"label": TotalTimeText,
        "label content": TotalTimeContent,
        "row": 5,
        "column": 0},
       {"label": TimeToReachText,
        "label content": TimeToReachContent,
        "row": 6,
        "column": 0},
       {"label": TimeRemainingText,
        "label content": TimeRemainingContent,
        "row": 7,
        "column": 0},
       {"label": TimeRemainingAtText,
        "label content": TimeRemainingAtContent,
        "row": 8,
        "column": 0},
       {"label": TicketRemainText,
        "label content": TicketRemainContent,
        "row": 9,
        "column": 0},
       {"label": TicketRemainAtText,
        "label content": TicketRemainAtContent,
        "row": 10,
        "column": 0},
       {"label": TicketTimeContent,
        "label content": TicketTimeContent,
        "row":11,
        "column": 0},
       {"label": TimePercentage,
        "label content": None,
        "row": 7,
        "column": 2},
       {"label": TicketPercentage,
        "label content": None,
        "row": 9,
        "column": 2},
    )
    
    for gui_element in GUI:
        Label(root, textvariable=gui_element["label"], text=gui_element["label"], font=lblFONT, fg=lblFGCOLOR).grid(row=gui_element["row"], column=gui_element["column"])
        if gui_element["label content"] is not None:
            Label(root, textvariable = gui_element["label content"], text=gui_element["label content"], font=lblFONT, fg=lblFGCOLOR).grid(row=gui_element["row"], column=gui_element["column"]+1)    
    pbarTime.grid(row=7,column=3)
    pbarTicket.grid(row=9,column=3)
    Button(root, text="Exit", command=btnExit).grid(row=12,column=3)
    Button(root, text="Recalc", command=btnRecalc).grid(row=12,column=1)

    root.bind('<Return>',btnRecalc)
    root.bind('<space>',btnRecalc)
    root.bind('<Escape>',btnExit)
    
    t = Thread(target=checkTime, args=())
    t.start()
    root.lift ()
    root.protocol("WM_DELETE_WINDOW", btnExit)
    root.call('wm', 'attributes', '.', '-topmost', True)
    root.after_idle(root.call, 'wm', 'attributes', '.', '-topmost', False)
    root.mainloop()

