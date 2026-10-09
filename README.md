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

The GUI (`-G`) uses Tkinter, part of the Python standard library. On some
platforms it needs a separate system package — e.g. on macOS with Homebrew:
`brew install python-tk@<your-python-version>`.

## Usage

```
wtime T1 [T2 [T3 [T4]]]        print a report for the given clockings
wtime T1 [T2 [T3 [T4]]] -G     same, opening the Tkinter GUI instead
wtime T1 [T2 [T3 [T4]]] -T     same, opening the curses terminal UI instead
wtime T1 T2 -o                 morning-only: WORK_DURATION - (T2-T1),
                               for a day finished off-site (livelli I-III)
wtime -a                       fetch today's clockings from the portal
wtime -d                       fetch today's timecard summary from the portal
wtime -b                       open the month's timecard in the browser and
                               leave it open for manual use
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
wtime 8:00 -G                     same, in the GUI
```

Other options:

| Flag             | Meaning                                              |
|-------------------|-------------------------------------------------------|
| `-c, --current-time` | simulate a different current time (the simulated clock starts there and keeps ticking in `-G`/`-T`) |
| `-G, --gui`        | open the Tkinter GUI instead of printing a report     |
| `-T, --tui`        | open the curses terminal UI instead (no Tkinter/Tk needed) |
| `-o, --offsite`    | just `WORK_DURATION - (T2-T1)`: morning badge-clocked, rest done off-site |
| `-a, --auto`       | fetch today's clockings from the portal (autoclocking)|
| `-d, --data`       | fetch today's timecard summary (autoclocking_data)    |
| `-b, --browse`     | log in and leave the current month's timecard open in the browser |
| `-t, --timeout`    | seconds allowed to complete 2FA (`-a`/`-d`/`-b`)      |
| `--dump`           | save the portal page to `page_after_login.html`       |
| `--otp CODE`       | OTP typed in as soon as the portal asks (`-a`/`-d`/`-b`); otherwise you're asked in the terminal |
| `--no-profile`     | use a throwaway Chrome profile instead of the saved one|

`-a`/`-d`/`-b` cannot be combined with each other or with explicit times, `-G`, `-T`, `-c` or `-o`: they read
today's clockings from the portal instead of from you.

## Terminal UI (`-T`)

Same clockings/ticket/time blocks as the Tkinter GUI (`-G`), drawn with
`curses` instead - no Tk dependency, works over SSH. Keys: `t` marks the
next clocking (T2, then T3, then T4), `u` refreshes immediately, `q` quits.
It also refreshes on its own every 5 seconds, and freezes with a one-time
warning if left open past midnight, same as `-G`.

## Off-site days (`-o`)

Some days only the morning is badge-clocked (`T1`/`T2`), with the rest of
the day declared as off-site work (*lavoro fuori sede*, levels I-III). None
of the pause or meal-ticket rules apply there, so `-o` skips them entirely
and just prints `WORK_DURATION - (T2-T1)`:

```
wtime 8:00 13:00 -o      # Remaining : 02:12:00
wtime 8:00 15:30 -o      # Overtime  : 00:18:00
```

If you already have the worked duration (e.g. from your own notes), give a
single value instead of T1 T2 and wtime subtracts it directly:

```
wtime 3:57 -o            # Remaining : 03:15:00
```

## Configuring the rules

All the section-specific numbers live in one place, at the top of
`wtimecore.py`:

- `WORK_DURATION` — daily working time due (default 7h12m)
- `DEFAULT_PAUSE` — pause assumed when none is clocked (default 30')
- `TICKET_MIN_WORK` — net work required for the meal ticket (default 6h)
- `TICKET_MIN_PAUSE` — minimum real pause for the meal ticket to be valid
  (default 30')

These follow the national research CCNL (art. 5, commi 2 and 10, for the
meal ticket rule). They have not been confirmed against a Catania-specific
local circular (none was found publicly) — check with your section's staff
office before relying on the defaults, especially `TICKET_MIN_PAUSE`.

## Portal autoclocking (`-a` / `-d` / `-b`)

`-a` and `-d` log into the timecard portal and read today's data instead of
you typing it. They need three files in the working directory:

- `.aaiuser` — your portal username
- `.aaipass` — your portal password
- `.clockurl` — the portal URL

The OTP is **not generated** by wtime: the script fills in username and
password, opens a visible Chrome window, and when the portal shows its OTP
field it asks you for the code in the terminal (read it from your
authenticator app) and types it in. The TOTP seed stays in the authenticator,
never on this machine next to `.aaipass` - which is the point of keeping the
two factors apart. Answer with an empty line to do the second factor yourself
in the browser instead; after 3 wrong codes it also leaves it to you.
You can also give the code up front, `wtime -a --otp 123456`, and it is typed
in at once with no question asked (spaces are ignored: `--otp "123 456"`).
Codes last about 30 seconds and the browser takes a few to reach the OTP
page, so read the code just before pressing Enter; if it was already stale,
the second attempt asks you in the terminal. It is also kept in your shell
history, which is harmless for a one-time code but worth knowing. It
waits up to 180s overall (`-t` to change). A dedicated Chrome profile
(`~/.autoclocking-chrome`) is reused between runs so the portal may remember
the device and ask for 2FA less often; use `--no-profile` to opt out.

`-b` does the same login (including the OTP step) but, instead of
reading anything, switches to the current month and leaves the browser open
for you to use. The command returns when you close the window; Ctrl+C in the
terminal closes the browser too. While that window is open it holds the
dedicated Chrome profile, so a second `wtime -a`/`-d`/`-b` started meanwhile
will fail to launch - close the window first (or use `--no-profile`).

`-a` prints today's clockings (equivalent to what you'd type as `T1 T2 T3
T4`). `-d` prints a fuller summary: worked hours, past-month hours, today's
row and the ticket/trip counters read from the monthly table.

## Project layout

```
wtimecore.py         working-time calculation (no CLI, no printing besides
                     printout()) — this is where the configuration lives
wtimegui.py          Tkinter GUI, built on wtimecore
wtimetui.py          curses terminal UI, built on wtimecore (no Tkinter/Tk
                     needed - same blocks and day-rollover guard as the GUI)
wtimecli.py          the wtime command: argument parsing and dispatch
portal_session.py    shared login/2FA-wait/browser-profile logic
autoclocking.py      -a: reads today's raw clockings from the portal
autoclocking_data.py -d: reads worked hours, tickets and trip days
setup.py             packaging (console_scripts entry point: wtime)
```

`autoclocking.py` and `autoclocking_data.py` can also be run directly
(`python3 autoclocking.py`) for standalone testing; `wtimecli.py` is the
normal way to use them through `wtime -a`/`wtime -d`.

## Older versions

Earlier, single-file versions of this tool (`wtime5.py`, `wtimegui4.py`,
one-off `autoclocking*.py` scripts) are kept in the `legacy` branch and the
`legacy-final` tag for reference; they are not maintained.
