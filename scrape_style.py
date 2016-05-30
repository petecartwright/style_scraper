from bs4 import BeautifulSoup
from urllib2 import urlopen
from time import sleep
from geocode_style import return_coords_and_formatted_address
import create_db

import os
import sys
import re



# Some terms:
#     Category = one of the 5 (or 6 in 2011) high level categories the awards are grouped into
#     Award = the individual awards (Best Hair Salon, Best Choice for Virginia's Official State Song, etc)
#     Critic's Pick = They've got of bunch of totes rando awards like "Best Hope for An Art Theater" and "Best Way To Make it For Yourself (not really)"
#                     These will be denoted as critic's pick and usually discarded from any analysis

CATEGORY_BASE_URL = "http://www.styleweekly.com/richmond/BestOf?category="

# collected this manually from the style pages
CATEGORIES_BY_YEAR = {'2011':{'Goods and Services':'1462337',
                              'Food & Drink':'1462336',
                              'Arts & Culture':'1462335',
                              'Nightlife':'1462339',
                              'People, Politics, and Media':'1462340',
                              'Living and Recreation': '1462338'
                               },
                      '2012':{'Goods and Services':'1462337',
                              'Food & Drink':'1462336',
                              'Arts & Culture':'1462335',
                              'Nightlife':'1462339',
                              'People and Places':'1712487'
                              },
                      '2013':{'Goods and Services':'1462337',
                              'Food & Drink':'1462336',
                              'Arts & Culture':'1462335',
                              'Nightlife':'1462339',
                              'People and Places':'1712487'
                              },
                      '2014':{'Goods and Services':'1462337',
                              'Food & Drink':'1462336',
                              'Arts & Culture':'1462335',
                              'Nightlife':'1462339',
                              'People and Places':'1712487'
                              },
                      '2015':{'Goods and Services':'1462337',
                              'Food & Drink':'1462336',
                              'Arts & Culture':'1462335',
                              'Nightlife':'1462339',
                              'People and Places':'1712487'
                              }
                      }

CATEGORY_SUFFIX = '&feature=&year='
# URL for a given category will look like CATEGORY_BASE_URL+CATEGORY_IDS[i]+CATEGORY_SUFFIX+<year>

RESULT_URL = "http://www.styleweekly.com/richmond/BestOf?oid="


def create_soup(url):
    beaut_soup = BeautifulSoup(urlopen(url),"lxml")
    return beaut_soup


# def add_to_database(category_data):
#     db = MySQLdb.connect(host='localhost',
#                          user='<<>>',
#                          passwd='<<>>',
#                          db='<<>>',
#                          charset='utf8',    # There were emdashes in a couple of the records.  This tells mysql to use unicode/utf8, which is cool with emdashes.
#                          use_unicode='true')
#     c = db.cursor()


#     category = category_data['category']
#     print category_data['category']
#     first_place = category_data['first_place']
#     second_place = category_data['second_place']
#     third_place = category_data['third_place']
#     description = category_data['description']
#     address = category_data['address']
#     address_lat = category_data['address_lat']
#     address_long = category_data['address_long']
#     address_formatted = category_data['address_formatted']
#     url = category_data['url']
#     phone = category_data['phone']
#     whose_pick = category_data['whose_pick']
#     style_url = category_data['style_url']
#     print category_data['style_url']
#     year = category_data['year']

#     try:
#        c.execute("""INSERT into styleweekly (category, first_place, second_place, third_place, description, address, address_lat, address_long,address_formatted, url, phone, whose_pick, style_url, year)
#                 VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s )""",(category, first_place, second_place, third_place, description, address, address_lat, address_long, address_formatted, url, phone, whose_pick, style_url, year))
#        db.commit()
#     except:
#        db.rollback()
#        raise
#     finally:
#        db.close()

#     return category_data


def get_name_from_place_string(place_string):
    # Some of the places have a "First Place: " string in front of them, but not all of them

    if ":" in place_string:
        to_return = place_string[place_string.find(": ")+2:]
        return to_return
    else:
        return place_string


def parse_address(address_list):
    """ Surprise, the address fields are inconsistently populated.
        This tries to figure out what it is - URL, street address, or Phone #
    """
    print "parsing address"

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
    """ Get the award_name, first_place, second_place,
        third_place, address, description, whose_pick fields for a given URL
    """
    print 'getting Soup for {0}'.format(url)
    soup = create_soup(url)
    style_url = url

    award_name = soup.find("h1","headline").text.strip()
    
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
            first_place  = get_name_from_place_string(soup.find("h2", "subheadline").text)
        else:

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

    page_data = {'award_name': award_name,
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

    # print page_data
    print 'done'

    return page_data


################################################################################################
################################################################################################
################################################################################################
################################################################################################



def get_award_urls_from_page(category_id, year):
    ''' take a category id and a year
        return a list of URLs for each award in that category
    '''
    print 'getting URLs for {0} from {1}'.format(category_id, year)
    # get the list of URLS for each award in each category in each year
    all_award_urls = []

    category_url = CATEGORY_BASE_URL + category_id + CATEGORY_SUFFIX + year

    # the main page for the category ALSO is the page for the first award
    all_award_urls.append(category_url)

    soup = create_soup(category_url)
    category_list_items = soup.findAll("ul","narrowOptions")[2].findAll("li")  # the list of links on the side is the third ul#narrowoptions
    for c in category_list_items:
        # if we have a link, add it to our list!
        if c.a:
            all_award_urls.append(c.a["href"])

    return all_award_urls


def scrape_award(session=None, award=None):
    ''' Takes a session and an Award object and fills in the data
    '''
    pass

def get_all_award_urls():
    s = create_db.get_session()

    for year in CATEGORIES_BY_YEAR:
        for category in CATEGORIES_BY_YEAR[year]:
            category_id = CATEGORIES_BY_YEAR[year][category]
            all_urls_in_category = get_award_urls_from_page(category_id=category_id, year=year)
            for u in all_urls_in_category:
                # check to see if we have it already
                awards = s.query(create_db.Award).filter(create_db.Award.url==u).first()
                if not awards:
                    new_award = create_db.Award()
                    new_award.url = u
                    new_award.category = category
                    new_award.year = year
                    s.add(new_award)
                    try:
                        s.commit()
                    except Exception:
                        print 'error!'
                        s.rollback()




def get_data_for_all_awards():
    s = create_db.get_session()
    all_awards = s.query(create_db.Award).all()

    for x in all_awards:
        if not x.award_name:
            data = get_data_for_page(x.url)
            
            x.award_name        = data['award_name']
            x.first_place       = data['first_place']
            x.second_place      = data['second_place']
            x.third_place       = data['third_place']
            x.description       = data['description']
            x.address           = data['address']
            x.address_lat       = data['address_lat']
            x.address_long      = data['address_long']
            x.address_formatted = data['address_formatted']
            x.phone             = data['phone']
            x.whose_pick        = data['whose_pick']
            x.style_url         = data['style_url']

            s.add(x)
            s.commit()
            # wait a bit so we're not sending 1000 requests 
            sleep(random.randrange(1, 9)/10.00)
