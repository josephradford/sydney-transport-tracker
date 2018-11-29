import pickle
import time
from trip_objects import *
import os

def merge_trips(old_trip, new_trip):
    if old_trip.trip_id != new_trip.trip_id:
        return old_trip
    for new_stop_time_update in new_trip.stop_time_updates:
        foundStop = False
        for old_stop_time_update in old_trip.stop_time_updates:
            if old_stop_time_update.stop_id == new_stop_time_update.stop_id:
                # take the new one for now
                old_stop_time_update = new_stop_time_update
                foundStop = True
                break
        if not foundStop:
            old_trip.stop_time_updates.append(new_stop_time_update)
    



def collate_train_delays(data_dir):
    files = os.listdir(data_dir)
    merged_trips = []
    trips = NetworkTrips()
    for delay_data_file in files:
        try:
            trips = pickle.load(open(data_dir + "/" + delay_data_file, "rb" ))
        except:
            continue # next file
        
        for new_trip in trips.trip_updates:
            foundTrip = False
            for merged_trip in merged_trips:
                if merged_trip.trip_id == new_trip.trip_id:
                    foundTrip = True
                    merged_trip = merge_trips(merged_trip, new_trip)
                    break

            if foundTrip == False:
                merged_trips.append(new_trip)

    print("Found " + str(len(merged_trips)) + " trips")

if __name__== "__main__":
    data_dir = "data/" + time.strftime("%Y%m%d", time.localtime())
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    collate_train_delays(data_dir)
