import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime

page = requests.get("https://www.hemnet.se/salda/bostader?sold_age=all")
#page = requests.get("https://www.hemnet.se/salda/bostader?page=9113&sold_age=all")
soup = BeautifulSoup(page.content, 'html.parser')
properties = soup.find_all('div', class_='sold-property-listing')

def main(link):
    print("Booting up the crawler...")
    current_page = get_page(link)
    count=1
    while  count <= 43: # page!= ""
    
        #Do something cool
        #Extract all objects from the page
        #Extract information about each object
        #Store information in dataframe or numpy array
        
        current_page = get_page(find_next_page(current_page))
        if count%10 ==0:
            print(f"Crawled {count} pages")
        count+=1
    return (print(f"Total pages crawled: {count}"))

def get_page(link):
    page = requests.get(link)
    return BeautifulSoup(page.content, 'html.parser')

def find_next_page(page):
    link=page.select("div a.next_page.button.button--primary")
    if not link:
        return("")
    return ("https://www.hemnet.se" + link[0].get("href"))
#"https://www.hemnet.se" + 

def check_all_properties(soup):
    properties = soup.find_all('div', class_='sold-property-listing')
    propertyList = []
    for property_ in properties:
        propertyList.append(check_property(property_))
    return propertyList

def check_property(property_):
    lst = []
    lst.append(get_property_type(property_))
    lst.append(get_yard_size(property_))
    lst.append(get_rooms(property_))
    lst.append(get_squaremeter_price(property_))
    lst.append(get_fee(property_))
    lst.append(get_address(property_))
    lst.append(get_city(property_))
    lst.append(get_city_area(property_))
    lst.append(get_sales_date(property_))
    lst.append(get_broker(property_))
    #Gör en append för varje datapunkt
    return lst

def get_property_type(property_):
    property_type = property_.select("div.sold-property-listing__location span.svg-icon__fallback-text")[0].get_text(strip=True)
    if not property_type:
        return("")
    else:
        return (property_type)

def get_yard_size(property_):
    yard_size = property_.select("div.sold-property-listing__land-area.sold-property-listing--left")
    if not yard_size:
        return ("")
    return re.sub("[^\\d]","",yard_size[0].get_text(strip=True))


def get_rooms(property_):
    rooms = property_.select("div.sold-property-listing__size div.clear-children div")
    if not rooms:
        return ("")
    else:
        rooms = rooms[0].get_text(strip=True).replace('\xa0','').replace(' ','').replace("\n","")
        if not rooms:
            return ""
        else:
            return re.search("(\d+,?\d?)rum",rooms)[1]
        #return int(re.match("[\d]+",string=rooms).group(0))
        #return re.search(".*(\d+)rum.*",rooms)[1]
        #return rooms
        
#FUNKAR EJ
def get_squaremeter_price(property_):
    size = property_.select("div.sold-property-listing__price-per-m2 sold-property-listing--left")[0].get_text(strip=True)
    size_to_return = size.replace('\xa0','').replace(' ','')
    return (size_to_return)
    #return int(re.match("(\d+)",size_to_return).group(0))

def get_fee(property_):
    fee = property_.select("'div.sold-property-listing__fee'")
    if not fee:
        return ("")
    return int(re.match('\d+',fee[0].get_text(strip=True).replace('\xa0','')).group(0))

def get_address(property_):
    #address = property_.find_all(lambda tag: tag.name =='span'and tag.get('class') == ['item-result-meta-attribute-is-bold.item-link'])
    address = property_.select("span.item-result-meta-attribute-is-bold.item-link")
    return (address[0].get_text(strip=True))

def get_city(property_):
    city = property_.select("div.sold-property-listing__location div")[0]
    if city.span:
        city.span.decompose()
        if city.span:
            city.span.decompose()
    return city.get_text(strip=True)

def get_city_area(property_):
    city_area = property_.find_all(lambda tag: tag.name =='span'and tag.get('class') == ['item-link'])
    return city_area[0].get_text(strip=True).replace(",","")

