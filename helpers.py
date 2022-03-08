import argparse
import datetime
import json

import pytz

from timezones import timezones_data


def hello_user():

    parser = argparse.ArgumentParser()

    parser.add_argument('-c', '--choose_action', help='Choose data base or compare action', type=str, choices={'first_db', 'second_db', 'compare'})
    parser.add_argument('source', help='Source airport', type=str)
    parser.add_argument('destination', help='Destination airport', type=str)
    parser.add_argument('passengers_types', help='Passengers list: adult, child, infant', nargs='+', choices={'adult', 'child', 'infant'}, type=str)

    arguments = parser.parse_args()

    action = arguments.choose_action
    source = arguments.source
    destination = arguments.destination
    passengers = arguments.passengers_types

    if action == 'first_db':
        file_name = 'RS_ViaOW.xml'
    if action == 'second_db':
        file_name = 'RS_ViaOW.xml'
    if action == 'compare':
        file_name = 'both'

    return file_name, source, destination, passengers


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

def load_return(data_dictionary):

    with open('return.json', 'w') as save_file:
        json.dump(data_dictionary, save_file, indent=3)
        print('Data loaded to return.json')