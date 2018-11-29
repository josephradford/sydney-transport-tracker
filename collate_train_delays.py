import pickle
import time
from trip_objects import *
import os

def collate_train_delays(data_dir):
    files = os.listdir(data_dir)
    all_trips = []
    trips = NetworkTrips()
    for delay_data_file in files:
        try:
            trips = pickle.load(open(data_dir + "/" + delay_data_file, "rb" ))
        except:
            continue #next file
        
        for new_trip in trips.trip_updates:
            foundTrip = False
            for all_trip in all_trips:
                if all_trip.trip_id == new_trip.trip_id:
                    foundTrip = True
                    break
                    # merge delays

            if foundTrip == False:
                all_trips.append(new_trip)

if __name__== "__main__":
    data_dir = "data/" + time.strftime("%Y%m%d", time.localtime())
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    collate_train_delays(data_dir)
