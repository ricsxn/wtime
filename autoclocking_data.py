#!/usr/bin/env python3
"""
autoclocking_data - extract today's timecard summary from the web portal
(worked hours, past-month hours, today's row, ticket/trip counters).

With 2FA enabled the script fills in username and password, then WAITS for you
to complete the second factor in the browser (visible window) and carries on
as soon as the timecard totals show up. The second factor is not automated.
"""
import argparse
import os
import sys
from datetime import datetime

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# =========================================================================
# CONFIGURATION - the only place to edit to adapt the script to a different
# INFN section or a portal layout change.
# =========================================================================
USER_FILE = '.aaiuser'
PASS_FILE = '.aaipass'
URL_FILE = '.clockurl'

# Dedicated Chrome profile: keeps cookies/session between runs (if the portal
# allows it, 2FA may be asked less often). Set to None to use a throwaway
# profile every time.
PROFILE_DIR = os.path.expanduser('~/.autoclocking-chrome')

TWO_FA_TIMEOUT = 180       # seconds allowed to complete 2FA by hand
LOGIN_FIELD_TIMEOUT = 5    # seconds to detect whether a login is needed (session still valid?)

TOTALS_ROW_SELECTOR = 'tr.icePnlGrdRow1.infnTotaliCartellinoRow1 td'
TOTALS_VALUE_SELECTOR = "span.iceOutTxt.infnTotaliCartellino"
WORKED_HOURS_SUFFIX = '-0-5'
PAST_MONTH_HOURS_SUFFIX = '-0-7'
TABLE_ROW_SELECTOR = ("table.iceDatTbl > tbody > tr.iceDatTblRow1, "
                      "table.iceDatTbl > tbody > tr.iceDatTblRow2")

# The portal is in Italian: these are literal labels/weekday abbreviations
# shown on the page, not code semantics.
WEEKDAYS = ('lun', 'mar', 'mer', 'gio', 'ven', 'sab', 'dom')
TICKET_LABEL = 'Ticket'
TRIP_LABEL = 'Trasferta'


