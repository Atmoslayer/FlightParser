from bs4 import BeautifulSoup
import json
import datetime
import pytz
from timezones import timezones_data


def hello_user():

    choices = [1, 2, 3]
    got_param = False

    while not (got_param):

        try:
            user_choice = int(input('Which data base to use? (1 - RS_ViaOW.xml, 2 - RS_Via-3.xml, compare)\n'))
        except ValueError:
            print('Please enter integer: 1, 2 or 3')

        if user_choice not in choices:
            print('Please enter 1, 2 or 3')
        elif user_choice == 1:
            file_name = 'RS_ViaOW.xml'
            got_param = True
        elif user_choice == 2:
            file_name = 'RS_Via-3.xml'
            got_param = True
        elif user_choice == 3:
            file_name = 'We use both'
            got_param = True

    return file_name


def remove_repetitions(data_base_dictionary):

    purified_data_base_dictionary = {}
    flight_number = 0

    for flight_index in data_base_dictionary:

        if data_base_dictionary[flight_index] not in purified_data_base_dictionary.values():
            purified_data_base_dictionary[flight_number] = data_base_dictionary[flight_index]
            flight_number += 1

    return purified_data_base_dictionary


def convert_flight_time(all_airports, all_times):
    all_airport_timezone = []
    for airport_quantity in range(len(all_airports)):
        airport = all_airports[airport_quantity].text
        time_obj = datetime.datetime.strptime(all_times[airport_quantity].text, '%Y-%m-%dT%H%M')
        for timezone in timezones_data:
            if timezone == airport:
                airport_timezone = timezones_data[timezone]
        time_timezone = pytz.timezone(airport_timezone)
        time_time_zoned = time_timezone.localize(time_obj)
        all_airport_timezone.append(time_time_zoned)
    return all_airport_timezone


def compare_data_base(first_data_base, second_data_base):

    both_data_base_dictionary = {}

    print('It can take some time...')

    first_data_base_dictionary = xml_to_dictionary(first_data_base)
    second_data_base_dictionary = xml_to_dictionary(second_data_base)

    for first_flight_index in first_data_base_dictionary:

        first_carrier = first_data_base_dictionary[first_flight_index]['carrier']
        first_flight_number = first_data_base_dictionary[first_flight_index]['flight_number']
        first_source = first_data_base_dictionary[first_flight_index]['source_airport']
        first_destination = first_data_base_dictionary[first_flight_index]['destination_airport']

        for second_flight_index in second_data_base_dictionary:

            second_carrier = second_data_base_dictionary[second_flight_index]['carrier']
            second_flight_number = second_data_base_dictionary[second_flight_index]['flight_number']
            second_source = second_data_base_dictionary[second_flight_index]['source_airport']
            second_destination = second_data_base_dictionary[second_flight_index]['destination_airport']

            if first_carrier == second_carrier and first_flight_number == second_flight_number and first_source == second_source and first_destination == second_destination:
                both_data_base_dictionary[first_flight_index] = {'first_db': first_data_base_dictionary[first_flight_index],
                                                                 'second_db': second_data_base_dictionary[second_flight_index]}

    purified_data_base_dictionary = remove_repetitions(both_data_base_dictionary)

    return purified_data_base_dictionary


