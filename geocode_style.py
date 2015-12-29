from urllib2 import urlopen # get the ability to open URLs
import csv                  # working with the list of places from last time
import json                 # to read JSON
from time import sleep      # to pause


def geocode_address(address):
    """ Take an address and hit the google geocode api with it
    """
    print "In geocode"
    url = ("http://maps.googleapis.com/maps/api/geocode/json?"
        "sensor=false&address={0}".format(address.replace(" ", "+")))  # replace all the spaces with +'s
    return json.loads(urlopen(url).read())
    
    
def return_coords_and_formatted_address(address):
    
    result = geocode_address(address)
    address_dict ={}
    # check to see if it worked
    if result["status"] == u"OK":
        address_lat = result["results"][0]["geometry"]["location"]["lat"]
        address_long = result["results"][0]["geometry"]["location"]["lng"]
        address_formatted = result["results"][0]["formatted_address"]
    else:
        address_lat = ''
        address_long = ''
        address_formatted = ''
    
    print address_lat
    print address_long
    print address_formatted        
    
    address_dict = {'address_lat': address_lat,
                    'address_long': address_long,
                    'address_formatted': address_formatted}
    
    return address_dict