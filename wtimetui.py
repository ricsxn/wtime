#!/usr/bin/env python3
"""
wtimetui - curses-based terminal UI on top of wtimecore.wtime.

Same building blocks as wtimegui.py (clockings, ticket block, time block)
and the same day-rollover guard, but drawn in a plain terminal via `curses`
(the standard-library module vi/vim, top, htop are built on) instead of
Tkinter - nothing extra to install.

Keys: [t] mark next clocking (T2/T3/T4)  [u] refresh now  [q] quit
"""
import curses
import datetime as dt

from wtimecore import wtime

__author__ = "Riccardo Bruno"
__copyright__ = "2017"
__license__ = "Apache"
__maintainer__ = "Riccardo Bruno"
__email__ = "riccardo.bruno@gmail.com"

REFRESH_SECONDS = 5
BAR_WIDTH = 20


class wtimeTUI:

    def __init__(self, t1=None, t2=None, t3=None, t4=None, current_time=None):
        self.t1, self.t2, self.t3, self.t4, self.ct = t1, t2, t3, t4, current_time
        self.wt = wtime(t1=self.t1, t2=self.t2, t3=self.t3, t4=self.t4,
                        current_time=self.ct)
        # Same day-rollover guard as wtimegui.py: T1..T4 are anchored to
        # today's date, so recalculating after midnight would be meaningless.
        self.day = dt.date.today()
        self.day_changed_warned = False

        self.out = {}
        self.status = ""
        self.last_update = None
        self.flag_time_reached = False
        self.flag_ticket_reached = False
        self.has_color = False  # set in run(), if the terminal supports it

    # ---------- state -------------------------------------------------

    def is_same_day(self):
        return dt.date.today() == self.day

    def mark_next(self):
        if not self.is_same_day():
            return
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

    def update(self):
        if not self.is_same_day():
            if not self.day_changed_warned:
                self.day_changed_warned = True
                self.status = ("New day since this session started: figures "
                               "are frozen (from yesterday). Quit and run "
                               "wtime again for today.")
            return
        try:
            self.out = self.wt.calc2()
        except Exception as e:
            self.status = "ERROR: %s" % e
            return
        self.last_update = dt.datetime.now()
        if "overtime" in self.out and not self.flag_time_reached:
            self.flag_time_reached = True
            self.flag_ticket_reached = True
            self.status = "You've DONE!!!"
        elif self.out.get("ticket remaining") == "reached" and not self.flag_ticket_reached:
            self.flag_ticket_reached = True
            self.status = "Ticket reached!!!"

    # ---------- rendering -----------------------------------------------

    @staticmethod
    def bar(perc, width=BAR_WIDTH):
        try:
            perc = max(0, min(100, perc))
        except TypeError:
            perc = 0
        filled = int(width * perc / 100)
        return "[%s%s] %3d%%" % ("#" * filled, "-" * (width - filled), perc)

    def render(self, stdscr):
        stdscr.erase()
        height, width = stdscr.getmaxyx()
        row = 0

        def line(text="", bold=False, alert=False):
            nonlocal row
            if row >= height - 1:
                return
            attr = curses.A_BOLD if (bold or alert) else curses.A_NORMAL
            if alert and self.has_color:
                attr |= curses.color_pair(1)  # bold white - makes the
                                              # "reached" notifications and
                                              # the day-changed warning stand out
            try:
                stdscr.addstr(row, 0, text[:max(width - 1, 0)], attr)
            except curses.error:
                pass  # terminal too small for this row/col; skip silently
            row += 1

        out = self.out
        line("wtime   [t] mark clocking  [u] refresh  [q] quit", bold=True)
        line("-" * max(width - 1, 0))

        if 'error' in out:
            line(out['error'])
        else:
            line("T1: %-10s T2: %-10s T2-T1: %s" %
                 (out.get('t1', '--'), out.get('t2', '--'), out.get('t2t1', '--')))
            line("T3: %-10s T4: %-10s T4-T3: %s" %
                 (out.get('t3', '--'), out.get('t4', '--'), out.get('t4t3', '--')))
            line("Pause time    : %s" % out.get('pause time', '--'))
            line()

            line("-- Ticket " + "-" * max(width - 11, 0))
            line("Ticket remain : %s" % out.get('ticket remaining', '--'), bold=True)
            if 'ticket remaining at' in out:
                line("         at   : %s" % out['ticket remaining at'], bold=True)
            line("Ticket time   : %s" % out.get('ticket time', '--'))
            line(self.bar(out.get('ticket remaining perc', 0)))
            line()

            line("-- Time " + "-" * max(width - 9, 0))
            consuming = out.get('consume pause')
            if consuming is None:
                line("Total time    : %s" % out.get('total time', '--'))
            else:
                line("Consume pause : %s to go" % consuming)
            if 'overtime' in out:
                line("Over time     : %s" % out['overtime'])
            line("Time to reach : %s" % out.get('time to reach', '--'), bold=True)
            line("Time remain   : %s" % out.get('time remaining', '--'), bold=True)
            line("         at   : %s" % out.get('time remaining at', '--'), bold=True)
            line(self.bar(out.get('time remaining perc', 0)))

        line()
        line("-" * max(width - 1, 0))
        # Status line in two differently-styled parts: the timestamp stays
        # plain, only the message (if any) is highlighted - "updated HH:MM:SS
        # - You've DONE!!!" rather than bolding the whole line.
        if row < height - 1:
            stamp = None
            if self.last_update is not None:
                stamp = "updated %s" % self.last_update.strftime("%H:%M:%S")
            col = 0
            if stamp:
                try:
                    stdscr.addstr(row, col, stamp[:max(width - 1, 0)], curses.A_NORMAL)
                except curses.error:
                    pass
                col += len(stamp)
            if self.status:
                msg = (" - " if stamp else "") + self.status
                attr = curses.A_BOLD
                if self.has_color:
                    attr |= curses.color_pair(1)
                try:
                    stdscr.addstr(row, col, msg[:max(width - 1 - col, 0)], attr)
                except curses.error:
                    pass
            row += 1
        stdscr.refresh()

    # ---------- main loop -----------------------------------------------

    def run(self, stdscr):
        curses.curs_set(0)
        try:
            curses.start_color()
            curses.use_default_colors()
            curses.init_pair(1, curses.COLOR_WHITE, -1)
            self.has_color = True
        except curses.error:
            pass  # terminal has no color support: alert lines just stay bold
        stdscr.timeout(REFRESH_SECONDS * 1000)  # getch() doubles as the refresh tick
        self.update()
        while True:
            self.render(stdscr)
            ch = stdscr.getch()
            if ch in (ord('q'), ord('Q')):
                break
            elif ch in (ord('t'), ord('T')):
                self.mark_next()
                self.update()
            elif ch in (ord('u'), ord('U')):
                self.update()
            elif ch == -1:
                self.update()  # timeout tick: this is the periodic refresh
            # curses.KEY_RESIZE: just loop and re-render with current self.out


def main(t1=None, t2=None, t3=None, t4=None, current_time=None):
    tui = wtimeTUI(t1=t1, t2=t2, t3=t3, t4=t4, current_time=current_time)
    curses.wrapper(tui.run)


if __name__ == "__main__":
    main()
