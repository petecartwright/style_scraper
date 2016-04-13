from __future__ import print_function
from bs4 import BeautifulSoup
from urllib2 import urlopen
from time import sleep
from geocode_style import return_coords_and_formatted_address
import csv, codecs, cStringIO
import re
import MySQLdb


BASE_URL = "http://www.styleweekly.com/richmond/BestOf?category="

# collected this manually from the style pages
CATEGORY_IDS = {'2011':{'Goods and Services':'1462337'
                      'Food & Drink':'1462336',
                      'Arts & Culture':'1462335',
                      'Nightlife':'1462339',
                      'People, Politics, and Media':'1462340',
                      'Living and Recreation': '1462338'
                      },
               '2012':{'Goods and Services':'1462337'
                       'Food & Drink':'1462336',
                       'Arts & Culture':'1462335',
                       'Nightlife':'1462339',
                       'People and Places':'1712487'
                       },
               '2013':{'Goods and Services':'1462337'
                       'Food & Drink':'1462336',
                       'Arts & Culture':'1462335',
                       'Nightlife':'1462339',
                       'People and Places':'1712487'
                       },
               '2014':{'Goods and Services':'1462337'
                       'Food & Drink':'1462336',
                       'Arts & Culture':'1462335',
                       'Nightlife':'1462339',
                       'People and Places':'1712487'
                       },
               '2015':{'Goods and Services':'1462337'
                       'Food & Drink':'1462336',
                       'Arts & Culture':'1462335',
                       'Nightlife':'1462339',
                       'People and Places':'1712487'
                       }
               }
 
CATEGORY_SUFFIX = '&feature=&year='
# URL for a given category will look like BASE_URL+CATEGORY_IDS[i]+CATEGORY_SUFFIX+<year>


RESULT_URL = "http://www.styleweekly.com/richmond/BestOf?oid="

def create_soup(url):
    beaut_soup = BeautifulSoup(urlopen(url),"lxml")
    return beaut_soup

def add_to_database(category_data):
    db = MySQLdb.connect(host='localhost',
                         user='<<>>',
                         passwd='<<>>',
                         db='<<>>',
                         charset='utf8',    # There were emdashes in a couple of the records.  This tells mysql to use unicode/utf8, which is cool with emdashes.
                         use_unicode='true')
    c = db.cursor()
    

    category = category_data['category']
    print(category_data['category'])
    first_place = category_data['first_place']
    second_place = category_data['second_place']
    third_place = category_data['third_place']
    description = category_data['description']
    address = category_data['address']
    address_lat = category_data['address_lat']
    address_long = category_data['address_long']
    address_formatted = category_data['address_formatted']
    url = category_data['url']
    phone = category_data['phone']
    whose_pick = category_data['whose_pick']
    style_url = category_data['style_url']
    print(category_data['style_url'])
    year = category_data['year']
    
    try:
       c.execute("""INSERT into styleweekly (category, first_place, second_place, third_place, description, address, address_lat, address_long,address_formatted, url, phone, whose_pick, style_url, year)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s )""",(category, first_place, second_place, third_place, description, address, address_lat, address_long, address_formatted, url, phone, whose_pick, style_url, year))
       db.commit()
    except:
       db.rollback()
       raise
    finally:
       db.close()
       
    return category_data


def get_name_from_place_string(place_string):
    # Some of the places have a "First Place: " string in front of them, but not all of them
    
    if ":" in place_string:
        to_return = place_string[place_string.find(": ")+2:]
        return to_return
    else:
        return place_string
    

def get_list_of_links():

    # get the list of URLS for each category
    BASE_URLs = []
    for cat_id in CATEGORY_IDS:
    #    BASE_URLs.append(BASE_URL+cat_id+CATEGORY_SUFFIX+"2013")
    #   BASE_URLs.append(BASE_URL+cat_id+CATEGORY_SUFFIX+"2012")
       BASE_URLs.append(BASE_URL+cat_id+CATEGORY_SUFFIX+"2011")
    
    # now roll through each category and get all of the URLs for each winner
    category_links= []
    for url in BASE_URLs:
        soup = create_soup(url)
        narrowoptions = soup.findAll("ul","narrowOptions")[2]  # the list of links on the side is ul class    "narrowoptions"
        # skip the first one since we have that one
        i = 1
        for option in narrowoptions.findAll("li",):
            if i > 1:
               # print(option.a["href"])
                category_links.append(option.a["href"])
            i = i+1
            
    return category_links


