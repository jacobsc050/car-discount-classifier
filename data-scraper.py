import pandas as pd
import urllib.request
from bs4 import BeautifulSoup
import requests

# URL to scrape data from
url = 'https://www.ttrepairables.com/inventory'

# Soupify the url
# html = urlopen(url)
# soup = BeautifulSoup(html,'lxml')
# print(soup)

# Soupify the url, but this time it doesn't not a 403 Forbidden error
user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
headers = {'User-Agent': user_agent, }
request = urllib.request.Request(url, None, headers)  # The assembled request
response = urllib.request.urlopen(request)
data = response.read()  # The data u need
soup = BeautifulSoup(data, 'lxml')

# Find and print all links
# all_links = soup.find_all('a')
# print(all_links)
# for link in all_links:
#     print(link.get('href'))

# Print the html title
# title = soup.title
# print(title)

# Print the html text
# text = soup.get_text()
# print(text)

# Find and print all links
# all_links = soup.find_all('a')
# print(all_links)
# for link in all_links:
#     print(link.get('href'))

# Find and print all tables
all_tables = soup.find_all('tr')
print(all_tables)

# Find and print the names/prices listed on the site
all_cars_names = soup.find_all('a', attrs={'class', 'inventory-photo'})
all_cars_description = soup.find_all('div', attrs={'style': 'text-align:left'})
all_cars_prices = soup.find_all('div', attrs={'class': 'accent-color1'})
all_cars_vin = soup.find_all('span', attrs={'class': 'vin'})
all_cars_stocknumber = soup.find_all('span', attrs={'class': 'stocknumber'})
all_cars_transmission = soup.find_all('div', attrs={'class': 'transmission'})
all_cars_engine = soup.find_all('div', attrs={'class': 'engine'})
all_cars_mileage = soup.find_all('span', attrs={'class': 'mileage'})
all_cars_url = soup.find_all('href', attrs={'class': 'inventory-photo'})

# Print the length of each list to determine if they're all the same
# print(len(all_cars_names))
# print(len(all_cars_description))
# print(len(all_cars_prices))
# print(len(all_cars_vin))
# print(len(all_cars_stocknumber))
# print(len(all_cars_transmission))
# print(len(all_cars_engine))
# print(len(all_cars_mileage))

# Create data frame to be filled with the car data
df = pd.DataFrame()

# Sample api request link for the VinAudit api
api_request = 'http://marketvalue.vinaudit.com/getmarketvalue.php?key=VA_DEMO_KEY&format=json&vin='

for i in range(len(all_cars_names) - 1):
    # Print the name, description, and VIN of each car from the ttrepairables website
    print(all_cars_names[i]['title'].strip())
    print(all_cars_description[i].text.strip())
    print('VIN:', all_cars_vin[i].text.strip())

    # Initialize dictionary to be appended to the pandas dataframe
    s = {'Car Name': str(all_cars_names[i]['title'].strip()),
         'url': str(all_cars_names[i]['href'].strip()),
         'Description': str(all_cars_description[i].text.strip()),
         'Year': int(all_cars_names[i]['title'].strip()[:5]),
         'VIN': str(all_cars_vin[i].text.strip())}

    # Get the title type from each car description
    if 'clean title' in all_cars_description[i].text.strip().lower():
        print('Title: Clean')
        s['Title'] = 'Clean'
    elif 'rebuilt' in all_cars_description[i].text.strip().lower():
        print('Title: Rebuilt')
        s['Title'] = 'Rebuilt'
    else:
        print('Title: Salvage')
        s['Title'] = 'Salvage'

    # Get data from the VinAudit website using the VIN of each car
    new_api_request = api_request + str(all_cars_vin[i].text)
    response = requests.get(new_api_request)
    data = response.json()

    # Print the miles listed on the VinAudit website based on the VIN
    try:
        print('Miles:', all_cars_mileage[i].text.strip(' miles!'))
        s['Miles'] = all_cars_mileage[i].text.strip(' miles!')
    except:
        print('Miles:', 'data not available')
        s['Miles'] = None

    # Print the listed price of each car from the ttrepeairables website
    print('Listed price:', all_cars_prices[i].text.strip())
    try:
        s['Listed Price'] = float(all_cars_prices[i].text.strip().replace('$', '').replace(',', ''))
    except:
        s['Listed Price'] = None

    # Try getting the average price data and calculate the savings
    try:
        print('Average Market Value: ', '$', int(data['prices'].get('average')), sep='')
        s['Average Market Value'] = data['prices'].get('average')
        if 'Sale Pending' not in all_cars_prices[i].text:
            print('Savings: ', '$', int(float(data['prices'].get('average')) - float(all_cars_prices[i].text.strip().replace('$', '').replace(',', ''))), sep='')
        else:
            continue
    except:
        print('Price data is unavailable')
        s['Average Market Value'] = None

    # Try to get transmission data
    try:
        print('Transmission:', all_cars_transmission[i].text.strip())
        s['Transmission'] = all_cars_transmission[i].text.strip()
    except:
        print('Transmission:', 'N/A')
        s['Transmission'] = None

    # Try to get engine data
    try:
        print('Engine:', all_cars_engine[i].text.strip(), '\n')
        s['Engine'] = all_cars_engine[i].text.strip()
    except:
        print('Engine:', 'N/A', '\n')
        s['Engine'] = None

    df = df.append(s, ignore_index=True)

    # print(all_cars_description[i].text.strip())
    # print('Stock number:', all_cars_stocknumber[i].text.strip())
    # print('Transmission type:', all_cars_transmission[i].text.strip())
    # print('Engine:', all_cars_engine[i].text.strip())
    # print('Miles:', all_cars_mileage[i].text.strip(), '\n')


print(df)
df.to_excel('car_data.xlsx', index=False)
