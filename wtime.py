#!/usr/bin/env python3
"""
wtime - Working time tracker (INFN, research staff levels I-III / technologist)

Encoded rules (national research CCNL, unless overridden by a local agreement):
  - daily working time due: 7h12m (36h per week over 5 days)
  - "virtual" pause when no pause is clocked: 30 minutes (deducted from worked time)
  - if the pause is clocked (T2/T3), the real interval is used
  - meal ticket: requires net work > 6h *and* a real pause of at least 30
    minutes (art. 5 paragraphs 2 and 10, CCNL 1998/2001). A clocked pause
    shorter than the minimum does NOT grant the meal ticket, even if net
    work exceeds 6h.

All values below are specific to the section/local agreement: check them with
your section's staff office before blindly trusting the defaults.
"""
import os
import sys
import datetime as dt

__author__ = "Riccardo Bruno"
__copyright__ = "2017"
__license__ = "Apache"
__maintainer__ = "Riccardo Bruno"
__email__ = "riccardo.bruno@gmail.com"

# =========================================================================
# CONFIGURATION - the only place to edit to adapt the script to a different
# INFN section or local regulation.
# =========================================================================

# Daily working time due (36h per week / 5 days)
WORK_DURATION = dt.timedelta(hours=7, minutes=12)

# "Virtual" pause applied when the pause is not clocked (T2/T3 missing):
# it is deducted as a flat amount from the worked time.
DEFAULT_PAUSE = dt.timedelta(minutes=30)

# Minimum NET work (pause excluded) required for the meal ticket.
# Fixed: the CCNL does not make it depend on the real pause length.
TICKET_MIN_WORK = dt.timedelta(hours=6)

# Minimum length of a clocked pause for the meal ticket to be valid. Usually
# equal to DEFAULT_PAUSE, but kept separate because in some sections the two
# values differ (minimum pause different from the "virtual" one applied when
# nothing is clocked).
TICKET_MIN_PAUSE = dt.timedelta(minutes=30)


def fmt_delta(delay: dt.timedelta) -> str:
    """Format a timedelta as HH:MM:SS (replaces the old printTimeDelta, without
    the fragile str(delay) trick)."""
    total_seconds = int(delay.total_seconds())
    sign = "-" if total_seconds < 0 else ""
    total_seconds = abs(total_seconds)
    h, rem = divmod(total_seconds, 3600)
    m, s = divmod(rem, 60)
    return "%s%02d:%02d:%02d" % (sign, h, m, s)


