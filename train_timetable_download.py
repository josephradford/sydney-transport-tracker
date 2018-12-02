import urllib
import pickle
import time
import os
import shutil

import requests, zipfile, io

def timeStr():
    ts = time.localtime()
    return time.strftime("%Y-%m-%d %H:%M:%S", ts)

def download_timetable(data_dir):
    print(timeStr() + ": Downloading today's timetable...")
    f = open("credentials.txt", 'r')
    apikey = f.read()

    url = 'https://api.transport.nsw.gov.au/v1/publictransport/timetables/complete/gtfs'

    req = urllib.request.Request(url)
    req.add_header('Authorization', 'apikey ' + apikey)
    response = urllib.request.urlopen(req)

    file_name = data_dir + "/gtfs_static.zip"
    # Download the file from `url` and save it locally under `file_name`:
    with urllib.request.urlopen(req) as response, open(file_name, 'wb') as out_file:
        shutil.copyfileobj(response, out_file)

def unzip_timetable(data_dir):
    file_name = data_dir + "/gtfs_static.zip"
    with open(file_name, "rb") as f:
        z = zipfile.ZipFile(io.BytesIO(f.read()))
    
    z.extractall(path=data_dir)


if __name__== "__main__":
    data_dir = "data/" + time.strftime("%Y%m%d", time.localtime())
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    download_timetable(data_dir)
    unzip_timetable(data_dir)
