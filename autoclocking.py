#!/usr/bin/env python3
"""
autoclocking - extract today's clockings from the timecard web portal.

With 2FA enabled the script fills in username and password, then WAITS for you
to complete the second factor in the browser (visible window) and carries on
as soon as the timecard page shows up. The second factor is not automated.
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
# CONFIGURATION
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
MONTH_CHANGE_TIMEOUT = 10

PERIOD_INPUT_ID = 'cartellinoformperiodo:dateRef'
NEXT_MONTH_XPATH = "//input[@class='iceCmdBtn' and @value='>>']"
# Offsets (relative to the span holding the day) of the spans with the clockings
CLOCKING_OFFSETS = (1, 2, 7, 8)

# The portal is in Italian: these map its labels
MONTHS = {
    "gennaio": 1, "febbraio": 2, "marzo": 3, "aprile": 4,
    "maggio": 5, "giugno": 6, "luglio": 7, "agosto": 8,
    "settembre": 9, "ottobre": 10, "novembre": 11, "dicembre": 12,
}
WEEKDAYS = ('lun', 'mar', 'mer', 'gio', 'ven', 'sab', 'dom')


class AutoClocking:

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
                EC.presence_of_element_located((By.ID, PERIOD_INPUT_ID)))
        except TimeoutException:
            raise RuntimeError("Timecard not reached within %d s (login or 2FA "
                               "not completed?)" % self.timeout_2fa)

    @staticmethod
    def _period_value(driver):
        return driver.find_element(By.ID, PERIOD_INPUT_ID).get_attribute('value')

    def _ensure_current_month(self, driver):
        value = self._period_value(driver)          # e.g. "ottobre 2024"
        month_name, year = value.split()
        now = datetime.now()
        if MONTHS[month_name.lower()] == now.month and int(year) == now.year:
            return
        try:
            WebDriverWait(driver, MONTH_CHANGE_TIMEOUT).until(
                EC.element_to_be_clickable((By.XPATH, NEXT_MONTH_XPATH))).click()
            WebDriverWait(driver, MONTH_CHANGE_TIMEOUT).until(
                lambda d: self._period_value(d) != value)
        except TimeoutException:
            raise RuntimeError("Cannot switch to the current month "
                               "(shown: %s)" % value)

    # ---------- extraction ------------------------------------------------

    def get_clocking(self, wait=False, dump=False):
        """Return today's clockings as a list of strings, e.g. ['08:01', ...]."""
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

            self._ensure_current_month(driver)

            today = datetime.now()
            day_search = "%s %s" % (today.strftime("%d"), WEEKDAYS[today.weekday()])

            spans = driver.find_elements(By.CLASS_NAME, "iceOutTxt")
            times = []
            for index, span in enumerate(spans):
                if day_search in span.text:
                    for offset in CLOCKING_OFFSETS:
                        try:
                            text = spans[index + offset].text.strip()
                        except IndexError:
                            print("Error: day row elements not found", file=sys.stderr)
                            break
                        if not text:
                            break
                        times.append(text)
                    break

            if wait:
                input("Press <ENTER> to conclude ...")
            return times
        finally:
            driver.quit()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract today's clockings from the timecard.")
    parser.add_argument('-w', '--wait', action='store_true',
                        help="Wait for ENTER before closing the browser.")
    parser.add_argument('-t', '--timeout', type=int, default=TWO_FA_TIMEOUT,
                        help="Seconds to complete 2FA (default %d)." % TWO_FA_TIMEOUT)
    parser.add_argument('--dump', action='store_true',
                        help="Save the page after login to page_after_login.html.")
    parser.add_argument('--no-profile', action='store_true',
                        help="Use a throwaway Chrome profile instead of the dedicated one.")
    args = parser.parse_args()

    ac = AutoClocking(profile_dir=None if args.no_profile else PROFILE_DIR,
                      timeout_2fa=args.timeout)
    try:
        print(' '.join(ac.get_clocking(wait=args.wait, dump=args.dump)))
    except RuntimeError as e:
        print("ERROR: %s" % e, file=sys.stderr)
        sys.exit(1)
