import urllib
import pickle
import time
import os

import requests, zipfile, io

def timeStr():
    ts = time.localtime()
    return time.strftime("%Y-%m-%d %H:%M:%S", ts)

def download_timetable(data_dir):
    print(timeStr() + ": Downloading today's timetable...")
    f = open("credentials.txt", 'r')
    apikey = f.read()

    url = 'https://api.transport.nsw.gov.au/v1/publictransport/timetables/complete/gtfs'
    headers = {'Authorization' : 'apikey ' + apikey}

    r = requests.get(url, headers=headers)
    print(r)
    z = zipfile.ZipFile(io.BytesIO(r.content))
    print(z)
    z.extractall()

    print(r)

    #pickle.dump(trips, open(data_dir + "/" + time.strftime("%H%M%S", trips.time_started) + ".pickle", "wb" ))
    #print(timeStr() + ": Found " + str(len(trips.trip_updates)) + " trips")

if __name__== "__main__":
    data_dir = "data/" + time.strftime("%Y%m%d", time.localtime())
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    download_timetable(data_dir)
