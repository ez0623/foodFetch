# gets data from anteatery menu for today
import requests
from bs4 import BeautifulSoup
import json
import sys
import re
import os

# period IDs
BREAKFAST = 49
BRUNCH = 2651
LUNCH = 106
DINNER = 107
LATENIGHT = 108

def get_url(id, date):
    return {'locationId' : 3056, 'storeIds' : '', 'mode' : 'Daily', 'date' : date, 'periodId' : id}

def scrape(result, daily=True):
    # print(result.headers)
    src = result.content
    soup = BeautifulSoup(src, 'lxml')

    menu = {}
    menu_section = soup.find_all(id='menuDailyDiv')
    
    def header_and_items(tag):
        headitem = (tag.has_attr('class') and 'section-subtitle' in tag['class']) or (tag.has_attr('class') and 'viewItem' in tag['class'])
        iteminfo = (tag.has_attr('class') and 'item__calories' in tag['class']) or (tag.has_attr('class') and 'item__content' in tag['class'])
        return headitem or iteminfo

    info = soup.find_all(header_and_items)
    current_section = ''

    for item in info:
        if 'section-subtitle' in item['class']:
            current_section = item.text
            menu[current_section] = {}
        elif current_section:
            if 'viewItem' in item['class']:
                current_item = item.text
                menu[current_section][current_item] = {}
            else:
                try:
                    if 'item__calories' in item['class']:
                        menu[current_section][current_item]['Calories'] = int(item.text.split(' ')[0])
                    elif 'item__content' in item['class']:
                        menu[current_section][current_item]['Description'] = item.text
                except KeyError:
                    continue
    return menu
    
        
if __name__ == '__main__':
    if  len(sys.argv) > 2 and str(sys.argv[2]) == 'ant':  
        loc = 'TheAnteatery'
    elif len(sys.argv) > 2 and str(sys.argv[2]) == 'brandy':
        loc = 'Brandywine'
    elif len(sys.argv) == 2:
        loc = 'TheAnteatery'
    elif len(sys.argv) > 2:
        print('INVALID LOCATION')
        exit()
    else:
        print('ENTER DATE')
        exit()

    date_pattern = re.compile(r'^(0[1-9]|1[012])[- /.] (0[1-9]|[12][0-9]|3[01])[- /.] (19|20)\d\d$.')
    day_string = str(sys.argv[1])

    if not re.match(date_pattern, day_string):
        day_menu ={}
        for i in ('Breakfast', 'Brunch', 'Lunch', 'Dinner', 'Latenight'):
            payload = get_url(eval(i.upper()), day_string)
            result = requests.get(f'https://uci.campusdish.com/en/LocationsAndMenus/{loc}?', params = payload)
            if result.status_code == 200:
                print(f'Getting data for {loc} {i}')
                day_menu[i] = scrape(result)
            else:
                print(f'Could not access: {i} for {loc}')
        #json
        try:
            os.mkdir('./data')
            fp = open((r'./data/' + f'Creating {day_string.replace("/", "-")}_{loc}_menu.json'), 'x', encoding = 'utf-8')
        except FileExistsError:
            fp = open((r'./data/' + f'Creating {day_string.replace("/", "-")}_{loc}_menu.json'), 'w', encoding = 'utf-8')
        json.dump(day_menu, fp, ensure_ascii=False, indent=4)
        fp.close()
    else:
        print('INVALID DATE FORMAT')