from dotenv import load_dotenv
import os
import requests


s = requests.Session()

# required for authorizing the header of the request
# get regenerated periodically and I don't know how to crack it
load_dotenv()
access_token = os.environ['ACCESS_TOKEN']

# name of the file where the data will be written
file = open('data5.txt', 'w')


# method for obtaining the get request as a json or None
def getResponse(url, parameters, headers):
    response = s.get(url, headers=headers, params=parameters)
    if response.status_code == 200:
        return response.json()
    else:
        return None

# header for get requests made to cpasso
# user agent can be modified according to need
cpasso_header = {
        'Host' 				: 'cppasso.mediatriple.net',
        'User-Agent' 		: 'Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0',
        'Accept' 			: 'application/json, text/plain, */*',
        'Accept-Language' 	: 'en-US,en;q=0.5',
        'Accept-Encoding' 	: 'gzip, deflate, br, zstd',
        'Content-Type' 		: 'text/plain',
        'Authorization' 	: f'Bearer {access_token}',
        'CurrentCulture'	: 'tr-TR',
        'Origin' 		    : 'https://www.passo.com.tr',
        'Connection' 		: 'keep-alive',
        'Referer' 		    : 'https://www.passo.com.tr/',
        'Sec-Fetch-Dest' 	: 'empty',
        'Sec-Fetch-Mode' 	: 'cors',
        'Sec-Fetch-Site' 	: 'cross-site',
        'DNT' 				: '1',
        'Sec-GPC' 			: '1',
        'TE' 				: 'trailers',
        }
# header for post requests made to tickettingweb
# user agent can be modified according to need
event_post_header = {
        'Host'              : 'ticketingweb.passo.com.tr',
        'User-Agent'        : 'Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0',
        'Accept'            : 'application/json, text/plain, */*',
        'Accept-Language'   : 'en-US,en;q=0.5',
        'Accept-Encoding'   : 'gzip, deflate, br, zstd',
        'Content-Type'      : 'application/json',
        'CurrentCulture'    : 'tr-TR',
        'Content-Length'    : '132',
        'Origin'            : 'https://www.passo.com.tr',
        'Connection'        : 'keep-alive',
        'Referer'           : 'https://www.passo.com.tr/',
        'Sec-Fetch-Dest'    : 'empty',
        'Sec-Fetch-Mode'    : 'cors',
        'Sec-Fetch-Site'    : 'same-site',
        'DNT'               : '1',
        'Sec-GPC'           : '1',
        'Priority'          : 'u=0',
        }

def getseats(event_id):

    # this was used to get the ticket type (which is set to e-ticket for football matches with the code 100)
    # this is now abondoned since it is usually not required to obtain the ticket data
    #tickettypeURL = 'https://cppasso.mediatriple.net/api/passoweb/gettickettypes'
    #tickettypeParams = {
    #        'eventId' : eventId,
    #        'serieId' : '',
    #        }
    #tickettype = getResponse(tickettypeURL, tickettypeParams, cpasso_header)
    #if tickettype:
    # tickettype = tickettype.get('valueList', [])[0].get('id')
    #else:
    #    tickettype = '100'

    # default id of e-tickets
    ticket_type_id = '100'
    
    # used to obtain the seat categories' ids in order to get their actual seat data afterwards
    seat_categories_url = 'https://cppasso.mediatriple.net/30s/api/passoweb/getcategories'
    seat_categories_params = {
            'eventId'                   : event_id,
            'serieId'                   : '',
            'tickettype'                : ticket_type_id,
            'campaignId'                : 'null',
            'validationintegrationid'   : 'null',
            }
    categories = getResponse(seat_categories_url, seat_categories_params, cpasso_header)
    if categories:
        categories = categories.get('valueList', [])
    
    # pre-set string to visualize seat data
    seats_string = ""
    
    # here we iterate through the seat categories and parse their available seat data
    available_seats_url = 'https://cppasso.mediatriple.net/30s/api/passoweb/getavailableblocklist'
    count = 0
    total_count = 0
    most_seats_available_string = ""
    if categories:
        most_available_seats = 0
        for category in categories:
            #print(str(category))
            #print(str(category.get('id')))
            available_seats_params = {
                    'eventId' : event_id,
                    'serieId' : '',
                    'seatCategoryId' : category.get('id'),
                    }
            seat_data_of_category = getResponse(available_seats_url, available_seats_params, cpasso_header)
            seats_string +="Category: " + category.get('name') + "\n"
            if seat_data_of_category:
                seat_data_of_category = seat_data_of_category.get('valueList', [])
                for category_info in seat_data_of_category :
                    count = category_info.get('totalCount')
                    seats_string += "Name: " + str(category_info.get('name')) + " || "
                    seats_string += "Available: " + str(count) + " || "
                    seats_string += "Price: " + str(category.get('price')) + "\n"
                    total_count += count
                    # determine which category has the most seats available
                    if count > most_available_seats:
                        most_available_seats = count
                        most_seats_available_string  = "Most available seat category:\n"
                        most_seats_available_string += "Name: " + str(category_info.get('name')) + " || "
                        most_seats_available_string += "Available: " + str(count) + " || "
                        most_seats_available_string += "Price: " + str(category.get('price')) + "\n"
            else:
                seats_string += "\tNo seat data available! Try updating your access token.\n"
    else:
        seats_string += "\tNo seat category data available! The info for the category might be restricted or try updating your access token.\n"
    print(most_seats_available_string)
    file.write(seats_string)
    file.write("Total count of available seats: " + str(total_count) + "\n")
    file.write(most_seats_available_string + "\n\n")


# used to fetch the event ids of all upcoming matches and get their seat data accordingly
all_events_url = 'https://ticketingweb.passo.com.tr/api/passoweb/allevents'
all_events_params = {
        "CountRequired"	: True,
        "HastagId"		: None,
        "CityId"		: None,
        "date"			: None,
        "VenueId"		: None,
        "GenreId"		: 4615,
        "LanguageId"	: 118 ,
        "from"			: 0,
        "size"			: 53
        }
events = s.post(all_events_url, headers=event_post_header, json=all_events_params).json().get('valueList', [])
for event in events:
    print(str(event.get('id')))
    # this is used to filter out football events that are not matches
    if not event.get('hideDate'):
        event_details = "Event: \n \tName: " + str(event.get('name'))
        event_details+= "\n\tDate: " + str(event.get('date')) + "\n\tHome Team: " +str(event.get('homeTeamName'))
        event_details+= "\n\tVenue: " + str(event.get('venueName')) + "\n"
        print(event_details)
        file.write(event_details)
        getseats(str(event.get('id')))
file.close()
