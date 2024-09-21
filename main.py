import os
import requests
import re
import json

from bs4 import BeautifulSoup

def get_table_data(element, css_class):
    return element.find('div', {'class': css_class}).get_text(strip=True)

# Retrieve table data from website's table
def get_table():
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


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print(get_table() if get_table() else "Nincs helyettesites")