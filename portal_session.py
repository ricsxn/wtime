#!/usr/bin/env python3
"""
portal_session - shared browser/login/2FA-wait logic for the timecard portal
scripts (autoclocking.py, autoclocking_data.py).

Subclasses only need the page-specific extraction logic: this module handles
reading credentials, starting the browser, logging in, and waiting for the
user to complete 2FA by hand in the visible window.
"""
import os
import sys

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# =========================================================================
# CONFIGURATION - shared defaults; pass different values to __init__ to
# override them for a single script without touching this file.
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


class PortalSession:
    """Handles credentials, browser setup, login and 2FA waiting for the
    timecard portal. Subclasses add the page-specific extraction logic and
    call open_portal()/_wait_for() with their own target element."""

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

    def new_driver(self):
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

    def open_portal(self, driver):
        """Navigate to the portal and log in if a login form is shown."""
        if not self.ok:
            raise RuntimeError("Session is not configured correctly")
        driver.get(self.url)
        self._login(driver)

    def wait_for(self, driver, locator, what="the timecard"):
        """Wait for `locator` to appear, giving the user time to complete
        2FA by hand in the visible browser window. Raises RuntimeError on
        timeout instead of leaving the caller with a half-loaded page."""
        print("Waiting for %s: if asked, complete 2FA in the browser "
              "(max %d s)..." % (what, self.timeout_2fa), file=sys.stderr)
        try:
            WebDriverWait(driver, self.timeout_2fa).until(
                EC.presence_of_element_located(locator))
        except TimeoutException:
            raise RuntimeError("%s not reached within %d s (login or 2FA "
                               "not completed?)" % (what.capitalize(), self.timeout_2fa))
