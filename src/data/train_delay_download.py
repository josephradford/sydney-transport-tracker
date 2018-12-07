import urllib.request
import pickle
import time
import os
from dotenv import load_dotenv
import logging
import sys


def download_delayed_trips(data_dir):
    # logging.info("Downloading delayed trips...")
    time_started = time.localtime()
    req = urllib.request.Request('https://api.transport.nsw.gov.au/v1/gtfs/realtime/sydneytrains')

    try:
        api_key = os.getenv("DELAYS_API_KEY")
        req.add_header('Authorization', 'apikey ' + api_key)
    except TypeError:
        logging.exception("Error using saved api key, may not have been specified")

    try:
        response = urllib.request.urlopen(req)
        filename = data_dir + "/" + time.strftime("%H%M%S", time_started) + ".pickle"
        pickle.dump(response.read(), open(filename, "wb"))
        logging.info("Delays saved to " + filename)
    except urllib.error.URLError:
        logging.exception("Error when downloading delays")


if __name__ == "__main__":
    # run in own directory
    os.chdir(os.path.dirname(sys.argv[0]))
    load_dotenv()
    destination_data_dir = "../../data/raw/" + time.strftime("%Y%m%d", time.localtime())
    if not os.path.exists(destination_data_dir):
        os.makedirs(destination_data_dir)
    log_dir = '../../data/logs/'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    logging.basicConfig(filename=log_dir+'train_delay_download.log', level=logging.INFO,
                        format='%(asctime)s %(message)s')
    download_delayed_trips(destination_data_dir)
