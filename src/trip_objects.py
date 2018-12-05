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

    def is_delayed(self):
        # this attribute should be tracked as items are appended
        for stop_time_update in self.stop_time_updates:
            if stop_time_update.arrival_delay > 0 or stop_time_update.departure_delay > 0:
                return True
        return False

    def cumulative_arrival_delay(self):
        # this attribute should be tracked as items are appended
        retval = 0
        for stop_time_update in self.stop_time_updates:
            if stop_time_update.arrival_delay > 0:
                retval += stop_time_update.arrival_delay
        return retval

    def maximum_arrival_delay(self):
        # this attribute should be tracked as items are appended
        retval = 0
        for stop_time_update in self.stop_time_updates:
            if stop_time_update.arrival_delay > retval:
                retval = stop_time_update.arrival_delay
        return retval

    def average_arrival_delay(self):
        # this attribute should be tracked as items are appended
        return self.cumulative_arrival_delay() / len(self.stop_time_updates)
        
    def cumulative_departure_delay(self):
        # this attribute should be tracked as items are appended
        retval = 0
        for stop_time_update in self.stop_time_updates:
            if stop_time_update.departure_delay > 0:
                retval += stop_time_update.departure_delay
        return retval

    def maximum_departure_delay(self):
        # this attribute should be tracked as items are appended
        retval = 0
        for stop_time_update in self.stop_time_updates:
            if stop_time_update.departure_delay > retval:
                retval = stop_time_update.departure_delay
        return retval
        
    def average_departure_delay(self):
        # this attribute should be tracked as items are appended
        return self.cumulative_departure_delay() / len(self.stop_time_updates)

    def overall_schedule_relationship(self):
        # this attribute should be tracked as items are appended
        for stop_time_update in self.stop_time_updates:
            if stop_time_update.schedule_relationship == 3:
                return 3
            if stop_time_update.schedule_relationship == 2:
                return 2
            if stop_time_update.schedule_relationship == 1:
                return 1
        return 0


class NetworkTrips:
    def __init__(self):
        self.trip_updates = []
        self.time_started = time.localtime()
