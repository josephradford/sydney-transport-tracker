import os
import pandas as pd
import logging
import sys
import time
import pickle
from progress.bar import Bar
from datetime import datetime, timedelta


def create_real_timetable(_raw_data_dir, _interim_data_dir, date_of_analysis, collated_delays_filename):
    logging.info("Creating real timetable for " + date_of_analysis)

    # load the static timetable into a data frame
    df_stop_times = pd.read_csv(_raw_data_dir + '/stop_times.txt', header=0,
                                encoding='utf-8-sig',
                                dtype={'stop_id': str},
                                parse_dates=['arrival_time', 'departure_time'])
    # date_parser=dateparse)

    # load the trip ids of that actual trips that happened on this day
    df_trips = pd.read_pickle(_interim_data_dir + '/trips_' + date_of_analysis + '.pickle')

    # remove any trips from stop_times that did NOT happen on this date
    df_stop_times = df_stop_times[df_stop_times['trip_id'].isin(df_trips['trip_id'])]

    # insert actual arrival, actual departure, and cancellation states into dataframe
    # mark all as N/A to start with, so we know which things never had real time updates
    df_stop_times.insert(2, 'arrival_delay', 'N/A')
    df_stop_times.insert(3, 'actual_arrival_time', 'N/A')
    df_stop_times.insert(5, 'departure_delay', 'N/A')
    df_stop_times.insert(6, 'actual_departure_time', 'N/A')
    df_stop_times.insert(7, 'schedule_relationship', 'N/A')

    # load all delays found on this date
    trip_delays = pickle.load(open(_interim_data_dir + "/" + collated_delays_filename + ".pickle", "rb"))

    bar = Bar('Analyse trips', max=len(trip_delays))
    for trip in trip_delays.values():
        bar.next()
        if trip.trip_id not in df_trips['trip_id'].values:
            # print("Trip " + trip.trip_id + " was not supposed to run today!")
            continue

        for stop_time_update in trip.stop_time_updates.values():
            # some of these values might be 24:00, 25:00 etc to signify next day

            idx = df_stop_times[(df_stop_times['trip_id'] == trip.trip_id) &
                                (df_stop_times['stop_id'] == stop_time_update.stop_id)].index
            if idx.empty:
                # it shouldn't be
                continue

            idx = idx.item()

            # calculate the real time
            actual_arrival_time = update_time(date_of_analysis, df_stop_times.at[idx, 'arrival_time'],
                                              stop_time_update.arrival_delay)
            actual_departure_time = update_time(date_of_analysis, df_stop_times.at[idx, 'departure_time'],
                                                stop_time_update.departure_delay)

            # add the new values to the new columns

            df_stop_times.at[idx, 'arrival_delay'] = stop_time_update.arrival_delay
            df_stop_times.at[idx, 'actual_arrival_time'] = actual_arrival_time
            df_stop_times.at[idx, 'departure_delay'] = stop_time_update.departure_delay
            df_stop_times.at[idx, 'actual_departure_time'] = actual_departure_time
            df_stop_times.at[idx, 'schedule_relationship'] = stop_time_update.schedule_relationship

    bar.finish()

    df_stop_times.to_csv(_interim_data_dir + "/timetable_with_delays.csv")
    df_stop_times.to_pickle(_interim_data_dir + "/timetable_with_delays.pickle")
    logging.info("Pickled the real timetable in " + _interim_data_dir)


