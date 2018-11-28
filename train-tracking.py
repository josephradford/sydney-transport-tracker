from google.transit import gtfs_realtime_pb2
import urllib
import pickle
import time

# https://developers.google.com/transit/gtfs-realtime/examples/python-sample

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

feed = gtfs_realtime_pb2.FeedMessage()
req = urllib.request.Request('https://api.transport.nsw.gov.au/v1/gtfs/realtime/sydneytrains')
f = open("credentials.txt", 'r')
apikey = f.read()
req.add_header('Authorization', 'apikey ' + apikey)
response = urllib.request.urlopen(req)
feed.ParseFromString(response.read())
trip_updates = []
time_started = time.time()
for entity in feed.entity:
    if entity.HasField('trip_update') and len(entity.trip_update.stop_time_update) > 0:
        trip_update = TripUpdate(entity.trip_update.trip.trip_id,
                                 entity.trip_update.trip.route_id,
                                 entity.trip_update.trip.schedule_relationship,
                                 entity.trip_update.timestamp)
        
        for stop_time_update in entity.trip_update.stop_time_update:
            trip_update.stop_time_updates.append(
                StopTimeUpdate(stop_time_update.stop_id,
                                stop_time_update.arrival.delay, 
                                stop_time_update.departure.delay,
                                stop_time_update.schedule_relationship))
        
        trip_updates.append(trip_update)
pickle.dump(trip_updates, open( str(time_started) + ".pickle", "wb" ))
