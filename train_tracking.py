from train_delay_download import *
from collate_train_delays import *
from analyse_by_route import *
import sched, time, os
    
s = sched.scheduler(time.time, time.sleep)
data_dir = "data/" + time.strftime("%Y%m%d", time.localtime())
analysed_today = False

def run_downloads():
    global data_dir
    global analysed_today
    # loop from 4am to 2am
    hour = time.localtime().tm_hour

    if hour > 4:
        download_delayed_trips(data_dir)
        analysed_today = False
    else:
        if not analysed_today:
            # put all data in one file
            collate_train_delays(data_dir)

            # analyse routes
            analyse_by_route(data_dir)

            # create the new data directory
            data_dir = "data/" + time.strftime("%Y%m%d", time.localtime())
            if not os.path.exists(data_dir):
                os.makedirs(data_dir)

            # stop the analysis from happening again
            analysed_today = True

    

    # parse all results after 2am

    # analyse results after results are parsed

    # exit application (or sleep until 4am)
    s.enter(60, 1, run_downloads)


if __name__== "__main__":
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    s.enter(1, 1, run_downloads)
    s.run()