class AutoClockingData:

    def __init__(self, user_file=USER_FILE, pass_file=PASS_FILE, url_file=URL_FILE,
                 profile_dir=PROFILE_DIR, timeout_2fa=TWO_FA_TIMEOUT):
        self.username = self._read(user_file)
        self.password = self._read(pass_file)
        self.url = self._read(url_file)
        self.profile_dir = profile_dir
        self.timeout_2fa = timeout_2fa
        self.ok = bool(self.username and self.password and self.url)
        if not self.ok:
            print('WARNING: missing credentials or URL', file=sys.stderr)
        now = datetime.now()
        self.today = "%d %s" % (now.day, WEEKDAYS[now.weekday()])

    @staticmethod
    def _read(path):
        try:
            with open(path, 'r') as f:
                return f.read().strip()   # strip: no trailing newline in user/pass/url
        except (FileNotFoundError, IOError) as e:
            print("Cannot read %s: %s" % (path, e), file=sys.stderr)
            return None

    # ---------- browser ---------------------------------------------------

    def _new_driver(self):
        opts = Options()
        if self.profile_dir:
            opts.add_argument('--user-data-dir=%s' % self.profile_dir)
        return webdriver.Chrome(options=opts)

    def _login(self, driver):
        try:
            login_field = WebDriverWait(driver, LOGIN_FIELD_TIMEOUT).until(
                EC.presence_of_element_located((By.ID, 'user')))
        except TimeoutException:
            return  # no login form: session is probably still active
        login_field.send_keys(self.username)
        driver.find_element(By.ID, 'PASS').send_keys(self.password)
        driver.find_element(By.ID, 'login-btn').click()

    def _wait_for_timecard(self, driver):
        print("Waiting for the timecard: if asked, complete 2FA in the "
              "browser (max %d s)..." % self.timeout_2fa, file=sys.stderr)
        try:
            WebDriverWait(driver, self.timeout_2fa).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, TOTALS_ROW_SELECTOR)))
        except TimeoutException:
            raise RuntimeError("Timecard not reached within %d s (login or 2FA "
                               "not completed?)" % self.timeout_2fa)

    # ---------- extraction ------------------------------------------------

    @staticmethod
    def _totals_value(driver, prefix, suffix):
        cell = driver.find_element(By.ID, prefix + suffix)
        return cell.find_element(By.CSS_SELECTOR, TOTALS_VALUE_SELECTOR).text

    def get_clocking(self, wait=False, dump=False, verbose=False):
        """Return a dict summarizing today's timecard: worked_hours,
        past_month_hours, today_row, today_extra_rows, ticket_count,
        trip_count."""
        if not self.ok:
            raise RuntimeError("Autoclocking is not configured correctly")

        driver = self._new_driver()
        try:
            driver.get(self.url)
            self._login(driver)
            self._wait_for_timecard(driver)

            if dump:
                with open('page_after_login.html', 'w', encoding='utf-8') as f:
                    f.write(driver.page_source)

            totals_cells = driver.find_elements(By.CSS_SELECTOR, TOTALS_ROW_SELECTOR)
            if not totals_cells:
                raise RuntimeError("Totals row not found on the timecard page")
            prefix = totals_cells[0].get_attribute("id").split('-')[0]

            worked_hours = self._totals_value(driver, prefix, WORKED_HOURS_SUFFIX)
            past_month_hours = self._totals_value(driver, prefix, PAST_MONTH_HOURS_SUFFIX)

            rows = driver.find_elements(By.CSS_SELECTOR, TABLE_ROW_SELECTOR)

            ticket_count = 0
            trip_count = 0
            today_row = None        # today's header row (date, clockings, ...)
            today_extra_rows = []   # continuation rows under today's header, if any
            in_today_block = False

            for row in rows:
                cells = row.text.strip().split('\n')
                is_day_header = bool(cells and cells[0]) and any(day in cells[0] for day in WEEKDAYS)
                if is_day_header:
                    if TICKET_LABEL in cells:
                        ticket_count += 1
                    if TRIP_LABEL in cells:
                        trip_count += 1
                    in_today_block = (cells[0] == self.today)
                    if in_today_block:
                        today_row = cells
                    if verbose:
                        print(('*' if in_today_block else '') + str(cells))
                else:
                    if in_today_block:
                        today_extra_rows.append(cells)
                    if verbose:
                        print(('*' if in_today_block else '') + '\t' + str(cells))

            if wait:
                input("Press <ENTER> to conclude ...")

            return {
                'worked_hours': worked_hours,
                'past_month_hours': past_month_hours,
                'today_row': today_row,
                'today_extra_rows': today_extra_rows,
                'ticket_count': ticket_count,
                'trip_count': trip_count,
            }
        finally:
            driver.quit()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract today's timecard summary from the portal.")
    parser.add_argument('-w', '--wait', action='store_true',
                        help="Wait for ENTER before closing the browser.")
    parser.add_argument('-t', '--timeout', type=int, default=TWO_FA_TIMEOUT,
                        help="Seconds to complete 2FA (default %d)." % TWO_FA_TIMEOUT)
    parser.add_argument('--dump', action='store_true',
                        help="Save the page after login to page_after_login.html.")
    parser.add_argument('--no-profile', action='store_true',
                        help="Use a throwaway Chrome profile instead of the dedicated one.")
    parser.add_argument('-v', '--verbose', action='store_true',
                        help="Print every parsed table row while scanning.")
    args = parser.parse_args()

    ac = AutoClockingData(profile_dir=None if args.no_profile else PROFILE_DIR,
                          timeout_2fa=args.timeout)
    try:
        data = ac.get_clocking(wait=args.wait, dump=args.dump, verbose=args.verbose)
    except RuntimeError as e:
        print("ERROR: %s" % e, file=sys.stderr)
        sys.exit(1)

    print("Worked hours     : %s" % data['worked_hours'])
    print("Past month hours : %s" % data['past_month_hours'])
    print("Today row        : %s" % data['today_row'])
    if data['today_extra_rows']:
        print("Today extra rows : %s" % data['today_extra_rows'])
    print("Tickets          : %d" % data['ticket_count'])
    print("Trip days        : %d" % data['trip_count'])
