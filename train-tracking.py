from google.transit import gtfs_realtime_pb2
import urllib
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# https://developers.google.com/transit/gtfs-realtime/examples/python-sample

# The goal of this script is to record delays against stops and trips ids and route ids
# Each pass through, see if delays have changed for the same runs
# do delays get removed from the list once trains has passed through, or do they remain?
# For now can leave every stop and run as the ID, don't need to map to sensible names until later

# stop_id | service A | service B |
# A       | 10        | N/A       |
# B       | N/A       | 2         |

# N/A might mean no delay or stop is not part of service. can fill that in with timetable later

try:
    df = pd.read_pickle('foo.pkl')
except FileNotFoundError:
    df = pd.DataFrame()

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
            stop_ids = []
            delays = []
            for stop_time_update in entity.trip_update.stop_time_update:
                if stop_time_update.departure.delay > 0:
                    stop_ids.append(stop_time_update.stop_id)
                    delays.append(stop_time_update.departure.delay)
            if len(delays) > 0:
                s = pd.Series(delays, index=stop_ids, name=entity.id)
                df2 = pd.DataFrame(s, dtype=int)
                #if len(df) == 0:
                #    df = df2
                #else:
                #    df = pd.concat([df, df2], axis=1, sort=True)
                print(entity)