def create_trip_summaries(_raw_data_dir, _interim_data_dir, date_of_analysis, collated_delays_filename):
    logging.info("Creating real trip summaries for " + date_of_analysis)

    # load the trip ids of that actual trips that happened on this day
    df_trips = pd.read_pickle(_interim_data_dir + '/trips_' + date_of_analysis + '.pickle')

    # get the stop times for trips that happened this day
    df_stop_times = pd.read_pickle(_interim_data_dir + "/timetable_with_delays.pickle")

    # insert actual arrival, actual departure, and cancellation states into dataframe
    # mark all as N/A to start with, so we know which things never had real time updates
    df_trips.insert(0, 'start_timestamp', 'N/A')
    df_trips.insert(1, 'end_timestamp', 'N/A')
    df_trips.insert(6, 'maximum_arrival_delay', 0)
    df_trips.insert(7, 'average_arrival_delay', 0)
    df_trips.insert(8, 'maximum_departure_delay', 0)
    df_trips.insert(9, 'average_departure_delay', 0)
    df_trips.insert(10, 'schedule_relationship', 0)

    # load all delays found on this date
    trip_delays = pickle.load(open(_interim_data_dir + "/" + collated_delays_filename + ".pickle", "rb"))

    bar = Bar('Analyse trips', max=len(trip_delays))
    for trip in trip_delays.values():
        bar.next()
        if trip.trip_id not in df_trips['trip_id'].values:
            # print("Trip " + trip.trip_id + " was not supposed to run today!")
            continue

        idx = df_trips[(df_trips['trip_id'] == trip.trip_id)].index
        if idx.empty:
            # it shouldn't be
            continue

        idx = idx.item()

        df_trips.at[idx, 'maximum_arrival_delay'] = trip.maximum_arrival_delay()
        df_trips.at[idx, 'average_arrival_delay'] = trip.average_arrival_delay()
        df_trips.at[idx, 'maximum_departure_delay'] = trip.maximum_departure_delay()
        df_trips.at[idx, 'average_departure_delay'] = trip.average_departure_delay()
        df_trips.at[idx, 'schedule_relationship'] = trip.overall_schedule_relationship()

    bar.finish()

    bar = Bar('Add stop and start times', max=len(df_trips))
    for i in df_trips.index:
        bar.next()
        departure_series = df_stop_times[df_stop_times['trip_id'] == df_trips.at[i, 'trip_id']]['departure_time']
        df_trips.at[i, 'start_timestamp'] = convert_to_timestamp(date_of_analysis, departure_series.iloc[0])
        df_trips.at[i, 'end_timestamp'] = convert_to_timestamp(date_of_analysis, departure_series.iloc[-1])

    bar.finish()

    df_trips.to_csv(_interim_data_dir + "/trips_with_delays.csv")
    df_trips.to_pickle(_interim_data_dir + "/trips_with_delays.pickle")
    logging.info("Pickled the real trip summaries in " + _interim_data_dir)


def update_time(date_of_analysis, time_str, delay_val):
    try:
        delay_val = int(delay_val)
        original_time = time.mktime(time.strptime(date_of_analysis + time_str, "%Y%m%d%H:%M:%S"))
        updated_time = original_time + delay_val
        updated_time = time.localtime(updated_time)
        return time.strftime("%H:%M:%S", updated_time)
    except:
        return "Exception"


def convert_to_timestamp(date_of_analysis, time_str):
    hours = int(time_str[0:2])
    if hours > 23:
        time_str = '0' + str(hours-23) + time_str[2:]
        retval = datetime.strptime(date_of_analysis + time_str, "%Y%m%d%H:%M:%S")
        retval += timedelta(days=1)
        return retval
    else:
        retval = datetime.strptime(date_of_analysis + time_str, "%Y%m%d%H:%M:%S")
        return retval


def create_real_timetable_run(_raw_data_dir, _interim_data_dir, date_of_analysis, collated_delays_filename):
    create_real_timetable(_raw_data_dir, _interim_data_dir, date_of_analysis, collated_delays_filename)
    create_trip_summaries(_raw_data_dir, _interim_data_dir, date_of_analysis, collated_delays_filename)


if __name__ == "__main__":
    # run in own directory
    os.chdir(os.path.dirname(sys.argv[0]))
    raw_data_dir = "../../data/raw/" + time.strftime("%Y%m%d", time.localtime())
    interim_data_dir = "../../data/interim/" + time.strftime("%Y%m%d", time.localtime())
    log_dir = '../../data/logs/'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    logging.basicConfig(filename=log_dir+'train_create_real_timetable.log', level=logging.INFO,
                        format='%(asctime)s %(message)s')
    create_real_timetable_run(raw_data_dir, interim_data_dir,
                              time.strftime("%Y%m%d", time.localtime()),
                              "collated_delays_000000_235959")
