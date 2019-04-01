from bs4 import BeautifulSoup
import requests
import re
import sys 


# First n links
stop_point = 0
if len(sys.argv) > 1:
    stop_point = (int(sys.argv[1]))

# Main Url
url = 'https://www.lueftner-cruises.com/en/river-cruises/cruise.html'

headers = {
    'User-Agent': 'Mozilla/5.0',
}


cruise_list = []


# Make request with Mozilla user agent
response = requests.get(url, headers=headers)

# Save page
data = response.text

# create soup object
soup = BeautifulSoup(data, 'lxml')

# find all travel links 
all_cruises = soup.find_all('a', 'btn btn-primary hidden-xs')

for items in all_cruises:
    cruise_dict = { 'name' : '', 'days' : '', 'itinerary' : '', 'dates' : ''} # create dict and setup order 
    # request each link
    detail_response = requests.get('https://www.lueftner-cruises.com' + items.get('href'), headers=headers)
    detail_data = detail_response.text
    detail_soup = BeautifulSoup(detail_data, 'lxml')
    
    # Get  name using reg exp    // Omg
    format_string = detail_soup.find('h1', attrs={'style' :  'margin-top:0;'}).get_text().strip()
    m = re.findall('[a-zA-Z ]*', format_string)    
    cruise_dict['name'] = ''.join(m).strip()
    
    # Get days
    cruise_dict['days'] = detail_soup.find('p', 'cruise-duration', 'pull-right').get_text().strip().split(' ')[0]
    
    # Get Route List
    itinerary_data = detail_soup.find_all('span', 'route-city')
    itinerary_list = []

    for item in itinerary_data:
        # Reg exp here for work with  'town > town' existences
        it_reg = re.findall('[a-zA-Z ]*', item.text)
        itinerary_list.extend(''.join(it_reg).strip().split())
    
    cruise_dict['itinerary'] = itinerary_list
    
    # Get Date, Ship name and Price
    first_panel = detail_soup.find('div', attrs={'class' : 'panel-group accordion price accordeon-data-price'})

    inner_list = []

    for child in first_panel.children:
        get_link = child.find('a')

        # Check for remove wrong objects 
        if type(first_panel) == type(get_link):
            # Find Date, Ship name and Price
            dict_date = get_link.attrs['href'][9:17]
            dict_date = dict_date[:4] + '-' + dict_date[4:6] + '-' + dict_date[6:8]

            dict_ship = get_link.find(class_='table-ship-name').text
            dict_price = get_link.find(class_='big-table-font').text.strip()[2:]

            inner_list.append({ dict_date : { 'ship' : dict_ship, 'price' : dict_price}})


    cruise_dict['dates'] = inner_list
    cruise_list.append(cruise_dict)

    #
    stop_point -= 1
    if stop_point == 0:
        break

print(cruise_list)