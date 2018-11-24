from google.transit import gtfs_realtime_pb2
import urllib

# https://developers.google.com/transit/gtfs-realtime/examples/python-sample

feed = gtfs_realtime_pb2.FeedMessage()
req = urllib.request.Request('https://api.transport.nsw.gov.au/v1/gtfs/vehiclepos/sydneytrains')
f = open("credentials.txt", 'r')
apikey = f.read()
req.add_header('Authorization', 'apikey ' + apikey)
response = urllib.request.urlopen(req)
feed.ParseFromString(response.read())
for entity in feed.entity:
    print(entity)
