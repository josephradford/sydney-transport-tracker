import urllib
import time

class StopTimeUpdate:
    def __init__(self, stop_id, arrival_delay, departure_delay, schedule_relationship):
        self.arrival_delay = arrival_delay
        self.departure_delay = departure_delay
        self.stop_id = stop_id
        self.schedule_relationship = schedule_relationship

    def __eq__(self, other):
        """Overrides the default implementation"""
        if isinstance(other, StopTimeUpdate):
            return ((self.arrival_delay == other.arrival_delay) and
                    (self.departure_delay == other.departure_delay) and
                    (self.stop_id == other.stop_id) and
                    (self.schedule_relationship == other.schedule_relationship))

        return NotImplemented

    def __ne__(self, other):
        """Overrides the default implementation (unnecessary in Python 3)"""
        x = self.__eq__(other)
        if x is not NotImplemented:
            return not x
        return NotImplemented

class TripUpdate:
    def __init__(self, trip_id, route_id, schedule_relationship, timestamp):
        self.stop_time_updates = []
        self.trip_id = trip_id
        self.route_id = route_id
        self.schedule_relationship = schedule_relationship
        self.timestamp = timestamp

class NetworkTrips:
    def __init__(self):
        self.trip_updates = []
        self.time_started = time.localtime()