def parse_address(address_list):
    """ Surprise, the address fields are inconsistently populated.  
        This tries to figure out what it is - URL, street address, or Phone #
    """
    print("parsing address")

    address = ''
    url = ''
    phone = ''
    address_lat = ''
    address_long = ''
    address_formatted = ''
    list = {}

    for item in address_list:
        #clear out the whitespace
        item = item.strip()
        phonePattern = re.compile(r'[0-9]{3}\D[0-9]{4}')
        urlPattern = re.compile(r'^[a-zA-Z0-9\-\.]+\.(com|org|net|mil|edu|us|biz|COM|ORG|NET|MIL|EDU|US|BIZ).*')
        # not bothering with an address regex because phones and URLs are easy to match and addresses aren't.  
        # If it's not a phone number or URL, we'll call it an address
    
        if phonePattern.search(item):
            phone = "804-" + phonePattern.search(item).group(0)  # this should append the actual part of the string that matches 
                                                        # rather than the entire string. using the first part if there are 
                                                        # multiple phone numbers in the string (River City Diner for example)
        elif urlPattern.search(item):
            url = item
        elif item != '':
            address = item + ", Richmond, VA"

    # I saw a large number of cases in 2012 where the address was in the format of something like "Address , phone number, url", 
    # so if we didn't get an address above and we have a comma in the first item in the address_list[], lets take what's in 
    # front of the comma and append RVA and see what happens

    if address == '' and address_list[0].find(',') != -1:
        address = address_list[0][:address_list[0].index(',')] + ", Richmond, VA"
        print(address)

    # if we have an address, lets get the geocode and google-formatted address
    if address != '':
        
        # imported from geocode_style
        geocode_dict = return_coords_and_formatted_address(address)
        address_lat = geocode_dict["address_lat"]
        address_long = geocode_dict["address_long"]
        address_formatted = geocode_dict["address_formatted"]
        
    list = {'address':address,
            'url':url,
            'phone':phone,
            'address_lat':address_lat,
            'address_long':address_long,
            'address_formatted':address_formatted
            }
    
    return list


def get_data_for_page(url):
    """ Get the category, first_place, second_place, 
        third_place, address, description, whose_pick fields for a given URL
    """
    soup = create_soup(url)
    style_url = url
    category = soup.find("h1","headline").text.strip()

    # some of these are critic's picks, some are reader's picks, this helps ID them
    # At least one had no pick identified, so we have this to check for bad data
    if soup.find(id="StoryFeatures"):
        whose_pick_intial = soup.find(id="StoryFeatures").find("h3").text.strip()
        whose_pick = whose_pick_intial[:whose_pick_intial.find("Pick")+4].strip()
    else:
        whose_pick = "Readers' Pick"

    first_place  = ''
    second_place = ''
    third_place  = ''
    address      = ''
    address_lat  = ''
    address_long = ''
    address_formatted  = ''
    url          = ''
    phone        = ''
    description  = ''
    year_initial = soup.find(id='BestOfSearchTerms').find("ul").find("li").text.strip()
    year = year_initial[year_initial.find("[X]")+3:].strip()
    
    if whose_pick == "Readers' Pick":

        # gets the header element under the div with page1 ID, then parses the actual name
        # 2013 - for some reason, a couple of these are h4 and some are h3.  I'm blaming Ned Oliver 
        # 2012 - the winners are under a different div

        if year == '2012':
            print("year is 2012")
            first_place  = get_name_from_place_string(soup.find("h2", "subheadline").text)

        elif year == '2013':
             
            if soup.find("div","page1").find("h3") is not None:
                first_place  = get_name_from_place_string(soup.find("div","page1").find("h3").text)
            elif soup.find("div","page1").find("h4") is not None:
                first_place  = get_name_from_place_string(soup.find("div","page1").find("h4").text)
            else:
                first_place = "...?"

        # Grab the body text of the story
        storyBody = soup.find(id="storyBody").findAll("p")
        
        # 2 cases here.  One - there are 4 <p> under storyBody.  ( addr, 2nd, 3rd, desc )
        #                Two - there are 3 <p> under storyBody (see Best Local Actor - no address!)  ( 2nd, 3rd, desc)
        if len(storyBody) >= 4:
            address_list = parse_address(storyBody[0].text.split("\n"))
            address = address_list['address']
            url = address_list['url']
            phone = address_list['phone']
            address_lat = address_list['address_lat']
            address_long = address_list['address_long']
            address_formatted = address_list['address_formatted']            
            second_place = get_name_from_place_string(storyBody[1].text).strip()
            
            # in at least one case, what should be the third place <p> also contains the description.
            # So we check for a newline, if there's a newline, everything before it goes to third place, everything after goes to description
            third_place  = get_name_from_place_string(storyBody[2].text).strip()
            if "\n" in third_place:
               newline_loc = third_place.index("\n")
               description = third_place[newline_loc+2:] # from the newline_loc to the end. +2 is because there are usually multiple newlines
               third_place = third_place[:newline_loc]   # from the beginning to the newline_loc 
            else:
                description = storyBody[3].text.strip()
            if len(storyBody) == 5:
                description += storyBody[4].text.strip()

        elif len(storyBody) == 3:
            second_place = get_name_from_place_string(storyBody[0].text).strip()
            third_place  = get_name_from_place_string(storyBody[1].text).strip()
            description = storyBody[2].text.strip()
        
    else :
        first_place  = 'Critic - unknown'
        second_place = 'Critic - unknown'
        third_place  = 'Critic - unknown'
        address      = 'Critic - fix later'
        description  = 'Critic - fix later' 

    page_data = {'category': category,
                 'first_place': first_place,
                 'second_place': second_place,
                 'third_place': third_place,
                 'description': description,
                 'address': address,
                 'address_lat':address_lat,
                 'address_long':address_long,
                 'address_formatted':address_formatted,                                  
                 'url':url,
                 'phone':phone,
                 'whose_pick': whose_pick,
                 'style_url': style_url,
                 'year': year}
    return page_data



all_links = get_list_of_links()

print(all_links)

