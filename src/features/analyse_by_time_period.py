import pickle
import time
from trip_objects import *
import os
import csv
from datetime import time, datetime
import logging
import pandas as pd
import sys
from collate_train_delays import collate_train_delay_save
from create_real_timetable import create_real_timetable_run
from analyse_by_trip import analyse_by_trip


def analyse_by_time_run(_raw_data_dir, _interim_data_dir, start_time, end_time):
    collate_train_delay_save(_raw_data_dir, _interim_data_dir, start_time, end_time)
    fname = "collated_delays_" + start_time.strftime("%H%M%S") + "_" + end_time.strftime("%H%M%S")
    create_real_timetable_run(_raw_data_dir, _interim_data_dir, datetime.strftime(datetime.now(), "%Y%m%d"), fname)
    analyse_by_trip(_interim_data_dir, start_time, end_time)


if __name__ == "__main__":
    # run in own directory
    os.chdir(os.path.dirname(sys.argv[0]))
    raw_data_dir = "../../data/raw/" + datetime.strftime(datetime.now(), "%Y%m%d")
    interim_data_dir = "../../data/interim/" + datetime.strftime(datetime.now(), "%Y%m%d")
    if not os.path.exists(interim_data_dir):
        os.makedirs(interim_data_dir)
    log_dir = '../../data/logs/'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    logging.basicConfig(filename=log_dir+'train_analyse_by_time.log', level=logging.INFO,
                        format='%(asctime)s %(message)s')
    from_time = time(7, 0, 0)
    to_time = time(10, 0, 0)
    analyse_by_time_run(raw_data_dir, interim_data_dir, from_time, to_time)
