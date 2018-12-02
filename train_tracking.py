from train_delay_download import *
from collate_train_delays import *
from analyse_by_route import *
import sched, time, os
    
s = sched.scheduler(time.time, time.sleep)
data_dir = "data/"
date_str =  time.strftime("%Y%m%d", time.localtime())
analysed_today = False

def run_downloads():
    global analysed_today
    global date_str
    # loop from 4am to 2am
    s.enter(60, 1, run_downloads)
    
    hour = time.localtime().tm_hour

    if hour > 4:
        download_delayed_trips(data_dir + date_str)
        analysed_today = False
    else:
        if not analysed_today:
            # put all data in one file
            collate_train_delays(data_dir)

            # analyse routes
            analyse_by_route(data_dir, date_str)

            # create the new data directory
            date_str = time.strftime("%Y%m%d", time.localtime())
            if not os.path.exists(data_dir + date_str):
                os.makedirs(data_dir + date_str)

            # stop the analysis from happening again
            analysed_today = True

    

    # parse all results after 2am

    # analyse results after results are parsed

    # exit application (or sleep until 4am)


if __name__== "__main__":
    date_str = time.strftime("%Y%m%d", time.localtime())
    if not os.path.exists(data_dir + date_str):
        os.makedirs(data_dir + date_str)
    s.enter(1, 1, run_downloads)
    s.run()
