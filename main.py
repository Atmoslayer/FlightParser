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
        return None

    elif destination not in destination_airports:
        print(f'Airport {destination} is missing in destination airports')
        return None

    else:
        print(f'There are {len(founded_flights)} flights founded')
        return founded_flights




def find_variants(founded_flights, passengers):


    if founded_flights:

        all_prices = []
        ratio_list = []
        ratio_dictionary = {}
        passenger_category = 'price_{passenger}'
        flight_times = []
        variants_info_list = []

        for founded_flight in founded_flights:

            flight_price = 0

            for passenger in passengers:

                flight_price += float(founded_flight[passenger_category.format(passenger=passenger)])

            all_prices.append(flight_price)

            flight_times.append(founded_flight['flight_time'])


    max_price = float(max(all_prices))
    min_price = float(min(all_prices))
    max_time = float(str(max(flight_times)).replace(':','.', 1).replace(':','', 1))
    min_time = float(str(min(flight_times)).replace(':','.', 1).replace(':','', 1))

    for flight_quantity in range(len(founded_flights)):

        ratio = all_prices[flight_quantity] / min_price + flight_times[flight_quantity] / min_time
        ratio_list.append(ratio)

    for ratio_number in range(len(ratio_list)):
        ratio_dictionary[ratio_list[ratio_number]] = founded_flights[ratio_number]

    sorted_info = sorted(ratio_dictionary.items(), key=lambda x: x[0])

    variants_dictionary = dict(sorted_info)

    for params_quantity in range(len(all_prices)):
        if all_prices[params_quantity] == max_price:
            variants_dictionary['expensive_flight'] = founded_flights[params_quantity]
        if all_prices[params_quantity] == min_price:
            variants_dictionary['cheap_flight'] = founded_flights[params_quantity]
        if flight_times[params_quantity] == max_time:
            variants_dictionary['long_flight'] = founded_flights[params_quantity]
        if all_prices[params_quantity] == min_time:
            variants_dictionary['short_flight'] = founded_flights[params_quantity]



    return variants_dictionary

# def find_optimal(maxmin_dictionary, passengers, founded_flights):
#
#
#     ratio_list = []
#     ratio_dictionary = {}
#     flight_price = 0
#
#     for flight in founded_flights:
#
#         for passenger in passengers:
#
#             passenger_category = 'price_{passenger}'
#             flight_price += float(flight[passenger_category.format(passenger=passenger)])
#
#
#         ratio = flight_price / float(maxmin_dictionary['min_price']) + float(flight['flight_time']) / float(maxmin_dictionary['min_time'])
#         ratio_list.append(ratio)
#
#     for ratio_number in range(len(ratio_list)):
#         ratio_dictionary[ratio_list[ratio_number]] = founded_flights[ratio_number]
#
#     sorted_info = sorted(ratio_dictionary.items(), key=lambda x: x[0])
#     rating_dictionary = dict(sorted_info)
#
#
#
#     return rating_dictionary



if __name__ == '__main__':

    data_base_dictionary = xml_to_dictionary('RS_ViaOW.xml')
    source = input('Sourse: ')
    destination = input('Destination: ')
    founded_flights = find_flight(source, destination, data_base_dictionary)
    passengers = []

    try:
        passengers_quantity = int(input('Passengers quantity: '))
        for passenger in range(passengers_quantity):
            new_passenger = input('Passanger: ')
            passengers.append(new_passenger)


        variants_dictionary = find_variants(founded_flights, passengers)
        print(variants_dictionary)

        # rating = (find_optimal(maxmin_dictionary, passengers, founded_flights))

    #     for flight in rating:
    #         print(rating[flight])
    except ValueError:
        print('Please, enter integer')





