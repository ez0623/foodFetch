	# gets data from anteatery menu for today
import requests
from datetime import date
from bs4 import BeautifulSoup
import json

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
    # deli, desert, traditions, grill, round grill, oven, produce market, saute, soups, daily feature
    
    #### pulls headers

    # for header in headers:
    #     if 'section-subtitle' in header['class']:
    #         menu[header.text] = {}
    
    def header_and_items(tag):
        headitem = (tag.has_attr('class') and 'section-subtitle' in tag['class']) or (tag.has_attr('class') and 'viewItem' in tag['class'])
        iteminfo = (tag.has_attr('class') and 'item__calories' in tag['class']) or (tag.has_attr('class') and 'item__content' in tag['class'])
        return headitem or iteminfo

    info = soup.find_all(header_and_items)

    for item in info:
        if 'section-subtitle' in item['class']:
            current_section = item.text
            menu[current_section] = {}
        else:
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
    i = input('Enter meal (BREAKFAST/BRUNCH/LUNCH/DINNER/LATENIGHT): ')
    if i:
        try:
            payload = get_url(eval(i))
        except NameError:
            print(f'INVALID INPUT: {i}')
            exit()
        result = requests.get('https://uci.campusdish.com/en/LocationsAndMenus/TheAnteatery?', params = payload)
        if result.status_code == 200:
            menu_dict = scrape(result)
            print(menu_dict)
        else:
            print('ERROR: Could not access menu')
    else:
        day_menu ={}
        # implement date selection
        day = date.today()
        ########################
        date = day.strftime('%m/%d/%Y')
        for i in ('Breakfast', 'Brunch', 'Lunch', 'Dinner', 'Latenight'):
            payload = get_url(eval(i.upper()), date)
            result = requests.get('https://uci.campusdish.com/en/LocationsAndMenus/TheAnteatery?', params = payload)
            day_menu[i] = scrape(result)
        print(day_menu)

        #json
        with open(f'{day.strftime("%m_%d_%Y")}.json', 'x') as fp:
            json.dump(day_menu, fp)