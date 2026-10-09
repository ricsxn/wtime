#!/usr/bin/env python3
"""
autoclocking - extract today's clockings from the timecard web portal.

See portal_session.py for the shared login/2FA-wait logic.
"""
import argparse
import sys
import time
from datetime import datetime

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, WebDriverException

from portal_session import PortalSession, PROFILE_DIR, TWO_FA_TIMEOUT

# =========================================================================
# CONFIGURATION specific to this script
# =========================================================================
PERIOD_INPUT_ID = 'cartellinoformperiodo:dateRef'
NEXT_MONTH_XPATH = "//input[@class='iceCmdBtn' and @value='>>']"
MONTH_CHANGE_TIMEOUT = 10
# Offsets (relative to the span holding the day) of the spans with the clockings
CLOCKING_OFFSETS = (1, 2, 7, 8)

# The portal is in Italian: these are literal labels shown on the page, not
# code semantics.
MONTHS = {
    "gennaio": 1, "febbraio": 2, "marzo": 3, "aprile": 4,
    "maggio": 5, "giugno": 6, "luglio": 7, "agosto": 8,
    "settembre": 9, "ottobre": 10, "novembre": 11, "dicembre": 12,
}
WEEKDAYS = ('lun', 'mar', 'mer', 'gio', 'ven', 'sab', 'dom')


class AutoClocking(PortalSession):

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

    @staticmethod
    def _wait_until_closed(driver):
        """Block until the user closes the browser window (or it dies)."""
        while True:
            try:
                if not driver.window_handles:
                    return
            except WebDriverException:
                return  # browser or driver is gone
            time.sleep(1)

    def browse(self, dump=False):
        """Log in, land on the current month's timecard and leave the browser
        open for manual use. Returns when the window is closed; Ctrl+C in the
        terminal closes the browser too."""
        if not self.ok:
            raise RuntimeError("Autoclocking is not configured correctly")
        driver = self.new_driver()
        try:
            self.open_portal(driver)
            self.wait_for(driver, (By.ID, PERIOD_INPUT_ID), "the timecard")
            if dump:
                with open('page_after_login.html', 'w', encoding='utf-8') as f:
                    f.write(driver.page_source)
            self._ensure_current_month(driver)
            print("Timecard open in the browser. Close the window (or press "
                  "Ctrl+C here) when done.", file=sys.stderr)
            self._wait_until_closed(driver)
        finally:
            try:
                driver.quit()
            except WebDriverException:
                pass  # already closed by the user

    def get_clocking(self, wait=False, dump=False):
        """Return today's clockings as a list of strings, e.g. ['08:01', ...]."""
        if not self.ok:
            raise RuntimeError("Autoclocking is not configured correctly")
        driver = self.new_driver()
        try:
            self.open_portal(driver)
            self.wait_for(driver, (By.ID, PERIOD_INPUT_ID), "the timecard")

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
    parser.add_argument('--otp', metavar='CODE',
                        help="OTP code to type in as soon as the portal asks for it.")
    parser.add_argument('--no-profile', action='store_true',
                        help="Use a throwaway Chrome profile instead of the dedicated one.")
    args = parser.parse_args()

    ac = AutoClocking(profile_dir=None if args.no_profile else PROFILE_DIR,
                      timeout_2fa=args.timeout, otp=args.otp)
    try:
        print(' '.join(ac.get_clocking(wait=args.wait, dump=args.dump)))
    except RuntimeError as e:
        print("ERROR: %s" % e, file=sys.stderr)
        sys.exit(1)
