import urllib.request
import time
import os
import shutil
import zipfile
import io
import logging
from dotenv import load_dotenv
import sys


def train_timetable_download(data_dir, date_of_analysis):
    url = 'https://api.transport.nsw.gov.au/v1/gtfs/schedule/sydneytrains'
    req = urllib.request.Request(url)

    try:
        api_key = os.getenv("API_KEY")
        req.add_header('Authorization', 'apikey ' + api_key)
    except TypeError:
        logging.exception("Error using saved api key, may not have been specified")

    file_name = data_dir + "/gtfs_schedule_sydneytrains.zip"
    # Download the file from `url` and save it locally under `file_name`:
    with urllib.request.urlopen(req) as response, open(file_name, 'wb') as out_file:
        shutil.copyfileobj(response, out_file)
    logging.info("Downloaded " + date_of_analysis + " timetable to " + data_dir)


def unzip_timetable(data_dir, date_of_analysis):
    file_name = data_dir + "/gtfs_schedule_sydneytrains.zip"
    with open(file_name, "rb") as f:
        z = zipfile.ZipFile(io.BytesIO(f.read()))
    
    z.extractall(path=data_dir)
    os.remove(file_name)
    logging.info("Unzipped " + date_of_analysis + " timetable to " + data_dir)


def train_timetable_download_run(data_dir, date_str):
    train_timetable_download(data_dir, date_str)
    unzip_timetable(data_dir, date_str)


if __name__== "__main__":
    # run in own directory
    os.chdir(os.path.dirname(sys.argv[0]))
    load_dotenv()
    destination_data_dir = "../../data/raw/" + time.strftime("%Y%m%d", time.localtime())
    if not os.path.exists(destination_data_dir):
        os.makedirs(destination_data_dir)
    logging.basicConfig(filename='../../data/train_timetable_download.log', level=logging.INFO,
                        format='%(asctime)s %(message)s')
    train_timetable_download_run(destination_data_dir, time.strftime("%Y%m%d", time.localtime()))
