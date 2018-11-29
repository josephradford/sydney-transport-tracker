from train_delay_download import *
import sched, time, os
    
s = sched.scheduler(time.time, time.sleep)
data_dir = "data/" + time.strftime("%Y%m%d", time.localtime())

def run_downloads():
    s.enter(60, 1, run_downloads)
    download_delayed_trips(data_dir)

if __name__== "__main__":
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    s.enter(1, 1, run_downloads)
    s.run()
