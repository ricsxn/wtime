#!/usr/bin/env python3
"""
wtimecore - working time calculation library (INFN, research staff levels
I-III / technologist). No CLI, no printing besides printout(): see wtimecli.py
for the command line and wtimegui.py for the Tkinter GUI.

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


def parse_duration(value):
    """Parse 'H:M[:S]' as a plain duration (e.g. hours already worked), not
    a time of day - unlike wtime.get_datetime, this is not anchored to
    today's date."""
    h, m, s = wtime.getTsHMS(value)
    return dt.timedelta(hours=h, minutes=m, seconds=s)


def offsite_remaining(t1, t2, work_duration=WORK_DURATION):
    """Plain `work_duration - (T2 - T1)`, for a day where only the morning is
    badge-clocked and the rest is off-site work (lavoro fuori sede, levels
    I-III): no pause or meal-ticket rule applies here, just the leftover time
    against the daily duration. Returns a timedelta, negative if the morning
    alone already exceeds work_duration."""
    t1_dt = wtime.get_datetime(t1)
    t2_dt = wtime.get_datetime(t2)
    if t1_dt is None or t2_dt is None:
        raise ValueError("both T1 and T2 are required")
    morning = t2_dt - t1_dt
    return work_duration - morning


class wtime:
    """All attributes are per-instance (no shared class-level state)."""

    def __init__(self, **kwargs):
        self.current_time = self.get_datetime(kwargs.get('current_time'))
        # Real instant this object was created: when a simulated current_time
        # is given, the simulated clock starts at that value *now* and keeps
        # ticking from here (see now()).
        self.sim_anchor = dt.datetime.now()
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

    def now(self):
        """Current time for the calculation. Without a simulated current_time
        (-c) this is the real clock. With one, it is a simulated clock that
        starts at that value when the object is created and then advances in
        real time, so a long-running GUI/TUI keeps updating (e.g. overtime
        grows) instead of staying frozen at the -c instant."""
        if self.current_time is None:
            return dt.datetime.now()
        return self.current_time + (dt.datetime.now() - self.sim_anchor)

    def now_ts(self):
        """now() as an HH:MM:SS string."""
        return self.now().strftime("%H:%M:%S")

    # ---------- calculation -------------------------------------------------

    def calc2(self):
        out = {}
        if self.t1 is None:
            out["error"] = "You must specify at least one time stamp in HH:MM:SS format"
            return out

        now = self.now()
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

        # Absolute clock time the threshold is/was reached: start + the real
        # break offset + the net duration due. Valid whether that moment is
        # in the past (already reached) or still ahead, so it's always shown,
        # not just while still counting down.
        due_at = dt1 + (dt3 - dt2) + due
        out["time remaining at"] = fmt_delta(due_at)
        # Like "ticket time" below: the fixed threshold value, always shown -
        # separate from "time remaining", which carries the status (a
        # countdown, or "reached"). Keeping both in "reached" duplicated the
        # same information under two labels.
        out["time to reach"] = fmt_delta(due)

        if due > worked:
            out["time remaining"] = fmt_delta(due - worked)
            due_sec = due.total_seconds()
            remaining_sec = (due - worked).total_seconds()
            out["time remaining perc"] = 100 * (due_sec - remaining_sec) / due_sec
        else:
            out["overtime"] = fmt_delta(worked - due)
            out["time remaining"] = "reached"
            out["time remaining perc"] = 100

        # meal ticket: a clocked pause (did>0) must be >= the minimum;
        # an unclocked pause is assumed to be the virtual one (DEFAULT_PAUSE),
        # which satisfies the minimum by definition.
        effective_pause = did if pause_clocked else DEFAULT_PAUSE
        pause_valid = effective_pause >= TICKET_MIN_PAUSE

        # Like `due` above: when the pause isn't clocked, `worked` is the raw
        # elapsed time since T1 (gross), so the threshold must include the
        # virtual pause too (TICKET_MIN_WORK + DEFAULT_PAUSE), not just the
        # net 6h. Previously this was left flat at TICKET_MIN_WORK in both
        # cases, granting the ticket up to 30' too early when unclocked.
        ticket_due = TICKET_MIN_WORK if pause_clocked else (TICKET_MIN_WORK + DEFAULT_PAUSE)

        if not pause_valid:
            out["ticket remaining"] = "pause too short (min %s)" % fmt_delta(TICKET_MIN_PAUSE)
            out["ticket remaining perc"] = 0
        else:
            out["ticket remaining at"] = fmt_delta(dt1 + (dt3 - dt2) + ticket_due)
            if worked >= ticket_due:
                out["ticket remaining"] = "reached"
                out["ticket remaining perc"] = 100
            else:
                out["ticket remaining"] = fmt_delta(ticket_due - worked)
                out["ticket remaining perc"] = 100 * worked.total_seconds() / ticket_due.total_seconds()
        out["ticket time"] = fmt_delta(ticket_due)

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
        overtime = out.get("overtime")
        if overtime is not None:
            print("Work time      : reached")
        else:
            print("Work time      : %s" % out["time remaining"])
        print("            at : %s" % out["time remaining at"])

        consuming = out.get("consume pause")
        if consuming is None:
            print("Total time     : %s" % out["total time"])
        else:
            print("Consume pause  : %s to go" % consuming)
        if overtime is not None:
            print("Overtime       : %s" % overtime)

        print("Ticket remain  : %s" % out["ticket remaining"])
        if "ticket remaining at" in out:
            print("            at : %s" % out["ticket remaining at"])
        print("Ticket time    : %s" % out["ticket time"])
        return 0
