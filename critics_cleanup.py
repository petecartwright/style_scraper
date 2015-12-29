from geocode_style import return_coords_and_formatted_address
import time

address_list = ['1809 Staples Mill Rd','3166 W Cary St','Shirley Ln','114 W Broad St','belle isle','1601 Willow Lawn Dr','3024 Stony Point Rd','2401 W Main St','11090 W Broad St','2601 W Cary St','5057 Forest Hill Ave ','3120 W Cary St','321 W 7th St','322 W Broad St','203 N Foushee St','1316 E Cary St','1201 E marshall','2916 W Cary St','214 E Broad St','6020 W Broad St','3110 W Leigh St','10150 Lakeridge Pkwy','11800 W Broad St #1040','12401 Jefferson Davis','15 N 1st St','103 E Cary St','2519 Grove Ave',' 4708 Old Main St','314 Dabney Rd','9125 W Broad St','428 N Boulevard','3107 W Cary St','27 W Broad St','11621 Robious Rd','7803 Midlothian Turnpike','528 N 2nd St','5704 Grove Ave','1124 Westbriar Dr','27 N Belmont Ave','1127 Gaskins Road','218 W Broad St','1021 E Cary St','1001 N Blvd','2001 Park Ave','2251 Old Brick Rd','320 E Grace St','6020 W Broad St','9204 Stony Point Pkwy','5875 Bremo Rd #400','6353 Mechanicsville Turnpike','10410 Ridgefield Pkwy','1800 Glenside Dr','8 S Harvie St','3800 Mountain Rd','416 E Grace St','101 W Franklin St','1601 Willow Lawn Dr','2201 Shields Lake Ct','140 Virginia St #200','14 S Allen Ave','3158 W Cary St','3012 W Cary St','2024 West Broad Street','200 North Robinson Street','7 N 17th St','1111 E Main St','2933 W Cary St','2314 Dabney Rd','2908 W Cary St','2361 Robious Station Cir','1411 E Cary St','8099 W Broad St']

finalized_address_list = []

for address in address_list:
    address = address + ", Richmond, VA"
    # imported from geocode_style
    geocode_dict = return_coords_and_formatted_address(address)
    address_lat = geocode_dict["address_lat"]
    address_long = geocode_dict["address_long"]
    address_formatted = geocode_dict["address_formatted"]
    address_array = [address_formatted, address_lat, address_long]
    finalized_address_list.append(address_array)
    time.sleep(0.1)

print(finalized_address_list)

