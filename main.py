import sys
import threading
from datetime import date, datetime
from typing import Any

import keyboard
import requests
import re
import time

from bs4 import BeautifulSoup, Tag

from helper import load_env, write_file, read_file, connect_smtp, send_email, close_smtp


def get_table_data(element: Tag, css_class: str) -> str:
    return element.find('div', {'class': css_class}).get_text(strip=True)

# Retrieve table data from website's table
def get_table() -> dict[Any, Any] | None:
    website = requests.get('https://szigbp.edupage.org/substitution').text

    table_data = re.search(r'"report_html":"((?:[^"\\]|\\.)*)"', website, re.DOTALL)

    if table_data and re.search("Erre a napra nincs megadva helyettesítés", website) is None:
        substitutions = []
        table = BeautifulSoup(table_data.group(1).replace(r'\"', '"'), 'html.parser')

        for section in table.find_all('div', {'class': 'section'}):
            name_of_class = get_table_data(section, 'header')
            rows = []

            for row in section.find_all('div', {'class': 'row'}):
                period = get_table_data(row, 'period')
                info = get_table_data(row, 'info')
                rows.append([period, info]) # from period and info create an array

            substitutions.append({name_of_class: rows}) # put the rows array in multidimensional array

        # Convert to a dictionary and return it
        return {list(entry.keys())[0]: list(entry.values())[0] for entry in substitutions}
    else:
        return None

exit_flag = False

def check_exit():
    global exit_flag
    while not exit_flag:
        if keyboard.is_pressed('esc'):
            print("Kilépés a folyamatból...")
            exit_flag = True
        time.sleep(0.1)  # Small sleep to reduce CPU usage

# Start the exit checking thread
exit_thread = threading.Thread(target=check_exit)
exit_thread.start()

if __name__ == '__main__':
    print("A futás megállításához nyomd meg az ESC billentyűt")

    load_env()
    server = connect_smtp()
    now = datetime.now()

    while not exit_flag:
        if now.weekday() < 5 and 5 <= now.hour < 15: # weekday(): 0-4 for Monday-Friday
            all_substitutions = get_table()
            addresses = read_file('addresses.txt', 'json')  # in case we need to add new address

            for name_of_class in addresses:
                substitutions = all_substitutions.get(name_of_class)
                file_path = f'substitution{name_of_class}{str(date.today())}.txt'
                old_substitutions = read_file(file_path)

                write_file(file_path, str(substitutions))

                if bool(substitutions) and old_substitutions != str(substitutions):
                    email_body = ""
                    for period, substitute in substitutions:
                        email_body += f'{period}. óra {substitute}\n'

                    for email in addresses[name_of_class]:
                        send_email(server, f'Helyettesítés {name_of_class}: {str(date.today())}', email_body, email)

        # Sleep for 30 minutes but check every 10 seconds
        for _ in range(180):  # 180 iterations for 10 seconds each
            if exit_flag:
                break
            time.sleep(10)

    close_smtp(server)
    exit_thread.join()
    print("A folyamat leállítva.")
    sys.exit()