#############
def get_price_development(property_):
    development = property_.select("div.sold-property-listing__price-change")[0].get_text(strip=True).replace("%","")
    try: 
        return 1+float(development)/100
    except Exception:
        return ""
    else:
        return ""
############

def get_end_price(property_):
    finalPrice = property_.select("div.sold-property-listing__price div.clear-children")[0].get_text(strip=True)
    endPrice = finalPrice.replace('\xa0','').replace(' ','')
    return int(re.match('(\D+)(\d+)(\D+)',endPrice).group(2))
               
def get_sales_date(property_):
    salesDate = property_.select("'div.sold-property-listing__sold-date'")[0].get_text(strip=True)
    salesDate = salesDate.replace('Såld','').replace('\xa0','').replace(' ','')
    monthTranslate = re.match('(\d+)(\D+)(\d+)',salesDate).group(2)
    salesDate = salesDate.replace(monthTranslate,get_sales_date_month_translator(monthTranslate.upper()))
    convertedDateTime = datetime.strptime(salesDate,'%d%B%Y')
    return (convertedDateTime.strftime('%Y-%m-%d'))

def get_sales_date_month_translator(month_):
    if month_ =="JANUARI":
        return "January"
    elif month_ == "FEBRUARI":
        return "February"
    elif month_ == "MARS":
        return "March"
    elif month_ == "APRIL":
        return "April"
    elif month_ == "MAJ":
        return "May"
    elif month_ == "JUNI":
        return "June"
    elif month_ == "JULI":
        return "July"
    elif month_ == "AUGUSTI":
        return "August"
    elif month_ == "SEPTEMBER":
        return "September"
    elif month_ == "OKTOBER":
        return "October"
    elif month_ == "NOVEMBER":
        return "November"
    elif month_ == "DECEMBER":
        return "December"
    else:
        return month_

def get_broker(property_):
    '''accepts any property and returns the broker'''
    broker = property_.select("'div.sold-property-listing__broker'")[0].get_text(strip=True)
    return (broker)

def test_function(function,properties):
    '''accepts any of the "get" functions and a list of all properties, use the "properties" list defined in the top'''
    return [function(properties[i]) for i in list(range(len(properties)))]

def test_function2(function,properties):
    for i in range(len(properties)):
        print(i)
        print(function(properties[i]))
        '''accepts any of the "get" functions and a list of all properties, use the "properties" list defined in the top'''
    return

str1 = '69\xa0m²\n          \xa0\n            3\xa0rum'
str2 = '5\xa0rum'

#dateTry = "22October2017"
#monthTranslate = re.match('(\d+)(\D+)(\d+)',dateTry).group(2)
#print(monthTranslate)
#convertDateTime = datetime.strptime(dateTry,'%d%B%Y')
#print(convertDateTime.strftime('%Y-%m-%d'))
#clear-children
#

#

#


    
    #return re.match("\d+",strToReturn).group(0)


    #return int(filter(str.isdigit,str(fee)))
#<div class="sold-property-listing__subheading sold-property-listing--left">
   #         63&nbsp;m²
  #        &nbsp;
    #        3&nbsp;rum
   #     </div>
#    return int(re.match("^\d+\s?\d?\d+$",string=fee).group(0))
    #b52'
    #import string
    #all=string.maketrans('','')
    #nodigs=all.translate(all, string.digits)
    #fee.translate(all, nodigs)

#search-results > li:nth-child(26) > div > div.sold-property-listing__size > div.clear-children > div
#    return


#search-results > li:nth-child(27) > div > div.sold-property-listing__location > h2 > span.item-result-meta-attribute-is-bold.item-link

#[print(get_property_type(properties[a])) for a in range(1,25)]
    
#a=soup.select("div.sold-property-listing__location div")
#search-results > li:nth-child(6) > div > div.sold-property-listing__location > div
 
#properties = soup.find_all('div', class_='sold-property-listing')

#search-results > li:nth-child(4) > div > div.sold-property-listing__location > div > span.item-link