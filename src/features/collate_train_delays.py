import pickle
import time
from trip_objects import *
import os
from progress.bar import Bar
import sys
import logging
import glob
from google.transit import gtfs_realtime_pb2


def merge_trips(old_trip, new_trip):
    if old_trip.trip_id != new_trip.trip_id:
        return old_trip
    if old_trip.timestamp == new_trip.timestamp:
        # no updates
        return old_trip

    for new_stop_time_update in new_trip.stop_time_updates:
        foundStop = False
        for old_stop_time_update in old_trip.stop_time_updates:
            if old_stop_time_update.stop_id == new_stop_time_update.stop_id:
                # take the new one for now
                # if old_stop_time_update != new_stop_time_update:
                old_stop_time_update = new_stop_time_update
                foundStop = True
                old_trip.timestamp = new_trip.timestamp
                break
        if not foundStop:
            old_trip.stop_time_updates.append(new_stop_time_update)


def collate_train_delays(data_dir, dest_data_dir):
    logging.info("Merging delays in " + data_dir + " to " + dest_data_dir)

    # TODO filter the files to those with actual time strings
    files = glob.glob(data_dir + '/*.pickle')

    bar = Bar('Merging files', max=len(files))
    merged_trips = []

    for delay_data_file in files:
        bar.next()
        try:
            current_delay_response = pickle.load(open(delay_data_file, "rb"))
        except:
            continue  # next file
        
        feed = gtfs_realtime_pb2.FeedMessage()
        feed.ParseFromString(current_delay_response)
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

                # merge with current trips
                found_trip = False
                for merged_trip in merged_trips:
                    if trip_update.trip_id == merged_trip.trip_id:
                        found_trip = True
                        merged_trip = merge_trips(merged_trip, trip_update)
                        break

                if not found_trip:
                    merged_trips.append(trip_update)

    bar.finish()

    pickle.dump(merged_trips, open(dest_data_dir + "/collated_delays.pickle", "wb"))
    logging.info("Found " + str(len(merged_trips)) + " trips")


if __name__ == "__main__":
    # run in own directory
    os.chdir(os.path.dirname(sys.argv[0]))
    source_data_dir = "../../data/raw/" + time.strftime("%Y%m%d", time.localtime())
    destination_data_dir = "../../data/interim/" + time.strftime("%Y%m%d", time.localtime())
    if not os.path.exists(destination_data_dir):
        os.makedirs(destination_data_dir)
    log_dir = '../../data/logs/'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    logging.basicConfig(filename=log_dir+'train_collate_delays.log', level=logging.INFO,
                        format='%(asctime)s %(message)s')
    collate_train_delays(source_data_dir, destination_data_dir)
