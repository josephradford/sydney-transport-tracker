import pickle
import time
from trip_objects import *
import os
import csv
from datetime import time, datetime
import logging
import pandas as pd
import sys


def analyse_by_trip(_interim_data_dir, start_time, end_time):

    if type(start_time) is not time:
        return
    if type(end_time) is not time:
        return

    start_time = datetime(datetime.today().year,
                          datetime.today().month,
                          datetime.today().day,
                          start_time.hour,
                          start_time.minute,
                          start_time.second)

    end_time = datetime(datetime.today().year,
                        datetime.today().month,
                        datetime.today().day,
                        end_time.hour,
                        end_time.minute,
                        end_time.second)

    trips = pd.read_pickle(_interim_data_dir + "/trips_with_delays.pickle")

    trips_time = trips[((start_time < trips['start_timestamp']) & (trips['start_timestamp'] < end_time)) |
                       ((start_time < trips['end_timestamp']) & (trips['end_timestamp'] < end_time))]

    logging.info("Found trips between " + start_time + " and " + end_time)
    trips_time.to_csv(_interim_data_dir + "/slice.csv")


if __name__ == "__main__":
    # run in own directory
    os.chdir(os.path.dirname(sys.argv[0]))
    raw_data_dir = "../../data/raw/" + datetime.strftime(datetime.now(), "%Y%m%d")
    interim_data_dir = "../../data/interim/" + datetime.strftime(datetime.now(), "%Y%m%d")
    log_dir = '../../data/logs/'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    logging.basicConfig(filename=log_dir+'train_analyse_trips.log', level=logging.INFO,
                        format='%(asctime)s %(message)s')
    from_time = time(7, 0, 0)
    to_time = time(10, 0, 0)
    analyse_by_trip(raw_data_dir, interim_data_dir, from_time, to_time)