def xml_to_dictionary(file_name):

    data_base_dictionary = {}

    try:

        with open(file_name) as data_base:
            data = data_base.read()

    except FileNotFoundError:

        return None

    parsed_data = BeautifulSoup(data, 'lxml')

    all_carriers = parsed_data.find('airfaresearchresponse').find_all('carrier')
    all_flight_numbers = parsed_data.find('airfaresearchresponse').find_all('flightnumber')
    all_sources = parsed_data.find('airfaresearchresponse').find_all('source')
    all_destinations = parsed_data.find('airfaresearchresponse').find_all('destination')
    all_classes = parsed_data.find('airfaresearchresponse').find_all('class')
    all_numbers_of_stops = parsed_data.find('airfaresearchresponse').find_all('numberofstops')
    all_ticket_types = parsed_data.find('airfaresearchresponse').find_all('tickettype')

    all_departure_times = parsed_data.find('airfaresearchresponse').find_all('departuretimestamp')
    all_arrival_times = parsed_data.find('airfaresearchresponse').find_all('arrivaltimestamp')
    all_times = []

    all_sources_timezoned = convert_flight_time(all_sources, all_departure_times)
    all_destinations_timezoned = convert_flight_time(all_destinations, all_arrival_times)

    for times_quantity in range(len(all_sources_timezoned)):

        departure_time_zoned_decoded = all_sources_timezoned[times_quantity]
        arrival_time_zoned_decoded = all_destinations_timezoned[times_quantity]
        flight_time = float(str(arrival_time_zoned_decoded - departure_time_zoned_decoded).replace(':','.', 1).replace(':','', 1))

        all_times.append(flight_time)


    all_prices_adult = []
    all_prices_child = []
    all_prices_infant = []

    for carrier in all_carriers:

        all_prices_adult.append(carrier.find_next('servicecharges', chargetype='TotalAmount', type='SingleAdult').text)
        try:
            all_prices_child.append(carrier.find_next('servicecharges', chargetype='TotalAmount', type='SingleChild').text)
        except AttributeError:
            all_prices_child.append(None)
        try:
            all_prices_infant.append(carrier.find_next('servicecharges', chargetype='TotalAmount', type='SingleInfant').text)
        except AttributeError:
            all_prices_infant.append(None)


    for flights_quantity in range(len(all_carriers)):

        data_base_dictionary[flights_quantity] = {'carrier': all_carriers[flights_quantity].text,
                                                    'flight_number': all_flight_numbers[flights_quantity].text,
                                                    'source_airport': all_sources[flights_quantity].text,
                                                    'destination_airport': all_destinations[flights_quantity].text,
                                                    'departure_time': all_departure_times[flights_quantity].text,
                                                    'arrival_time': all_arrival_times[flights_quantity].text,
                                                    'flight_time': all_times[flights_quantity],
                                                    'flight_class': all_classes[flights_quantity].text,
                                                     'number_of_stops': all_numbers_of_stops[flights_quantity].text,
                                                    'ticket_type': all_ticket_types[flights_quantity].text,
                                                    'price_adult': all_prices_adult[flights_quantity],
                                                    'price_child': all_prices_child[flights_quantity],
                                                      'price_infant': all_prices_infant[flights_quantity]}

    purified_data_base_dictionary = remove_repetitions(data_base_dictionary)

    return purified_data_base_dictionary


def find_flight(source, destination, data_base_dictionary):

    if data_base_dictionary is not None:

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
        variants_dictionary = {}
        flight_times = []

        for founded_flight in founded_flights:

            flight_price = 0
            category_found = True

            for passenger in passengers:

                price = founded_flight[f'price_{passenger}']
                if price is not None:
                    flight_price += float(founded_flight[f'price_{passenger}'])
                else:
                    category_found = False
                    flight_price += float(founded_flight[f'price_adult'])

            all_prices.append(flight_price)

            flight_times.append(founded_flight['flight_time'])

    max_price = float(max(all_prices))
    min_price = float(min(all_prices))
    max_time = float(str(max(flight_times)).replace(':', '.', 1).replace(':', '', 1))
    min_time = float(str(min(flight_times)).replace(':', '.', 1).replace(':', '', 1))

    for flight_quantity in range(len(founded_flights)):

        ratio = all_prices[flight_quantity] / min_price + flight_times[flight_quantity] / min_time
        ratio_list.append([str(ratio), founded_flights[flight_quantity]])


    sorted_ratio_list = sorted(ratio_list, key=lambda ratio: ratio[0])

    for rated_flight_index in range(len(sorted_ratio_list)):

        variants_dictionary[f'top_{rated_flight_index + 1}'] = sorted_ratio_list[rated_flight_index][1]

    for params_quantity in range(len(all_prices)):

        if all_prices[params_quantity] == max_price:
            variants_dictionary['expensive_flight'] = founded_flights[params_quantity]
        if all_prices[params_quantity] == min_price:
            variants_dictionary['cheap_flight'] = founded_flights[params_quantity]
        if flight_times[params_quantity] == max_time:
            variants_dictionary['long_flight'] = founded_flights[params_quantity]
        if flight_times[params_quantity] == min_time:
            variants_dictionary['short_flight'] = founded_flights[params_quantity]

    if not category_found:
        print(f'If no price data for child/infant price for adult used')

    return variants_dictionary


if __name__ == '__main__':

    data_base_name = hello_user()
    if data_base_name == 'We use both':
        data_base_dictionary = compare_data_base('RS_ViaOW.xml', 'RS_Via-3.xml')
        print(data_base_dictionary)

    else:
        data_base_dictionary = xml_to_dictionary(data_base_name)
        if data_base_dictionary is not None:
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

                for info in variants_dictionary:
                    print(variants_dictionary[info])

            except ValueError:
                print('Please, enter integer')



