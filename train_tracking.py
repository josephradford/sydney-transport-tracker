from train_delay_download import *
import sched, time
    
s = sched.scheduler(time.time, time.sleep)

def run_downloads():
    s.enter(60, 1, run_downloads)
    download_delayed_trips()

if __name__== "__main__":
    s.enter(1, 1, run_downloads)
    s.run()
