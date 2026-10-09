#!/usr/bin/env python3
"""
autoclocking_data - extract today's timecard summary from the web portal
(worked hours, past-month hours, today's row, ticket/trip counters).

See portal_session.py for the shared login/2FA-wait logic.
"""
import argparse
import sys
from datetime import datetime

from selenium.webdriver.common.by import By

from portal_session import PortalSession, PROFILE_DIR, TWO_FA_TIMEOUT

# =========================================================================
# CONFIGURATION specific to this script
# =========================================================================
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


class AutoClockingData(PortalSession):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        now = datetime.now()
        self.today = "%d %s" % (now.day, WEEKDAYS[now.weekday()])

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
        driver = self.new_driver()
        try:
            self.open_portal(driver)
            self.wait_for(driver, (By.CSS_SELECTOR, TOTALS_ROW_SELECTOR), "the timecard")

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
    parser.add_argument('--otp', metavar='CODE',
                        help="OTP code to type in as soon as the portal asks for it.")
    parser.add_argument('--no-profile', action='store_true',
                        help="Use a throwaway Chrome profile instead of the dedicated one.")
    parser.add_argument('-v', '--verbose', action='store_true',
                        help="Print every parsed table row while scanning.")
    args = parser.parse_args()

    ac = AutoClockingData(profile_dir=None if args.no_profile else PROFILE_DIR,
                          timeout_2fa=args.timeout, otp=args.otp)
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
