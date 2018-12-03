#! /usr/bin/python3

from train_delay_download import *
from collate_train_delays import collate_train_delays_run
from analyse_by_route import *
from static_train_timetable import static_train_timetable_run
import sched, time, os, sys
    
s = sched.scheduler(time.time, time.sleep)
data_dir = "data/"
date_str =  time.strftime("%Y%m%d", time.localtime())
state = 'prepare'

def run_downloads():
    global state
    global date_str

    hour = time.localtime().tm_hour

    if state == 'prepare':
        if hour > 3:
            # create the new data directory
            date_str = time.strftime("%Y%m%d", time.localtime())
            if not os.path.exists(data_dir + date_str):
                os.makedirs(data_dir + date_str)

            # get today's timetable        
            static_train_timetable_run(data_dir, date_str)
            s.enter(1, 1, run_downloads)
            state = 'download_delays'

        else:
            s.enter(60 * 5, 1, run_downloads)

    elif state == 'download_delays':
        s.enter(60, 1, run_downloads)
        download_delayed_trips(data_dir + date_str)
        if hour > 1 and hour < 2:
            # we've rolled over to 1 am, time to collate everything
            state = 'collate_analyse' 

    elif state == 'collate_analyse':
        # put all data in one file
        collate_train_delays_run(data_dir, date_str)
        # analyse routes
        analyse_by_route(data_dir, date_str)
        
        # now we wait for tomorrow to start
        state = 'prepare'
        s.enter(60 * 5, 1, run_downloads)

    else:
        s.enter(60 * 5, 1, run_downloads)
        state = 'prepare'


if __name__== "__main__":
    # run in own directory
    os.chdir(os.path.dirname(sys.argv[0]))
    state = 'prepare'
    s.enter(1, 1, run_downloads)
    s.run()
