import argparse
import sys
from datetime import datetime
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC




class AutoClocking:

    def __init__(self, userfile, passfile, clockurl):
        self.ok = True
        self.username = self.read_string_file(userfile)
        self.password = self.read_string_file(passfile)
        self.url = self.read_string_file(clockurl)
        if self.password is None or len(self.password) == 0 or\
            self.username is None or len(self.username) == 0:
            print('WARNING: No password file found',file=sys.stderr)
            self.ok = False


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

        # Print or process the HTML content
        #with open('cartellino.html', 'w', encoding='utf-8') as file:
        #    file.write(html_content)


        # You can also save the HTML to a file if needed
        with open('page_after_login.html', 'w', encoding='utf-8') as f:
            f.write(html_content)

        # Estrarre il valore del mese dal tag input con id 'cartellinoformperiodo:dateRef'
        input_element = driver.find_element(By.ID, 'cartellinoformperiodo:dateRef')
        input_value = input_element.get_attribute('value')  # Questo sarà tipo "ottobre 2024"

        month_map = {
            "gennaio": 1,
            "febbraio": 2,
            "marzo": 3,
            "aprile": 4,
            "maggio": 5,
            "giugno": 6,
            "luglio": 7,
            "agosto": 8,
            "settembre": 9,
            "ottobre": 10,
            "novembre": 11,
            "dicembre": 12
        }

        # Dividere 'ottobre 2024' in due parti: mese e anno
        input_month, input_year = input_value.split()
        input_month_number = month_map[input_month.lower()]  # Ottieni il numero del mese
        input_year_number = int(input_year)  # Converti l'anno in intero

        # Prendere il mese e l'anno correnti
        current_month_number = datetime.now().month
        current_year_number = datetime.now().year

        # Confrontare il mese e l'anno correnti con quelli estratti dalla pagina
        if input_month_number == current_month_number and input_year_number == current_year_number:
            #print("Il mese e l'anno corrispondono al mese corrente.")
            pass
        else:
            #print(f"Il mese e l'anno non corrispondono. Mese trovato: {input_month_number}, anno: {input_year_number}")
            try:
                # Premere il pulsante per aggiornare il mese
                button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//input[@class='iceCmdBtn' and @value='>>']"))
                )
                button.click()
                time.sleep(1)

                # Rileggere il nuovo valore dopo l'aggiornamento della pagina
                input_value = driver.find_element(By.ID, 'cartellinoformperiodo:dateRef').get_attribute('value')
                #print(f"Nuovo mese dopo aggiornamento: {updated_input_value}")
            except:
                print("Errore nel caricamento della nuova pagina:", e)
                sys.exit(1)

        # Mappatura dei giorni della settimana dall'inglese all'italiano
        days_map = {
            'mon': 'lun',
            'tue': 'mar',
            'wed': 'mer',
            'thu': 'gio',
            'fri': 'ven',
            'sat': 'sab',
            'sun': 'dom'
        }

        oggi = datetime.now()
        giorno_corrente = oggi.strftime("%d")  # Formatta il giorno corrente come "04"
        giorno_settimana_corrente = oggi.strftime("%a").lower()  # Formatta il giorno della settimana come "ven", "lun", ecc.
        if giorno_settimana_corrente in days_map.keys():
            giorno_settimana_corrente = days_map[giorno_settimana_corrente]

        day_search = giorno_corrente + " " + giorno_settimana_corrente

        span_elements = driver.find_elements(By.CLASS_NAME, "iceOutTxt")

        #print(f'searching: {day_search} in span elements')

        # Cercare il tag che contiene il giorno e il giorno della settimana correnti
        for index, span in enumerate(span_elements):
            if day_search in span.text:
                #print(index, span.get_attribute('outerHTML'))
                # Ora cerca i successivi elementi dopo questo span
                try:
                    for i in [1,2,7,8]:
                        time_span = span_elements[index + i].text.strip()
                        if time_span is not None and time_span != '':
                            print(time_span, end=' ')
                        else:
                            break
                except IndexError:
                    print("Errore: uno degli elementi successivi non è stato trovato!")
                break     
            else:
                #print("Today tag not found on web page")
                pass

        if wait is True:
            input("Press <ENTER> to conclude ...")
        driver.quit()



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Script con opzione di attesa.")
    parser.add_argument('-w', '--wait', action='store_true', help="Attende che l'utente prema Enter prima di terminare.")
    args = parser.parse_args()

    auto_clocking = AutoClocking('.aaiuser', '.aaipass', '.clockurl')
    auto_clocking.get_clocking(wait=args.wait)

