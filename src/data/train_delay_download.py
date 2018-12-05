import urllib.request
import pickle
import time
import os
from dotenv import load_dotenv
import logging
logging.basicConfig(filename='../../data/train_delay_download.log', level=logging.INFO,
                    format='%(asctime)s %(message)s')


def download_delayed_trips(data_dir):
    # logging.info("Downloading delayed trips...")
    time_started = time.localtime()
    try:
        req = urllib.request.Request('https://api.transport.nsw.gov.au/v1/gtfs/realtime/sydneytrains')
        api_key = os.getenv("API_KEY")
        req.add_header('Authorization', 'apikey ' + api_key)
        response = urllib.request.urlopen(req)
        filename = data_dir + "/" + time.strftime("%H%M%S", time_started) + ".pickle"
        pickle.dump(response.read(), open(filename, "wb"))
        logging.info("Delays saved to " + filename)
    except urllib.error.URLError:
        logging.exception("Error when downloading delays")


if __name__ == "__main__":
    load_dotenv()
    destination_data_dir = "../../data/" + time.strftime("%Y%m%d", time.localtime())
    if not os.path.exists(destination_data_dir):
        os.makedirs(destination_data_dir)
    download_delayed_trips(destination_data_dir)
