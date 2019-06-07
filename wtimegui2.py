#!/usr/bin/env python
#
# wtimegui - Working time class with GUI
#
import sys
import time
try:
    from Tkinter import *
    import ttk
    import tkMessageBox
except ModuleNotFoundError:
    from tkinter import *
    from tkinter import ttk
    from tkinter import messagebox as tkMessageBox
from wtime3 import wtime

__author__ = "Riccardo Bruno"
__copyright__ = "2017"
__license__ = "Apache"
__maintainer__ = "Riccardo Bruno"
__email__ = "riccardo.bruno@gmail.com"


class wtimeGUI:

    flag_ticket_reached = False
    flag_time_reached = False
    flag_thread_running = False
    interval_thread_waitcycles = 5
    check_time_thread=None
    wtime_out = None

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



    def __init__(self):

        self.t1,self.t2,self.t3,self.t4 = wtime.getTimes("wtime3")
        self.wt = wtime(t1=self.t1,t2=self.t2,t3=self.t3,t4=self.t4)
        wtime_out = self.wt.calc2()
        self.wt.printout(wtime_out)

        #style = ttk.Style()
        #style.configure('wt.Horizontal.TProgressbar', fieldbackground='maroon')
        #style.map("Horizontal.TProgressbar",fieldbackground=[("active", "black"), ("disabled", "red")])
        self.pbarTime = ttk.Progressbar(self.root, orient=HORIZONTAL, length=64, mode='determinate')
        self.pbarTicket = ttk.Progressbar(self.root, orient=HORIZONTAL, length=64, mode='determinate')
        self.gui_build()
        self.root.bind('<Return>',self.btnRecalc)
        self.root.bind('<space>',self.btnRecalc)
        self.root.bind('<Escape>',self.btnExit)
        self.root.lift ()
        self.root.protocol("WM_DELETE_WINDOW", self.btnExit)
        self.root.call('wm', 'attributes', '.', '-topmost', True)
        self.root.after_idle(self.root.call, 'wm', 'attributes', '.', '-topmost', False)
        self.gui_update(wtime_out)
        self.root.after(1000, self.time_check)
        self.counter=0

    def time_check(self):
        if self.wt is not None and self.counter % self.interval_thread_waitcycles == 0:
            wtime_out = self.wt.calc2()
            self.gui_update(wtime_out)
            #self.wt.printout(wtime_out)
            if wtime_out.get("overtime", None) is not None and self.flag_time_reached == False:
                print("You've DONE!!!")
                self.flag_time_reached = True
                flag_thread_running = False
                gui.show_message_box("You've DONE!!!")
            elif wtime_out["ticket remaining"] == "reached" and flag_ticket_reached == False:
                print("Ticket reached!!!")
                flag_ticket_reached = True
                gui.show_message_box("Ticket reached!!!")
        self.counter+=1
        self.root.after(1000, self.time_check)

    def btnExit(self, *args):
        global flag_thread_running
        flag_thread_running = False
        self.root.destroy()
        sys.exit(0)

    def btnRecalc(self, *args):
        wtime_out = self.wt.calc2()
        self.wt.printout(wtime_out)
        self.gui_update(wtime_out)

    def gui_update(self, out):
        self.T1Content.set(out["t1"])
        self.T2Content.set(out["t2"])
        self.T2T1Content.set(out["t2t1"])
        self.T3Content.set(out["t3"])
        self.T4Content.set(out["t4"])
        self.T4T3Content.set(out["t4t3"])
        self.PauseTimeContent.set(out["pause time"])
        self.TotalTimeContent.set(out.get("total time",""))
        self.TimeToReachContent.set(out.get("time to reach",""))
        self.TimeRemainingContent.set(out.get("time remaining","reached"))
        self.TimeRemainingAtContent.set(out.get("time remaining at",""))
        self.TicketRemainContent.set(out["ticket remaining"])
        self.TicketRemainAtContent.set(out.get("ticket remaining at",""))
        self.TicketTimeContent.set(out["ticket time"])
        self.pbarTime["value"] = out["time remaining perc"]
        self.pbarTicket["value"] = out["ticket remaining perc"]
        self.TimePercentage.set("%2d %%" % out["time remaining perc"])
        self.TicketPercentage.set("%2d %%" % out["ticket remaining perc"])

    def gui_build(self):
            GUI = ( 
               {"label": self.T1Text,
                "label content": self.T1Content,
                "row": 0,
                "column": 0},
               {"label": self.T2Text,
                "label content": self.T2Content,
                "row": 1,
                "column": 0},
               {"label": self.T2T1Text,
                "label content": self.T2T1Content,
                "row": 1,
                "column": 2},
               {"label": self.T3Text,
                "label content": self.T3Content,
                "row": 2,
                "column": 0},
               {"label": self.T4Text,
                "label content": self.T4Content,
                "row": 3,
                "column": 0},
               {"label": self.T4T3Text,
                "label content": self.T4T3Content,
                "row": 3,
                "column": 2},
               {"label": self.PauseTimeText,
                "label content": self.PauseTimeContent,
                "row": 4,
                "column": 0},
               {"label": self.TotalTimeText,
                "label content": self.TotalTimeContent,
                "row": 5,
                "column": 0},
               {"label": self.TimeToReachText,
                "label content": self.TimeToReachContent,
                "row": 6,
                "column": 0},
               {"label": self.TimeRemainingText,
                "label content": self.TimeRemainingContent,
                "row": 7,
                "column": 0},
               {"label": self.TimeRemainingAtText,
                "label content": self.TimeRemainingAtContent,
                "row": 8,
                "column": 0},
               {"label": self.TicketRemainText,
                "label content": self.TicketRemainContent,
                "row": 9,
                "column": 0},
               {"label": self.TicketRemainAtText,
                "label content": self.TicketRemainAtContent,
                "row": 10,
                "column": 0},
               {"label": self.TicketTimeContent,
                "label content": self.TicketTimeContent,
                "row":11,
                "column": 0},
               {"label": self.TimePercentage,
                "label content": None,
                "row": 7,
                "column": 2},
               {"label": self.TicketPercentage,
                "label content": None,
                "row": 9,
                "column": 2},
            )
            for gui_element in GUI:
                Label(self.root,
                    textvariable=gui_element["label"],
                    text=gui_element["label"],
                    font=self.lblFONT,
                    fg=self.lblFGCOLOR).grid(row=gui_element["row"],
                                        column=gui_element["column"])
                if gui_element["label content"] is not None:
                    Label(self.root,
                          textvariable = gui_element["label content"],
                          text=gui_element["label content"],
                          font=self.lblFONT, fg=self.lblFGCOLOR).grid(row=gui_element["row"],
                                                            column=gui_element["column"]+1)
            self.pbarTime.grid(row=7,column=3)
            self.pbarTicket.grid(row=9,column=3)
            Button(self.root, text="Exit", command=self.btnExit).grid(row=12,column=3)
            Button(self.root, text="Recalc", command=self.btnRecalc).grid(row=12,column=1)

    def show_message_box(self, message):
        self.root.attributes("-topmost", True)
        tkMessageBox.showinfo("wtimegui", message,parent=self.root)
        self.root.attributes("-topmost", False)

def check_time(*args):
    gui=args[0]
    if gui is None:
        print("ERROR: No GUI object received")
        return
    t = current_thread()
    while gui.flag_thread_running:
        for i in range(1, gui.interval_thread_waitcycles):
            time.sleep(1)
        q.put(1)

if __name__ == "__main__":
    gui = wtimeGUI()
    gui.root.mainloop()



