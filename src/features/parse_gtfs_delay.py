from google.transit import gtfs_realtime_pb2
import urllib.request
import pickle
import time
from trip_objects import *
import os
from dotenv import load_dotenv
import logging

logging.basicConfig(filename='../../data/train_delay_download.log', level=logging.INFO,
                    format='%(asctime)s %(message)s')


def unused_function():
    feed = gtfs_realtime_pb2.FeedMessage()
    feed.ParseFromString(response.read())
    logging.info("Found " + str(len(trips.trip_updates)) + " trips")
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

            trips.trip_updates.append(trip_update)

    pickle.dump(trips, open(data_dir + "/" + time.strftime("%H%M%S", trips.time_started) + ".pickle", "wb"))


if __name__ == "__main__":
    load_dotenv()
    data_dir = "../../data/" + time.strftime("%Y%m%d", time.localtime())
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    download_delayed_trips(data_dir)
