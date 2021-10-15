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
    from threading import *
except ImportError:
    from tkinter import *
    from tkinter import ttk
    from threading import *
    from tkinter import messagebox as tkMessageBox

from wtime4 import wtime


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
    wtime_out = {}

    winTITLE="wtime GUI"
    lblFONT=("Lucida Grande", 12)
    lblFGCOLOR='black'

    root = None

    GUI_data = (
        {"type": "text", "name": "t1", "title": "T1", "row": 0, "col": 0},
        {"type": "text", "name": "t2", "title": "T2", "row": 1, "col": 0},
        {"type": "text", "name": "t2t1", "title": "T2 - T1", "row": 1, "col": 2},
        {"type": "text", "name": "t3", "title": "T3", "row": 2, "col": 0},
        {"type": "text", "name": "t4", "title": "T4", "row": 3, "col": 0},
        {"type": "text", "name": "t4t3", "title": "T4 - T3", "row": 3, "col": 2},
        {"type": "text", "name": "pause time", "title": "Pause Time", "row": 4, "col": 0},
        {"type": "text", "name": "total time", "title": "Total Time", "row": 5, "col": 0},
        {"type": "text", "name": "overtime", "title": "Over Time", "row": 5, "col": 2},
        {"type": "text", "name": "time to reach", "title": "Time to reach", "row": 6, "col": 0},
        {"type": "text", "name": "time remaining", "title": "Time remain", "row": 7, "col": 0},
        {"type": "text", "name": "time remaining at", "title": "at", "row": 8, "col": 0},
        {"type": "text", "name": "ticket remaining", "title": "Ticket remain", "row": 9, "col": 0},
        {"type": "text", "name": "ticket remaining at", "title": "at", "row": 10, "col": 0},
        {"type": "text", "name": "ticket time", "title": "TicketTime", "row": 11, "col": 0},
        {"type": "text", "name": "time remaining perc", "title": "%", "row": 7, "col": 2},
        {"type": "text", "name": "ticket remaining perc", "title": "%", "row": 9, "col": 2},
        {"type": "progress", "name": "t1", "title": "Time progress", "row": 7, "col": 3},
        {"type": "progress", "name": "t1", "title": "Ticket progress", "row": 9, "col": 3},
        {"type": "button", "name": "Tx", "title": "T2", "row": 12, "col": 0},
        {"type": "button", "name": "Update", "title": "Update", "row": 12, "col": 1},
        {"type": "button", "name": "Exit", "title": "Exit", "row": 12, "col": 3},
    )

    def get_item(self, type, name):
        item_result = None
        for item in self.GUI_data:
            if item["type"] == type and item["name"] == name:
                item_result = item
                break
        return item_result

    def __init__(self):
        # wtime4
        self.t1, self.t2, self.t3, self.t4, self.ct = wtime.getTimes(sys.argv)
        self.wt = wtime(t1=self.t1, t2=self.t2, t3=self.t3, t4=self.t4, current_time=self.ct)
        # GUI
        self.root = Tk()
        self.root.title(self.winTITLE)
        self.gui_build()
        self.check_time()
        self.root.bind('<Return>',self.btnUpdate)
        self.root.bind('<space>',self.btnUpdate)
        self.root.bind('<Escape>',self.btnExit)
        self.root.lift()
        self.root.protocol("WM_DELETE_WINDOW", self.btnExit)
        self.root.call('wm', 'attributes', '.', '-topmost', True)
        self.root.after_idle(self.root.call, 'wm', 'attributes', '.', '-topmost', False)
        #Thread
        self.check_time_thread = Thread(target=self.check_time_thread, args=(self,))
        self.check_time_thread.start()
        # Main loop
        self.root.mainloop()

    def update_T_button(self):
        button = self.get_item("button","Tx")["button_ctl"]
        if self.t4 is not None:
            button["text"] = "T-"
            button["state"] = DISABLED
        elif self.t3 is not None:
            button["text"] = "T4"
        elif self.t2 is not None:
            button["text"] = "T3"
        else:
            pass

    def check_time(self):
        self.wtime_out = self.wt.calc2()
        self.gui_update()

    def btnTx(self, *args):
        ts = wtime.get_ts()
        if self.t2 is None:
            self.t2 = ts
        elif self.t3 is None:
            self.t3 = ts
        elif self.t4 is None:
            self.t4 = ts
        else:
            return
        self.wt = wtime(t1=self.t1, t2=self.t2, t3=self.t3, t4=self.t4, current_time=self.ct)
        self.update_T_button()
        self.btnUpdate()

    def btnExit(self, *args):
        self.btnUpdate()
        self.flag_thread_running = False
        #Wait for thread completion
        self.check_time_thread.join()
        self.root.destroy()
        sys.exit(0)

    def btnUpdate(self, *args):
        self.check_time()
        self.wt.printout(self.wtime_out)
        #print(self.wtime_out)

    def btnUnknown(self, *args):
        print("WARNING: Unknown button pressed")

    def show_message_box(self, message):
        self.root.attributes("-topmost", True)
        tkMessageBox.showinfo("wtimegui", message,parent=self.root)
        self.root.attributes("-topmost", False)

    def gui_build(self):
        for item in self.GUI_data:
            if item["type"] == "text":
                item["label_var"] = StringVar()
                item["value_var"] = StringVar()
                item["label_ctl"] = Label(self.root,
                                          textvariable=item["label_var"],
                                          text="None",
                                          font=self.lblFONT,
                                          fg=self.lblFGCOLOR).grid(row=item["row"],
                                                                   column=item["col"])
                item["value_ctl"] = Label(self.root,
                                         textvariable = item["value_var"],
                                         text="None",
                                         font=self.lblFONT,
                                         fg=self.lblFGCOLOR).grid(row=item["row"],
                                                                  column=item["col"]+1)
            elif item["type"] == "progress":
                item["progress_ctl"] = ttk.Progressbar(self.root,
                                                       orient=HORIZONTAL,
                                                       length=64,
                                                       mode='determinate')
                item["progress_ctl"].grid(row=item["row"],
                                          column=item["col"])
            elif item["type"] == "button":
                if item["title"] == "Exit":
                    callback = self.btnExit
                elif item["title"] == "Update":
                    callback = self.btnUpdate
                elif item["title"][0] == "T":
                    callback = self.btnTx
                else:
                    print("WARNING: Unhespected button named: %s" % item["title"])
                    callback = self.btnUnknown
                item['button_ctl'] = Button(self.root,
                                            text=item["title"],
                                            command=callback)
                item['button_ctl'].grid(row=item["row"],
                                        column=item["col"])
            else:
              print("WARNING: Skipping unknown type: '%s' for item '%s'"
                    % (item["type"], item["title"]))
        self.update_T_button()

    def gui_update(self):
        for item in self.GUI_data:
            if item["type"] == "text":
                if item["name"] == "time remaining perc" or item["name"] == "ticket remaining perc":
                    perc = max(0, self.wtime_out.get(item["name"],""))
                    item["label_var"].set("%2d%%: " % perc)
                elif item["name"] == "total time" and self.wtime_out.get("consume pause", None) is not None:
                    item["label_var"].set("Consuming pause: ")
                    item["value_var"].set(self.wtime_out["consume pause"])
                else:
                    value = self.wtime_out.get(item["name"],"")
                    if value != "":
                        item["label_var"].set(item["title"] + " :")
                        item["value_var"].set(value)
                    else:
                        pass
            elif item["type"] == "progress":
                item["progress_ctl"]["value"] = self.wtime_out["time remaining perc"]
                item["progress_ctl"]["value"] = self.wtime_out["ticket remaining perc"]
            elif item["type"] == "button":
                pass
            else:
                print("WARNING: Skipping unknown type: '%s' for item '%s'"
                        % (item["type"], item["title"]))

    def check_time_thread(self, *args):
        gui = args[0]
        if gui is None:
            print("ERROR: No GUI passed")
        time.sleep(.1)
        try:
            t = currentThread()
        except NameError as e:
            t = current_thread()
            print("wtime updating thread started")
            self.flag_thread_running = True
            while self.flag_thread_running:
                overtime = self.wtime_out.get("overtime", None)
                if overtime is not None and self.flag_time_reached == False:
                    print("You've DONE!!!")
                    self.flag_time_reached = True
                    gui.show_message_box("You've DONE!!!")
                elif overtime is not None and self.flag_time_reached == True:
                    self.TotalTimeText = "Overtime: "
                    self.gui_build()
                elif self.wtime_out["ticket remaining"] == "reached" and self.flag_ticket_reached == False:
                    print("Ticket reached!!!")
                    self.flag_ticket_reached = True
                    gui.show_message_box("Ticket reached!!!")
                self.check_time()
                for i in range(1,10 * self.interval_thread_waitcycles):
                    if self.flag_thread_running:
                        time.sleep(.1)
                    else:
                        break
        except Exception as e:
            print("Exception: %s" % type(e).__name__ )
            print("wtime updating thread not started: %s" % e)
        print("wtime updating thread terminated")

if __name__ == "__main__":
    gui = wtimeGUI()


