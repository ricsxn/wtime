import argparse
import sys
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC




class AutoClocking:

    # Define a dictionary for the Italian weekday names
    weekdays = {
        0: 'lun',  # Monday
        1: 'mar',  # Tuesday
        2: 'mer',  # Wednesday
        3: 'gio',  # Thursday
        4: 'ven',  # Friday
        5: 'sab',  # Saturday
        6: 'dom'   # Sunday
    }

    def __init__(self, userfile, passfile, clockurl):
        self.ok = True
        self.username = self.read_string_file(userfile)
        self.password = self.read_string_file(passfile)
        self.url = self.read_string_file(clockurl)
        if self.password is None or len(self.password) == 0 or\
            self.username is None or len(self.username) == 0:
            print('WARNING: No password file found',file=sys.stderr)
            self.ok = False
        now = datetime.now()
        day_number = now.day
        weekday_name = self.weekdays[now.weekday()]
        self.today = f"{day_number} {weekday_name}"


    def read_string_file(self, file_path):
        try:
            with open(file_path, 'r') as file:
                content = file.read()
            return content
        except FileNotFoundError:
            print(f"The file {file_path} does not exist.")
            return None
        except IOError:
            print(f"Error reading the file {file_path}.")
            return None

    def get_clocking(self, **kwargs):
        wait = kwargs.get('wait', False)
        if self.ok is False:
            print('ERROR: Autoclocking not well configured',file=sys.stderr)
            sys.exit(1)
        # Open the browser and go to the login page
        driver = webdriver.Chrome()
        driver.get(self.url)

        # Find elements by their IDs and send credentials
        login_field = driver.find_element(By.ID, 'user')  # Replace 'login_id' with the actual ID
        password_field = driver.find_element(By.ID, 'PASS')  # Replace 'password_id' with the actual ID
        login_button = driver.find_element(By.ID, 'login-btn')  # Replace 'button_id' with the actual ID

        # Send the login credentials
        login_field.send_keys(self.username)  # Enter your username
        password_field.send_keys(self.password)  # Enter your password
        # Click the login button
        login_button.click()

        # Optionally, you can wait to observe what happens (useful for debugging)
        driver.implicitly_wait(5)  # Waits for 5 seconds

        # Get the page source (HTML) of the page after successful login
        html_content = driver.page_source

        # You can also save the HTML to a file if needed
        with open('page_after_login.html', 'w', encoding='utf-8') as f:
            f.write(html_content)

        # Select the first <td> element that contains the relevant class
        tds = driver.find_elements(By.CSS_SELECTOR,'tr.icePnlGrdRow1.infnTotaliCartellinoRow1 td')

        # Extract the ID to get the prefix (e.g., j_id102:j_id103)
        id_value = tds[0].get_attribute("id")
        prefix = id_value.split('-')[0]  # Get the prefix part before the '-'
        print(f"Prefix extracted: {prefix}")

        workded_hours = None
        worked_hours_td = driver.find_element(By.ID, prefix+'-0-5')
        worked_hours = worked_hours_td.find_element(By.CSS_SELECTOR, "span.iceOutTxt.infnTotaliCartellino").text
        print(f'Worked hours: {worked_hours}') 

        past_month_hours = None
        past_month_hours_td = driver.find_element(By.ID, prefix+'-0-7')
        past_month_hours = past_month_hours_td.find_element(By.CSS_SELECTOR, "span.iceOutTxt.infnTotaliCartellino").text
        print(f'Past month hours: {past_month_hours}')

        # Locate the div with class 'cartellino'
        div_element = driver.find_element("id", "cartellino")

        # Locate the table rows
        #rows = driver.find_elements(By.CSS_SELECTOR, "table.iceDatTbl > tbody > tr")
        rows = driver.find_elements(By.CSS_SELECTOR, "table.iceDatTbl > tbody > tr.iceDatTblRow1, table.iceDatTbl > tbody > tr.iceDatTblRow2")


        # Loop through each row and get the inner text of the cells
        today_flag=''
        today_row1 = None
        today_row2 = None
        ticket_count = 0
        trip_count = 0

        for row in rows:
            #print(f'[{row.get_attribute('innerHTML')}]')
            row_html = row.text.strip()
            cells = row_html.split('\n')  # Gets all text inside the row and splits it by spaces
            if any(x in row_html for x in ['lun', 'mar', 'mer', 'gio', 'ven', 'sab', 'dom']):
                if 'Ticket' in cells:
                    ticket_count += 1
                if 'Trasferta' in cells:
                    trip_count += 1
                if self.today == cells[0]:
                    today_flag = '*'
                    today_row1 = cells
                else:
                    today_flag = '' 
                print(f'{today_flag}{cells}')
                continue
            else:
                print(f'{today_flag}\t{cells}')
            if today_flag == '*':
                today_row2 = cells

        # Today values
        print(f'Today row1:{today_row1}, Today row2:{today_row2}')
        print(f'Tickets: {ticket_count}')
        print(f'Trip days: {trip_count}')

        if wait is True:
            input("Press <ENTER> to conclude ...")
        driver.quit()




if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Script con opzione di attesa.")
    parser.add_argument('-w', '--wait', action='store_true', help="Attende che l'utente prema Enter prima di terminare.")
    args = parser.parse_args()

    auto_clocking = AutoClocking('.aaiuser', '.aaipass', '.clockurl')
    auto_clocking.get_clocking(wait=args.wait)

