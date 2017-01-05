#!/usr/bin/env python
#
# wtimegui - Working time class with GUI
#
import sys
from Tkinter import *
from wtime3 import wtime

T1Content = '09:28:00'
T2Content = '11:53:19'
T2T1Content = '02:25:19'
T3Content = '11:53:19'
T4Content = '11:53:19'
T4T3Content = '00:00:00'
PauseTimeContent = '00:30:00'
TotalTimeContent = '01:55:19'
TimeToReachContent = '07:12:00'
TimeRemainingContent = '05:16:41'
TimeRemainingAtContent = '17:10:00'
TicketRemainContent = '04:04:41'
TicketRemainAtContent = '15:58:00'
TicketTimeContent = '06:30:00'

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

def btnExit():
    sys.exit(0)

def btnRecalc():
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
    TotalTimeContent.set(out["total time"])
    TimeToReachContent.set(out["time to reach"])
    TimeRemainingContent.set(out["time remaining"])
    TimeRemainingAtContent.set(out["time remaining at"])
    TicketRemainContent.set(out["ticket remaining"])
    TicketRemainAtContent.set(out["ticket remaining at"])
    TicketTimeContent.set(out["ticket time"])

if __name__ == "__main__":
    t1,t2,t3,t4 = wtime.getTimes("wtime3")
    wt = wtime(t1=t1,t2=t2,t3=t3,t4=t4)
    out = wt.calc2()
    wt.printout(out)
    
    gui_update(out)        
    GUI = ( 
	   {"label": "T1 :", 
		"label content": T1Content,
		"row": 0,
		"column": 0},
	   {"label": "T2 :",
		"label content": T2Content,
		"row": 1,
		"column": 0},
	   {"label": "T2-T1 :",
		"label content": T2T1Content,
		"row": 1,
		"column": 2},
	   {"label": "T3 :",
		"label content": T3Content,
		"row": 2,
		"column": 0},
	   {"label": "T4 :",
		"label content": T4Content,
		"row": 3,
		"column": 0},
	   {"label": "T4-T3 :",
		"label content": T4T3Content,
		"row": 3,
		"column": 2},
	   {"label": "Pause Time :",
		"label content": PauseTimeContent,
		"row": 4,
		"column": 0},
	   {"label": "Total Time :",
		"label content": TotalTimeContent,
		"row": 5,
		"column": 0},
	   {"label": "Time to reach :",
		"label content": TimeToReachContent,
		"row": 6,
		"column": 0},
	   {"label": "Time remaining :",
		"label content": TimeRemainingContent,
		"row": 7,
		"column": 0},
	   {"label": "at :",
		"label content": TimeRemainingAtContent,
		"row": 8,
		"column": 0},
	   {"label": "Ticket remain :",
		"label content": TicketRemainContent,
		"row": 9,
		"column": 0},
	   {"label": " at :",
		"label content": TicketRemainAtContent,
		"row": 10,
		"column": 0},
	   {"label": "Ticket time :",
		"label content": TicketTimeContent,
		"row":11,
		"column": 0},
    )
    
    for gui_element in GUI:
	    Label(root, text=gui_element["label"], font=lblFONT, fg=lblFGCOLOR).grid(row=gui_element["row"], column=gui_element["column"])
	    Label(root, textvariable = gui_element["label content"], text=gui_element["label content"], font=lblFONT, fg=lblFGCOLOR).grid(row=gui_element["row"], column=gui_element["column"]+1)
    Button(root, text="Exit", command=btnExit).grid(row=12,column=3)
    Button(root, text="Recalc", command=btnRecalc).grid(row=12,column=1)

    root.mainloop()

