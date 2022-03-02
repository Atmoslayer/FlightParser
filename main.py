from bs4 import BeautifulSoup
import json
import datetime
import pytz
from timezones import timezones_data

def xml_to_dictionary(file_name):

    data_base_dictionary = {}

    with open(file_name) as data_base:
        data = data_base.read()

    parsed_data = BeautifulSoup(data, 'lxml')

    all_carriers = parsed_data.find('airfaresearchresponse').find_all('carrier')
    all_flight_numbers = parsed_data.find('airfaresearchresponse').find_all('flightnumber')
    all_sources = parsed_data.find('airfaresearchresponse').find_all('source')
    all_destinations = parsed_data.find('airfaresearchresponse').find_all('destination')
    all_classes = parsed_data.find('airfaresearchresponse').find_all('class')
    all_numbers_of_stops = parsed_data.find('airfaresearchresponse').find_all('numberofstops')
    all_ticket_types = parsed_data.find('airfaresearchresponse').find_all('tickettype')


    all_arrival_times = parsed_data.find('airfaresearchresponse').find_all('arrivaltimestamp')
    all_departure_times = parsed_data.find('airfaresearchresponse').find_all('departuretimestamp')
    all_sources_timezone = []
    all_destinations_timezone = []
    all_times = []


    for source_quantity in range(len(all_sources)):

            source = all_sources[source_quantity].text
            departure_time_obj = datetime.datetime.strptime(all_departure_times[source_quantity].text, '%Y-%m-%dT%H%M')
            for timezone in timezones_data:
                if timezone == source:
                    source_timezone = timezones_data[timezone]
            departure_timezone = pytz.timezone(source_timezone)
            departure_time_zoned = departure_timezone.localize(departure_time_obj)
            all_sources_timezone.append(departure_time_zoned)

    for source_quantity in range(len(all_destinations)):

            destination = all_destinations[source_quantity].text
            arrival_time_obj = datetime.datetime.strptime(all_arrival_times[source_quantity].text, '%Y-%m-%dT%H%M')
            for timezone in timezones_data:
                if timezone == destination:
                    destination_timezone = timezones_data[timezone]
            arrival_timezone = pytz.timezone(destination_timezone)
            arrival_time_zoned = arrival_timezone.localize(arrival_time_obj)
            all_destinations_timezone.append(arrival_time_zoned)


    for times_quantity in range(len(all_sources_timezone)):

        departure_time_zoned_decoded = all_sources_timezone[times_quantity]
        arrival_time_zoned_decoded = all_destinations_timezone[times_quantity]
        flight_time = float(str(arrival_time_zoned_decoded - departure_time_zoned_decoded).replace(':','.', 1).replace(':','', 1))

        all_times.append(flight_time)


    all_prices_adult = []
    all_prices_child = []
    all_prices_infant = []

    for carrier in all_carriers:
        all_prices_adult.append(carrier.find_next('servicecharges', chargetype='TotalAmount', type='SingleAdult'))
        all_prices_child.append(carrier.find_next('servicecharges', chargetype='TotalAmount', type='SingleChild'))
        all_prices_infant.append(carrier.find_next('servicecharges', chargetype='TotalAmount', type='SingleInfant'))

    for flights_quantity in range(len(all_carriers)):

        data_base_dictionary[flights_quantity] = {'carrier': all_carriers[flights_quantity].text,
                                                    'flight_number': all_flight_numbers[flights_quantity].text,
                                                    'source_airport': all_sources[flights_quantity].text,
                                                    'destination_airport': all_destinations[flights_quantity].text,
                                                    'flight_time': all_times[flights_quantity],
                                                    'flight_class': all_classes[flights_quantity].text,
                                                     'number_of_stops': all_numbers_of_stops[flights_quantity].text,
                                                    'ticket_type': all_ticket_types[flights_quantity].text,
                                                    'price_adult': all_prices_adult[flights_quantity].text,
                                                    'price_child': all_prices_child[flights_quantity].text,
                                                    'price_infant': all_prices_infant[flights_quantity].text}

    return data_base_dictionary


def find_flight(source, destination, data_base_dictionary):

    source_airports = []
    destination_airports = []
    founded_flights = []

    for flight in range(len(data_base_dictionary)):

        source_airports.append(data_base_dictionary[flight]['source_airport'])
        destination_airports.append(data_base_dictionary[flight]['destination_airport'])


        if data_base_dictionary[flight]['source_airport'] == source and data_base_dictionary[flight]['destination_airport'] == destination:

            founded_flights.append(data_base_dictionary[flight])

    if source not in source_airports:
        print(f'Airport {source} is missing in sourse airports')
        return founded_flights

    if destination not in destination_airports:
        print(f'Airport {destination} is missing in destination airports')
        return founded_flights

    return founded_flights


def find_max_min_variants(founded_flights, passangers, data_base_dictionary):

    maxmin_dictionary = {}
    if founded_flights != []:
        if founded_flights:

            all_prices = []
            flight_times = []
            max_price = 0
            min_price = 0

            for passenger in passangers:

                for flights_quantity in range(len(data_base_dictionary)):
                    for founded_flights_quantity in range(len(founded_flights)):

                        dictionary_flight_number = (data_base_dictionary[flights_quantity]['flight_number'])
                        founded_flight_number = (founded_flights[founded_flights_quantity]['flight_number'])

                        if dictionary_flight_number == founded_flight_number:
                            passenger_category = 'price_{passenger}'
                            all_prices.append(data_base_dictionary[flights_quantity][passenger_category.format(passenger=passenger)])
                            flight_times.append(data_base_dictionary[flights_quantity]['flight_time'])



            max_time = max(flight_times)
            min_time = min(flight_times)
            max_time = float(str(max_time).replace(':','.', 1).replace(':','', 1))
            min_time = float(str(min_time).replace(':','.', 1).replace(':','', 1))
            max_price += float(max(all_prices))
            min_price += float(min(all_prices))


        maxmin_dictionary['max_price'] = max_price
        maxmin_dictionary['min_price'] = min_price
        maxmin_dictionary['max_time'] = max_time
        maxmin_dictionary['min_time'] = min_time

    return maxmin_dictionary

def find_optimal(maxmin_dictionary, founded_flights):


    ratio_list = []
    ratio_dictionary = {}

    for flight in founded_flights:
        ratio = (float(flight['price_adult']) / float(maxmin_dictionary['min_price']) + float(flight['flight_time']) / float(maxmin_dictionary['min_time']))
        ratio_list.append(ratio)

    for ratio_number in range(len(ratio_list)):
        ratio_dictionary[ratio_list[ratio_number]] = founded_flights[ratio_number]

    sorted_info = sorted(ratio_dictionary.items(), key=lambda x: x[0])
    rating_dictionary = dict(sorted_info)


    return rating_dictionary




if __name__ == '__main__':

    data_base_dictionary = xml_to_dictionary('RS_ViaOW.xml')
    source = input('Sourse: ')
    destination = input('Destination: ')
    founded_flights = find_flight(source, destination, data_base_dictionary)
    passangers = []

    try:
        passengers_quantity = int(input('Passengers quantity: '))
        for passanger in range(passengers_quantity):
            passangers.append(input('Passanger: '))

        maxmin_dictionary = find_max_min_variants(founded_flights, passangers, data_base_dictionary)

        rating = (find_optimal(maxmin_dictionary, founded_flights))

        for flight in rating:
            print(rating[flight])
    except ValueError:
         print('Please, enter integer')