class wtime:
    """All attributes are per-instance (no shared class-level state)."""

    def __init__(self, **kwargs):
        self.current_time = self.get_datetime(kwargs.get('current_time'))
        self.t1 = self.get_datetime(kwargs.get('t1'))
        self.t2 = self.get_datetime(kwargs.get('t2'))
        self.t3 = self.get_datetime(kwargs.get('t3'))
        self.t4 = self.get_datetime(kwargs.get('t4'))

    # ---------- parsing helpers ---------------------------------------------

    @staticmethod
    def getTsHMS(ts):
        """Parse 'H:M[:S]' -> (h, m, s). Raise ValueError if ts is not valid."""
        if ts is None:
            raise ValueError("timestring is None")
        parts = ts.split(':')
        try:
            h = int(parts[0])
            m = int(parts[1]) if len(parts) > 1 else 0
            s = int(parts[2]) if len(parts) > 2 else 0
        except (IndexError, ValueError):
            raise ValueError("'%s' is not a valid time (expected H:M[:S])" % ts)
        return h, m, s

    @staticmethod
    def get_ts():
        return dt.datetime.now().strftime("%H:%M:%S")

    @staticmethod
    def get_datetime(timestring):
        if timestring is None:
            return None
        h, m, s = wtime.getTsHMS(timestring)
        now = dt.datetime.now()
        return dt.datetime(now.year, now.month, now.day, h, m, s)

    # ---------- calculation -------------------------------------------------

    def calc2(self):
        out = {}
        if self.t1 is None:
            out["error"] = "You must specify at least one time stamp in HH:MM:SS format"
            return out

        now = self.current_time or dt.datetime.now()
        t2 = self.t2 or now
        t3 = self.t3 or now
        t4 = self.t4 or now

        def as_seconds_timedelta(t):
            return dt.timedelta(seconds=t.hour * 3600 + t.minute * 60 + t.second)

        dt1 = as_seconds_timedelta(self.t1)
        dt2 = as_seconds_timedelta(t2)
        dt3 = as_seconds_timedelta(t3)
        dt4 = as_seconds_timedelta(t4)
        dtn = as_seconds_timedelta(now)

        dtw = WORK_DURATION
        dtp = DEFAULT_PAUSE

        dtm = dt2 - dt1   # morning: T2 - T1
        dta = dt4 - dt3   # afternoon: T4 - T3
        did = dt3 - dt2   # real pause: T3 - T2

        out["t1"] = self.t1.strftime("%H:%M:%S")
        out["t2"] = t2.strftime("%H:%M:%S")
        out["t3"] = t3.strftime("%H:%M:%S")
        out["t4"] = t4.strftime("%H:%M:%S")
        out["t2t1"] = fmt_delta(dtm)
        out["t4t3"] = fmt_delta(dta)

        pause_clocked = did > dt.timedelta(seconds=0)

        if pause_clocked:
            out["pause time"] = fmt_delta(did)
            out["total time"] = fmt_delta(dtm + dta)
        else:
            out["pause time"] = fmt_delta(dtp)
            if dtm + dta >= dtp:
                out["total time"] = fmt_delta(dtm + dta - dtp)
            else:
                out["consume pause"] = fmt_delta(dtp - (dtm + dta))

        # time due / overtime. If the pause is not clocked, the default 30'
        # must be added to the working time due (dtw + dtp).
        worked = dtm + dta
        due = dtw if pause_clocked else (dtw + dtp)

        if due > worked:
            out["time to reach"] = fmt_delta(dtw)
            out["time remaining"] = fmt_delta(due - worked)
            out["time remaining at"] = fmt_delta(dt1 + (dt3 - dt2) + due)
            due_sec = due.total_seconds()
            remaining_sec = (due - worked).total_seconds()
            out["time remaining perc"] = 100 * (due_sec - remaining_sec) / due_sec
        else:
            out["overtime"] = fmt_delta(worked - due)
            out["time to reach"] = "reached"
            out["time remaining perc"] = 100

        # meal ticket: a clocked pause (did>0) must be >= the minimum;
        # an unclocked pause is assumed to be the virtual one (DEFAULT_PAUSE),
        # which satisfies the minimum by definition.
        effective_pause = did if pause_clocked else DEFAULT_PAUSE
        pause_valid = effective_pause >= TICKET_MIN_PAUSE

        if not pause_valid:
            out["ticket remaining"] = "pause too short (min %s)" % fmt_delta(TICKET_MIN_PAUSE)
            out["ticket remaining perc"] = 0
        elif worked >= TICKET_MIN_WORK:
            out["ticket remaining"] = "reached"
            out["ticket remaining perc"] = 100
        else:
            out["ticket remaining"] = fmt_delta(TICKET_MIN_WORK - worked)
            out["ticket remaining at"] = fmt_delta(dtn + TICKET_MIN_WORK - worked)
            out["ticket remaining perc"] = 100 * worked.total_seconds() / TICKET_MIN_WORK.total_seconds()
        out["ticket time"] = fmt_delta(TICKET_MIN_WORK)

        return out

    # ---------- CLI -----------------------------------------------------

    def printout(self, out):
        if 'error' in out:
            print(out['error'])
            return 1
        print("-----------------------------------------")
        print(" wtime                                   ")
        print("-----------------------------------------")
        print("T1             : %s" % out["t1"])
        print("T2             : %s T2-T1: %s" % (out["t2"], out["t2t1"]))
        print("T3             : %s" % out["t3"])
        print("T4             : %s T4-T3: %s" % (out["t4"], out["t4t3"]))
        print("Pause time     : %s" % out["pause time"])
        consuming = out.get("consume pause")
        if consuming is None:
            print("Total time     : %s" % out["total time"])
        else:
            print("Consume pause  : %s to go" % consuming)
        overtime = out.get("overtime")
        if overtime is not None:
            print("Overtime       : %s" % overtime)
        else:
            print("Time to reach  : %s" % out["time to reach"])
            print("Time remaining : %s" % out["time remaining"])
            print("            at : %s" % out["time remaining at"])
        if out["ticket remaining"] != "reached":
            print("Ticket remain  : %s" % out["ticket remaining"])
            if "ticket remaining at" in out:
                print("            at : %s" % out["ticket remaining at"])
        print("Ticket time    : %s" % out["ticket time"])
        return 0

    @staticmethod
    def show_usage(wtimecmd):
        print("Usage %s [opts] t1 [[[t2] t3] t4]" % os.path.basename(wtimecmd[0]))
        print("Where tx in the form [H]H:[M]M[:[S]S]")
        print("Options:")
        print("    -h| --help         Print this message")
        print("    -c| --current_time Set a different current time")
        sys.exit(0)

    @staticmethod
    def getTimes(wtimecmd):
        t1 = t2 = t3 = t4 = ct = None
        if len(wtimecmd) <= 1:
            wtime.show_usage(wtimecmd)
        argc = 1
        opt_key = None
        for arg in wtimecmd[1:]:
            if opt_key is not None:
                if opt_key == 'current_time':
                    ct = wtimecmd[argc]
                    opt_key = None
            else:
                if arg[0] == '-':
                    if arg in ('-h', '--help'):
                        wtime.show_usage(wtimecmd)
                    elif arg in ('-c', '--current-time'):
                        opt_key = 'current_time'
                else:
                    break
            argc += 1
        try:
            t1 = wtimecmd[argc + 0]
            t2 = wtimecmd[argc + 1]
            t3 = wtimecmd[argc + 2]
            t4 = wtimecmd[argc + 3]
        except IndexError:
            pass
        return t1, t2, t3, t4, ct


if __name__ == "__main__":
    t1, t2, t3, t4, ct = wtime.getTimes(sys.argv)
    wt = wtime(t1=t1, t2=t2, t3=t3, t4=t4, current_time=ct)
    out = wt.calc2()
    sys.exit(wt.printout(out))
