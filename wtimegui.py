#!/usr/bin/env python3
"""
wtimegui - Tkinter GUI on top of wtimecore.wtime.

Not meant to parse the command line itself: wtimecli.py builds a wtimeGUI
instance with explicit t1..t4/current_time. Running this file directly opens
the GUI with no clockings prefilled (only useful for a quick UI smoke test).
"""
import datetime as dt
from tkinter import *
from tkinter import ttk
from tkinter import messagebox

from wtimecore import wtime

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

    winTITLE = "wtime GUI"
    lblFONT = ("Lucida Grande", 12)
    lblFGCOLOR = 'black'

    root = None

    # Rows are grouped by topic: clockings, then the whole time block, then
    # the whole ticket block, then the buttons - instead of interleaving
    # time and ticket rows.
    GUI_data = (
        # clockings
        {"type": "text", "name": "t1", "title": "T1", "row": 0, "col": 0},
        {"type": "text", "name": "t2", "title": "T2", "row": 1, "col": 0},
        {"type": "text", "name": "t2t1", "title": "T2 - T1", "row": 1, "col": 2},
        {"type": "text", "name": "t3", "title": "T3", "row": 2, "col": 0},
        {"type": "text", "name": "t4", "title": "T4", "row": 3, "col": 0},
        {"type": "text", "name": "t4t3", "title": "T4 - T3", "row": 3, "col": 2},
        {"type": "text", "name": "pause time", "title": "Pause Time", "row": 4, "col": 0},
        # ticket block
        {"type": "text", "name": "ticket remaining", "title": "Ticket remain", "row": 5, "col": 0},
        {"type": "text", "name": "ticket remaining at", "title": "at", "row": 6, "col": 0},
        {"type": "text", "name": "ticket remaining perc", "title": "%", "row": 6, "col": 2},
        {"type": "progress", "name": "ticket progress", "title": "Ticket progress", "row": 6, "col": 3},
        {"type": "text", "name": "ticket time", "title": "TicketTime", "row": 7, "col": 0},
        # time block
        {"type": "text", "name": "total time", "title": "Total Time", "row": 8, "col": 0},
        {"type": "text", "name": "overtime", "title": "Over Time", "row": 8, "col": 2},
        {"type": "text", "name": "time to reach", "title": "Time to reach", "row": 9, "col": 0},
        {"type": "text", "name": "time remaining", "title": "Time remain", "row": 10, "col": 0},
        {"type": "text", "name": "time remaining at", "title": "at", "row": 11, "col": 0},
        {"type": "text", "name": "time remaining perc", "title": "%", "row": 11, "col": 2},
        {"type": "progress", "name": "time progress", "title": "Time progress", "row": 11, "col": 3},
        # buttons
        {"type": "button", "name": "Tx", "title": "T2", "row": 12, "col": 0},
        {"type": "button", "name": "Update", "title": "Update", "row": 12, "col": 1},
        {"type": "button", "name": "Exit", "title": "Exit", "row": 12, "col": 3},
    )

    def get_item(self, type, name):
        for item in self.GUI_data:
            if item["type"] == type and item["name"] == name:
                return item
        return None

    def __init__(self, t1=None, t2=None, t3=None, t4=None, current_time=None):
        self.t1, self.t2, self.t3, self.t4, self.ct = t1, t2, t3, t4, current_time
        self.wt = wtime(t1=self.t1, t2=self.t2, t3=self.t3, t4=self.t4,
                        current_time=self.ct)
        # T1..T4 are anchored to *this* calendar day (see wtimecore.get_datetime).
        # If the window is left open past midnight, recalculating against
        # today's date with yesterday's clockings produces meaningless
        # 24h+ deltas. Remember the day so we can notice and stop instead.
        self.day = dt.date.today()
        self.flag_day_changed = False

        self.root = Tk()
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
        # Position the window flush to the top-right corner, now that its
        # real size is known (doing this before gui_build() anchored the
        # window to the *default* small size, so it grew off-screen to the
        # right once the widgets were added).
        self.root.update_idletasks()
        self.root.geometry("-0+0")
        self.root.bind('<Return>', self.btnUpdate)
        self.root.bind('<space>', self.btnUpdate)
        self.root.bind('<Escape>', self.btnExit)
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
        button = self.get_item("button", "Tx")["button_ctl"]
        if self.t4 is not None:
            button["text"] = "T-"
            button["state"] = DISABLED
        elif self.t3 is not None:
            button["text"] = "T4"
        elif self.t2 is not None:
            button["text"] = "T3"
        else:
            pass

    def is_same_day(self):
        return dt.date.today() == self.day

    def warn_day_changed(self):
        if self.flag_day_changed:
            return
        self.flag_day_changed = True
        self.show_message_box(
            "A new day has started since this window was opened: the "
            "clockings shown are from yesterday, so the figures are no "
            "longer meaningful. Close this window and run wtime again "
            "for today.")

    def check_time(self):
        if not self.is_same_day():
            # Day changed: stop recalculating and leave the last valid
            # (pre-midnight) figures on screen instead of overwriting them
            # with meaningless deltas.
            self.warn_day_changed()
            return
        try:
            self.wtime_out = self.wt.calc2()
        except Exception as e:
            print(e)
            self.root.destroy()
            return
        self.gui_update()

    def btnTx(self, *args):
        ts = self.wt.now_ts()  # simulated time if -c was given, else real
        if self.t2 is None:
            self.t2 = ts
        elif self.t3 is None:
            self.t3 = ts
        elif self.t4 is None:
            self.t4 = ts
        else:
            return
        if self.ct is not None:
            # Re-anchor the simulated clock at "now": the new wtime object
            # restarts its ticking from the value it's given, so passing the
            # original -c would jump the clock back to where it started.
            self.ct = ts
        self.wt = wtime(t1=self.t1, t2=self.t2, t3=self.t3, t4=self.t4,
                        current_time=self.ct)
        self.update_T_button()
        self.btnUpdate()

    def btnExit(self, *args):
        self.btnUpdate()
        self.root.destroy()

    def btnUpdate(self, *args):
        self.check_time()
        self.wt.printout(self.wtime_out)

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
                if item["name"] in ("ticket remaining", "ticket remaining at",
                                    "time to reach", "time remaining",
                                    "time remaining at", "overtime"):
                    lblFONT_val_style = ("bold",)
                else:
                    lblFONT_val_style = ()
                if item["name"] in ("ticket remaining", "ticket remaining perc",
                                    "time to reach", "time remaining",
                                    "time remaining perc", "overtime"):
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
                                         textvariable=item["value_var"],
                                         text="None",
                                         font=self.lblFONT + lblFONT_val_style,
                                         foreground=self.lblFGCOLOR).grid(row=item["row"],
                                                                  column=item["col"] + 1)
            elif item["type"] == "progress":
                item["progress_ctl"] = ttk.Progressbar(self.root,
                                                       orient=HORIZONTAL,
                                                       length=64,
                                                       mode='determinate')
                item["progress_ctl"].grid(row=item["row"], column=item["col"])
            elif item["type"] == "button":
                if item["title"] == "Exit":
                    callback = self.btnExit
                elif item["title"] == "Update":
                    callback = self.btnUpdate
                elif item["title"][0] == "T":
                    callback = self.btnTx
                else:
                    print("WARNING: Unexpected button named: %s" % item["title"])
                    callback = self.btnUnknown
                item['button_ctl'] = ttk.Button(self.root, text=item["title"], command=callback)
                item['button_ctl'].grid(row=item["row"], column=item["col"])
            else:
                print("WARNING: Skipping unknown type: '%s' for item '%s'"
                      % (item["type"], item["title"]))
        self.update_T_button()

    def gui_update(self):
        for item in self.GUI_data:
            if item["type"] == "text":
                if item["name"] in ("time remaining perc", "ticket remaining perc"):
                    perc = max(0, self.wtime_out.get(item["name"], ""))
                    item["label_var"].set("%2d%%: " % perc)
                elif item["name"] == "total time" and self.wtime_out.get("consume pause") is not None:
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
            elif item["type"] == "button":
                pass
            else:
                print("WARNING: Skipping unknown type: '%s' for item '%s'"
                      % (item["type"], item["title"]))

    def check_time_gui(self):
        if not self.is_same_day():
            # Warn once and stop the periodic loop entirely: nothing more
            # to recompute or notify about once the day has rolled over.
            self.warn_day_changed()
            return
        notify_message = None
        prev_out = "%s" % self.wtime_out
        self.check_time()
        if "overtime" in self.wtime_out and not self.flag_time_reached:
            print(prev_out + " -> %s" % self.wtime_out)
            notify_message = "You've DONE!!!"
            self.flag_time_reached = True
            self.flag_ticket_reached = True
        elif self.wtime_out["ticket remaining"] == "reached" and not self.flag_ticket_reached:
            print(prev_out + " -> %s" % self.wtime_out)
            notify_message = "Ticket reached!!!"
            self.flag_ticket_reached = True
        if notify_message is not None:
            print(notify_message)
            self.show_message_box(notify_message)
            notify_message = None
        self.root.after(self.check_interval, self.check_time_gui)


if __name__ == "__main__":
    wtimeGUI()
