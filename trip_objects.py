import urllib
import time

class StopTimeUpdate:
    def __init__(self, stop_id, arrival_delay, departure_delay, schedule_relationship):
        self.arrival_delay = arrival_delay
        self.departure_delay = departure_delay
        self.stop_id = stop_id
        self.schedule_relationship = schedule_relationship

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
        self.time_started = time.time()
