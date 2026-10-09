#!/usr/bin/env python3
"""
portal_session - shared browser/login/2FA-wait logic for the timecard portal
scripts (autoclocking.py, autoclocking_data.py).

Subclasses only need the page-specific extraction logic: this module handles
reading credentials, starting the browser, logging in, and getting through
the 2FA step: when the portal shows its OTP field, the code is asked in the
terminal and typed in for you (the TOTP seed stays in your authenticator app,
never on this machine); or you can complete it by hand in the visible window.
"""
import os
import re
import sys

from selenium import webdriver
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
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

# The portal's OTP page: <input id="otp" name="otp" type="text" ...>
OTP_FIELD_ID = 'otp'
OTP_MAX_ATTEMPTS = 3      # codes asked in the terminal before leaving it to you in the browser


class PortalSession:
    """Handles credentials, browser setup, login and 2FA waiting for the
    timecard portal. Subclasses add the page-specific extraction logic and
    call open_portal()/wait_for() with their own target element."""

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

    @staticmethod
    def _ask_otp():
        """Ask the code in the terminal. Returns '' if the user prefers to do
        it in the browser (empty answer) or there is no terminal to ask on."""
        print("OTP requested. Enter the code from your authenticator app "
              "(empty = do it yourself in the browser): ",
              end="", file=sys.stderr, flush=True)
        try:
            code = input()
        except EOFError:
            print(file=sys.stderr)
            return ""
        return re.sub(r"\s+", "", code)   # authenticator apps show "123 456"

    def _enter_otp(self, field):
        code = self._ask_otp()
        if not code:
            return
        field.clear()
        field.send_keys(code)
        field.send_keys(Keys.RETURN)   # submits the form

    def wait_for(self, driver, locator, what="the timecard"):
        """Wait for `locator` to appear. If the portal shows its OTP field
        meanwhile, ask the code in the terminal and type it in (up to
        OTP_MAX_ATTEMPTS times; after that, or with an empty answer, the 2FA is
        left to you in the browser). Raises RuntimeError on timeout instead of
        leaving the caller with a half-loaded page."""
        print("Waiting for %s: if asked, give the OTP here or complete 2FA in "
              "the browser (max %d s)..." % (what, self.timeout_2fa),
              file=sys.stderr)
        state = {'prompts': 0, 'last_field': None}

        def ready(d):
            if d.find_elements(*locator):
                return True
            if state['prompts'] < OTP_MAX_ATTEMPTS:
                try:
                    fields = d.find_elements(By.ID, OTP_FIELD_ID)
                    # a new page load gives a new element: that's how a wrong
                    # code (OTP page shown again) is told from the same page
                    if (fields and fields[0].is_displayed()
                            and fields[0].id != state['last_field']):
                        state['last_field'] = fields[0].id
                        state['prompts'] += 1
                        self._enter_otp(fields[0])
                except WebDriverException:
                    pass  # page changed under us (stale element): re-check next poll
            return False

        try:
            WebDriverWait(driver, self.timeout_2fa).until(ready)
        except TimeoutException:
            raise RuntimeError("%s not reached within %d s (login or 2FA "
                               "not completed?)" % (what.capitalize(), self.timeout_2fa))
