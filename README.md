# wtime

Working-time tracker for INFN research staff (levels I-III / technologist).
Computes daily working time, overtime and meal-ticket eligibility from your
clock-in/clock-out times, either from numbers you type or fetched
automatically from the timecard portal.

## Install

```
pip install .
```

This installs a single `wtime` command (see `setup.py`). Requires Python
>= 3.7. The `-a`/`-d` portal-fetch options additionally require Chrome and
its matching chromedriver (installed automatically by `selenium` >= 4.6 via
Selenium Manager).

The GUI (`-g`) uses Tkinter, part of the Python standard library. On some
platforms it needs a separate system package — e.g. on macOS with Homebrew:
`brew install python-tk@<your-python-version>`.

## Usage

```
wtime T1 [T2 [T3 [T4]]]        print a report for the given clockings
wtime T1 [T2 [T3 [T4]]] -g     same, opening the Tkinter GUI instead
wtime -a                       fetch today's clockings from the portal
wtime -d                       fetch today's timecard summary from the portal
```

`T1`..`T4` are times in `H:M[:S]` format:
- `T1` clock-in
- `T2` clock-out for the break (omit if you haven't taken one yet)
- `T3` clock-in back from the break
- `T4` clock-out for the day

Only `T1` is required; missing later times are treated as "now" (or as the
time given with `-c`).

```
wtime 8:00 13:00 13:30 16:30      full day, 30' break clocked
wtime 8:00                        just started, report so far
wtime 8:00 -c 15:00                simulate a different current time
wtime 8:00 -g                     same, in the GUI
```

Other options:

| Flag             | Meaning                                              |
|-------------------|-------------------------------------------------------|
| `-c, --current-time` | simulate a different current time                  |
| `-g, --gui`        | open the Tkinter GUI instead of printing a report     |
| `-a, --auto`       | fetch today's clockings from the portal (autoclocking)|
| `-d, --data`       | fetch today's timecard summary (autoclocking_data)    |
| `-t, --timeout`    | seconds allowed to complete 2FA by hand (`-a`/`-d`)   |
| `--dump`           | save the portal page to `page_after_login.html`       |
| `--no-profile`     | use a throwaway Chrome profile instead of the saved one|

`-a`/`-d` cannot be combined with explicit times, `-g` or `-c`: they read
today's clockings from the portal instead of from you.

## Configuring the rules

All the section-specific numbers live in one place, at the top of
`wtimecore.py`:

- `WORK_DURATION` — daily working time due (default 7h12m)
- `DEFAULT_PAUSE` — pause assumed when none is clocked (default 30')
- `TICKET_MIN_WORK` — net work required for the meal ticket (default 6h)
- `TICKET_MIN_PAUSE` — minimum real pause for the meal ticket to be valid
  (default 30')

These follow the national research CCNL (art. 5, commi 2 and 10, for the
meal ticket rule). Check with your section's staff
office before relying on the defaults, especially `TICKET_MIN_PAUSE`.

## Portal autoclocking (`-a` / `-d`)

`-a` and `-d` log into the timecard portal and read today's data instead of
you typing it. They need three files in the working directory:

- `.aaiuser` — your portal username
- `.aaipass` — your portal password
- `.clockurl` — the portal URL

2FA is **not** automated: the script fills in username and password, opens
a visible Chrome window, and waits (default 180s, `-t` to change) for you
to complete the second factor by hand before reading the page. A dedicated
Chrome profile (`~/.autoclocking-chrome`) is reused between runs so the
portal may remember the device and ask for 2FA less often; use
`--no-profile` to opt out.

`-a` prints today's clockings (equivalent to what you'd type as `T1 T2 T3
T4`). `-d` prints a fuller summary: worked hours, past-month hours, today's
row and the ticket/trip counters read from the monthly table.

## Project layout

```
wtimecore.py         working-time calculation (no CLI, no printing besides
                     printout()) — this is where the configuration lives
wtimegui.py          Tkinter GUI, built on wtimecore
wtimecli.py          the wtime command: argument parsing and dispatch
portal_session.py    shared login/2FA-wait/browser-profile logic
autoclocking.py      -a: reads today's raw clockings from the portal
autoclocking_data.py -d: reads worked hours, tickets and trip days
setup.py             packaging (console_scripts entry point: wtime)
```

`autoclocking.py` and `autoclocking_data.py` can also be run directly
(`python3 autoclocking.py`) for standalone testing; `wtimecli.py` is the
normal way to use them through `wtime -a`/`wtime -d`.

