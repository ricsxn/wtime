#!/usr/bin/env python3
"""
wtimecli - single entry point for the wtime command.

  wtime T1 [T2 [T3 [T4]]]        print a report for the given clockings
  wtime T1 [T2 [T3 [T4]]] -G     same, opening the Tkinter GUI instead
  wtime T1 [T2 [T3 [T4]]] -T     same, opening the curses terminal UI instead
  wtime T1 T2 -o                 morning-only: WORK_DURATION - (T2-T1),
                                 for a day finished off-site (livelli I-III)
  wtime HH:MM -o                 same, but you already have the worked
                                 duration: WORK_DURATION - HH:MM
  wtime -a                       fetch today's clockings from the portal
  wtime -d                       fetch today's timecard summary from the portal
  wtime -b                       open the month's timecard in the browser and
                                 leave it open for manual use
"""
import argparse
import sys

from wtimecore import wtime, offsite_remaining, parse_duration, fmt_delta, WORK_DURATION


def build_parser():
    parser = argparse.ArgumentParser(
        prog="wtime",
        description="INFN working-time tracker: report, GUI and portal fetch.")
    parser.add_argument('times', nargs='*', metavar='Tn',
                        help="clockings in H:M[:S] format: T1 [T2 [T3 [T4]]]")
    parser.add_argument('-c', '--current-time', metavar='HH:MM[:SS]',
                        help="simulate a different current time")
    parser.add_argument('-G', '--gui', action='store_true',
                        help="open the Tkinter GUI instead of printing a report")
    parser.add_argument('-T', '--tui', action='store_true',
                        help="open the curses terminal UI instead of printing "
                             "a report (no Tkinter/Tk needed)")
    parser.add_argument('-o', '--offsite', action='store_true',
                        help="WORK_DURATION minus what's already worked, for "
                             "a day finished off-site (lavoro fuori sede, "
                             "livelli I-III) - no pause or meal-ticket rule "
                             "applied. Takes T1 T2 (clock-in/out) or a "
                             "single already-worked duration, e.g. 3:57")
    parser.add_argument('-a', '--auto', action='store_true',
                        help="fetch today's clockings from the portal (autoclocking)")
    parser.add_argument('-d', '--data', action='store_true',
                        help="fetch today's timecard summary from the portal (autoclocking_data)")
    parser.add_argument('-b', '--browse', action='store_true',
                        help="log in and leave the current month's timecard open "
                             "in the browser for manual use (close the window to finish)")
    parser.add_argument('-t', '--timeout', type=int,
                        help="seconds to complete 2FA (only with -a/-d/-b)")
    parser.add_argument('--dump', action='store_true',
                        help="save the portal page to page_after_login.html (only with -a/-d/-b)")
    parser.add_argument('--otp', metavar='CODE',
                        help="OTP code to type in as soon as the portal asks for it "
                             "(only with -a/-d/-b); without it you are asked in the terminal")
    parser.add_argument('--no-profile', action='store_true',
                        help="use a throwaway Chrome profile (only with -a/-d/-b)")
    return parser


def _portal_kwargs(args):
    from portal_session import PROFILE_DIR
    kwargs = {'profile_dir': None if args.no_profile else PROFILE_DIR}
    if args.timeout is not None:
        kwargs['timeout_2fa'] = args.timeout
    if args.otp:
        kwargs['otp'] = args.otp
    return kwargs


def run_auto(args):
    from autoclocking import AutoClocking
    ac = AutoClocking(**_portal_kwargs(args))
    try:
        times = ac.get_clocking(dump=args.dump)
    except RuntimeError as e:
        print("ERROR: %s" % e, file=sys.stderr)
        return 1
    print(' '.join(times))
    return 0


