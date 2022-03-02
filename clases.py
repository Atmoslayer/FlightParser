class Ticket(object):

    def __init__(self, carrier, flight_number, source, destination, departure_time, arrival_time, ticket_class, number_of_stops, tickettype, price_adult, price_child, price_infant):

        self.carrier = carrier
        self.flightn_umber = flight_number
        self.source = source
        self.destination = destination
        self.departure_time = departure_time
        self.arrival_time = arrival_time
        self.ticket_class = ticket_class
        self.number_of_stops = number_of_stops
        self.tickettype = tickettype
        self.price_adult = price_adult
        self.price_child = price_child
        self.price_infant = price_infant

