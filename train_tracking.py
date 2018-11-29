from train_delay_download import *
import sched, time, os
    
s = sched.scheduler(time.time, time.sleep)
data_dir = "data/" + time.strftime("%Y%m%d", time.localtime())

def run_downloads():
    # loop from 4am to 2am
    s.enter(60, 1, run_downloads)
    download_delayed_trips(data_dir)

    # parse all results after 2am

    # analyse results after results are parsed

    # exit application (or sleep until 4am)

if __name__== "__main__":
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    s.enter(1, 1, run_downloads)
    s.run()
