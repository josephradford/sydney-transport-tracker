import pickle
import time
from trip_objects import *
import os
from progress.bar import Bar
import pandas as pd
import numpy as np
import datetime

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
                #if old_stop_time_update != new_stop_time_update:
                old_stop_time_update = new_stop_time_update
                foundStop = True
                old_trip.timestamp = new_trip.timestamp
                break
        if not foundStop:
            old_trip.stop_time_updates.append(new_stop_time_update)
    
def collate_train_delays(data_dir):
    print("Merging files in " + data_dir)
    files = os.listdir(data_dir)
    merged_trips = []

    bar = Bar('Merging files', max=len(files))

    for delay_data_file in files:
        try:
            trips = pickle.load(open(data_dir + "/" + delay_data_file, "rb" ))
        except:
            continue # next file
        
        if not hasattr(trips, 'trip_updates'):
            continue

        for new_trip in trips.trip_updates:
            foundTrip = False
            for merged_trip in merged_trips:
                if merged_trip.trip_id == new_trip.trip_id:
                    foundTrip = True
                    merged_trip = merge_trips(merged_trip, new_trip)
                    break

            if foundTrip == False:
                merged_trips.append(new_trip)

        bar.next()

    bar.finish()

    pickle.dump(merged_trips, open(data_dir + "/collated_delays.pickle", "wb" ))
    print("Found " + str(len(merged_trips)) + " trips")

def create_real_timetable(data_dir, date_of_analysis):
    data_dir = data_dir + date_of_analysis

    # load the static timetable into a data frame
    df_stop_times = pd.read_csv(data_dir + '/stop_times.txt', header=0, encoding='utf-8-sig')
       
    # load the trip ids of that actual trips that happend on this day
    df_trips = pd.read_pickle(data_dir + '/trips_' + date_of_analysis + '.pickle')

    # remove any trips from stop_times that did NOT happen on this date
    df_stop_times = df_stop_times[df_stop_times['trip_id'].isin(df_trips['trip_id'])]

    # insert actual arrival, actual departure, and cancellation states into dataframe
    df_stop_times.insert(3, 'actual_arrival_time', 0)
    df_stop_times.insert(4, 'actual_departure_time', 0)
    df_stop_times.insert(5, 'schedule_relationship', 0)

    # load all delays found on this date
    trip_delays = pickle.load(open(data_dir + "/collated_delays.pickle", "rb" ))

    bar = Bar('Analyse trips', max=len(trip_delays))
    for trip in trip_delays:
        if not trip.is_delayed() and trip.overall_schedule_relationship() == 0:
            continue
        if not trip.trip_id in df_trips['trip_id'].values:
            print("Trip " + trip.trip_id + " was not supposed to run today!")
            continue
            
        df_trip_rows = df_stop_times[df_stop_times['trip_id'] == trip.trip_id]
        for stop_time_update in trip.stop_time_updates:
            df_row = df_trip_rows[df_trip_rows['stop_id'] == int(stop_time_update.stop_id)]
            # some of these values might be 24:00, 25:00 etc to signfiy next day

            if df_row.empty:
                # it shouldn't be
                continue

            actual_arrival_time = update_time(date_of_analysis, df_row['arrival_time'].item(), stop_time_update.arrival_delay)
            actual_departure_time = update_time(date_of_analysis, df_row['departure_time'].item(), stop_time_update.departure_delay)

            df_row.loc[0,'actual_arrival_time'] = actual_arrival_time
            df_row.loc[0,'actual_departure_time'] = actual_departure_time

            df_row.loc[0,'schedule_relationship'] = stop_time_update.schedule_relationship

            #print(df_row)
        bar.next()

    bar.finish()

    print(df_stop_times)

def update_time(date_of_analysis, time_str, delay_val):
    delay_val = int(delay_val)
    original_time = time.mktime(time.strptime(date_of_analysis + time_str, "%Y%m%d%H:%M:%S"))
    updated_time = original_time + delay_val
    updated_time = time.localtime(updated_time)
    return time.strftime("%H:%M:%S", updated_time)


if __name__== "__main__":
    data_dir = "data/" + time.strftime("%Y%m%d", time.localtime())
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    collate_train_delays(data_dir)
