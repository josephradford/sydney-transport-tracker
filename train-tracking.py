from google.transit import gtfs_realtime_pb2
import urllib

# https://developers.google.com/transit/gtfs-realtime/examples/python-sample

# The goal of this script is to record delays against stops and trips ids and route ids

feed = gtfs_realtime_pb2.FeedMessage()
req = urllib.request.Request('https://api.transport.nsw.gov.au/v1/gtfs/realtime/sydneytrains')
f = open("credentials.txt", 'r')
apikey = f.read()
req.add_header('Authorization', 'apikey ' + apikey)
response = urllib.request.urlopen(req)
feed.ParseFromString(response.read())
for entity in feed.entity:
    if entity.HasField('trip_update'):
        if len(entity.trip_update.stop_time_update) > 0:
            print(entity)