def run_data(args):
    from autoclocking_data import AutoClockingData
    ac = AutoClockingData(**_portal_kwargs(args))
    try:
        data = ac.get_clocking(dump=args.dump)
    except RuntimeError as e:
        print("ERROR: %s" % e, file=sys.stderr)
        return 1
    print("Worked hours     : %s" % data['worked_hours'])
    print("Past month hours : %s" % data['past_month_hours'])
    print("Today row        : %s" % data['today_row'])
    if data['today_extra_rows']:
        print("Today extra rows : %s" % data['today_extra_rows'])
    print("Tickets          : %d" % data['ticket_count'])
    print("Trip days        : %d" % data['trip_count'])
    return 0


def run_browse(args):
    from autoclocking import AutoClocking
    ac = AutoClocking(**_portal_kwargs(args))
    try:
        ac.browse(dump=args.dump)
    except RuntimeError as e:
        print("ERROR: %s" % e, file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print(file=sys.stderr)  # Ctrl+C: the browser is closed, exit quietly
    return 0


def run_offsite(args):
    if len(args.times) == 1:
        # a single value: already-worked duration, e.g. "3:57"
        try:
            worked = parse_duration(args.times[0])
        except ValueError as e:
            print("ERROR: %s" % e, file=sys.stderr)
            return 1
        remaining = WORK_DURATION - worked
    elif len(args.times) == 2:
        # two values: clock-in/clock-out, wtime computes T2-T1 itself
        try:
            remaining = offsite_remaining(args.times[0], args.times[1])
        except ValueError as e:
            print("ERROR: %s" % e, file=sys.stderr)
            return 1
    else:
        print("ERROR: -o takes either T1 T2 (clock-in/out) or a single "
             "already-worked duration, e.g. 3:57", file=sys.stderr)
        return 1
    if remaining.total_seconds() >= 0:
        print("Remaining : %s" % fmt_delta(remaining))
    else:
        print("Overtime  : %s" % fmt_delta(-remaining))
    return 0


def run_report_or_gui(args):
    t1, t2, t3, t4 = (args.times + [None, None, None, None])[:4]
    if not t1:
        print("ERROR: at least T1 is required", file=sys.stderr)
        return 1
    if args.gui:
        try:
            from wtimegui import wtimeGUI
        except ModuleNotFoundError as e:
            # '_tkinter' missing: the Tk bridge is absent (e.g. Homebrew
            # Python); 'tkinter' missing: the whole package is (e.g. Debian/
            # Ubuntu without python3-tk). Same remedy family for both.
            if e.name in ('_tkinter', 'tkinter'):
                print("ERROR: Tkinter is not available in this Python "
                     "(missing '%s'). Install it - macOS/Homebrew: "
                     "brew install python-tk@<your-python-version>; "
                     "Debian/Ubuntu: sudo apt install python3-tk - or use "
                     "the terminal UI instead: -T (no Tk needed)." % e.name,
                     file=sys.stderr)
                return 1
            raise
        wtimeGUI(t1=t1, t2=t2, t3=t3, t4=t4, current_time=args.current_time)
        return 0
    if args.tui:
        from wtimetui import main as tui_main
        tui_main(t1=t1, t2=t2, t3=t3, t4=t4, current_time=args.current_time)
        return 0
    wt = wtime(t1=t1, t2=t2, t3=t3, t4=t4, current_time=args.current_time)
    out = wt.calc2()
    return wt.printout(out)


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.otp and not (args.auto or args.data or args.browse):
        parser.error("--otp only makes sense with -a, -d or -b")
    if sum([args.auto, args.data, args.browse]) > 1:
        parser.error("-a, -d and -b are mutually exclusive")
    if (args.auto or args.data or args.browse) and (
            args.times or args.gui or args.tui or args.current_time or args.offsite):
        parser.error("-a/-d/-b work on the portal: they can't be combined "
                     "with explicit times, -G, -T, -c or -o")
    if args.gui and args.tui:
        parser.error("-G and -T are mutually exclusive")
    if args.offsite and (args.gui or args.tui):
        parser.error("-o can't be combined with -G or -T")

    if args.auto:
        return run_auto(args)
    if args.data:
        return run_data(args)
    if args.browse:
        return run_browse(args)
    if args.offsite:
        return run_offsite(args)
    return run_report_or_gui(args)


if __name__ == "__main__":
    sys.exit(main())
