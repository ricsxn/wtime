#/usr/bin/env python3
#
# wtimegui - Working time class with GUI
#
import sys
import time
from tkinter import *
from tkinter import ttk
from tkinter import messagebox

from wtime4 import wtime


__author__ = "Riccardo Bruno"
__copyright__ = "2017"
__license__ = "Apache"
__maintainer__ = "Riccardo Bruno"
__email__ = "riccardo.bruno@gmail.com"


class wtimeGUI:
    
    theme_name = None 

    flag_ticket_reached = False
    flag_time_reached = False
    check_interval = 5000
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
        {"type": "text", "name": "ticket remaining", "title": "Ticket remain", "row": 7, "col": 0},
        {"type": "text", "name": "ticket remaining at", "title": "at", "row": 8, "col": 0},
        {"type": "text", "name": "ticket time", "title": "TicketTime", "row": 9, "col": 0},
        {"type": "text", "name": "ticket remaining perc", "title": "%", "row": 8, "col": 2},
        {"type": "progress", "name": "ticket progress", "title": "Ticket progress", "row": 8, "col": 3},
        {"type": "text", "name": "time remaining", "title": "Time remain", "row": 10, "col": 0},
        {"type": "text", "name": "time remaining at", "title": "at", "row": 11, "col": 0},
        {"type": "text", "name": "time remaining perc", "title": "%", "row": 11, "col": 2},
        {"type": "progress", "name": "time progress", "title": "Time progress", "row": 11, "col": 3},
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
        self.root.geometry("-0+0")
        self.root.title(self.winTITLE)
        
        self.menu = Menu(self.root)
        self.root.config(menu=self.menu)
        self.file_menu = Menu(self.menu)
        self.menu.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="Exit", command=self.btnExit)
        self.help_menu = Menu(self.menu)
        self.menu.add_cascade(label="Help", menu=self.help_menu)
        self.help_menu.add_command(label="About", command=self.about)
        
        
        self.gui_build()
        self.check_time()
        self.root.bind('<Return>',self.btnUpdate)
        self.root.bind('<space>',self.btnUpdate)
        self.root.bind('<Escape>',self.btnExit)
        self.root.lift()
        self.root.protocol("WM_DELETE_WINDOW", self.btnExit)
        self.root.call('wm', 'attributes', '.', '-topmost', True)        
        self.root.after_idle(self.root.call, 'wm', 'attributes', '.', '-topmost', False)
        self.root.after(self.check_interval, self.check_time_gui)
        self.root.mainloop()

    def about(self):
        self.root.attributes("-topmost", True)
        messagebox.showinfo(self.winTITLE, "wtimeGUI by Riccardo Bruno", parent=self.root)
        self.root.attributes("-topmost", False)

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
        try:
            self.wtime_out = self.wt.calc2()
        except Exception as e:
            print(e)
            self.root.destroy()
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
        self.root.destroy()

    def btnUpdate(self, *args):
        self.check_time()
        self.wt.printout(self.wtime_out)
        #print(self.wtime_out)

    def btnUnknown(self, *args):
        print("WARNING: Unknown button pressed")

    def show_message_box(self, message):
        self.root.attributes("-topmost", True)
        messagebox.showinfo(self.winTITLE, message, parent=self.root)
        self.root.attributes("-topmost", False)

    def gui_build(self):
        self.style = ttk.Style(self.root)
        self.theme = self.style.theme_use(self.theme_name)
        for item in self.GUI_data:
            if item["type"] == "text":
                if item["name"] in ("ticket remaining",
                                    "ticket remaining at",
                                    "time remaining",
                                    "time remaining at",
                                    "overtime"):
                    lblFONT_val_style = ("bold",)
                else:
                    lblFONT_val_style = ()
                if item["name"] in ("ticket remaining",
                                    "ticket remaining perc",
                                    "time remaining",
                                    "time remaining perc",
                                    "overtime"):
                    lblFONT_lbl_style = ("bold",)
                else:
                    lblFONT_lbl_style = ()
                item["label_var"] = StringVar(self.root, "")
                item["value_var"] = StringVar(self.root, "")
                item["label_ctl"] = ttk.Label(self.root,
                                          textvariable=item["label_var"],
                                          text="None",
                                          font=self.lblFONT + lblFONT_lbl_style,
                                          foreground=self.lblFGCOLOR).grid(row=item["row"],
                                                                   column=item["col"])
                item["value_ctl"] = ttk.Label(self.root,
                                         textvariable = item["value_var"],
                                         text="None",
                                         font=self.lblFONT + lblFONT_val_style,
                                         foreground=self.lblFGCOLOR).grid(row=item["row"],
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
                item['button_ctl'] = ttk.Button(self.root,
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
                    value = self.wtime_out.get(item["name"], "")
                    if value != "":
                        item["label_var"].set(item["title"] + " :")
                        item["value_var"].set(value)
                    else:
                        item["label_var"].set("")
                        item["value_var"].set("")
            elif item["type"] == "progress":
                if item["name"] == "time progress":
                    item["progress_ctl"]["value"] = self.wtime_out["time remaining perc"]
                elif item["name"] == "ticket progress":
                    item["progress_ctl"]["value"] = self.wtime_out["ticket remaining perc"]
                else:
                    pass
            elif item["type"] == "button":
                pass
            else:
                print("WARNING: Skipping unknown type: '%s' for item '%s'"
                        % (item["type"], item["title"]))
    
    def check_time_gui(self):
        notify_message = None        
        # Update working time values
        prev_out = "%s" %self.wtime_out
        self.check_time()
        # Check for ticket and time done
        if self.wtime_out["time to reach"] == "reached" and not self.flag_time_reached:
            print(prev_out + " -> %s" % self.wtime_out)
            notify_message = "You've DONE!!!"
            self.flag_time_reached = True
            self.flag_ticket_reached = True
        elif self.wtime_out["ticket remaining"] == "reached" and not self.flag_ticket_reached:
            print(prev_out + " -> %s" % self.wtime_out)
            notify_message = "Ticket reached!!!"
            self.flag_ticket_reached = True
        # Notify message if needed
        if notify_message is not None:
            print(notify_message)
            self.show_message_box(notify_message)
            #self.gui_build()
            notify_message = None        
        self.root.after(self.check_interval, self.check_time_gui)

if __name__ == "__main__":
    gui = wtimeGUI()

