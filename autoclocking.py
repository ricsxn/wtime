import sys
from datetime import datetime
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

    def get_clocking(self):
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
            print(f"Il mese e l'anno non corrispondono. Mese trovato: {input_month_number}, anno: {input_year_number}")
            
            # Premere il pulsante per aggiornare il mese
            button = driver.find_element(By.ID, 'ID_DEL_TUO_BOTTONE')  # Sostituisci con l'ID reale del pulsante
            button.click()

        # Aspettare che il nuovo contenuto HTML sia caricato (aspetta fino a 10 secondi)
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, 'cartellinoformperiodo:dateRef'))  # Attendi che l'elemento che vuoi sia ricaricato
            )
            # Rileggere il nuovo valore dopo l'aggiornamento della pagina
            updated_input_value = driver.find_element(By.ID, 'cartellinoformperiodo:dateRef').get_attribute('value')
            #print(f"Nuovo mese dopo aggiornamento: {updated_input_value}")
        except Exception as e:
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
        for span in span_elements:
            if day_search in span.text:
                #print(f"Tag trovato: {span.get_attribute('outerHTML')}")
                
                # Now search for the next 4 <span> elements (entro 1, esco 1, entro 2, esco 2)
                # Get the parent <td> element where the current span is located
                parent_element = span.find_element(By.XPATH, './ancestor::td')

                # Find the next 4 <span> elements that contain the time entries
                # We use XPath to find all subsequent <td> elements and within them <span> with class 'iceOutTxt'
                next_spans = parent_element.find_elements(By.XPATH, './following::td//span[@class="iceOutTxt"]')[:4]

                # Extract the times from these spans
                if next_spans:
                    time_entries = []
                    for idx, next_span in enumerate(next_spans, start=1):
                        time_entry = next_span.text
                        if time_entry == '' or time_entry == '00:00':
                            time_entry = None
                        #print(f"Time {idx}: {time_entry}", file=sys.stderr)
                        time_entries.append(time_entry)
                    for time_entry in time_entries:
                        if time_entry is not None:
                            print(f'{time_entry}', end=' ')
                else:
                    print("No time spans found after the matched day.")

                # Exit after processing the first match
                break
        else:
            print("Today tag not found on web page")

        # Chiudere il browser
        driver.quit()



if __name__ == "__main__":
    auto_clocking = AutoClocking('.aaiuser', '.aaipass', '.clockurl')
    auto_clocking.get_clocking()

