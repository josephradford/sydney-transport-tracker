import urllib
import pickle
import time
import os
import shutil
import csv
import calendar
import pandas as pd
import requests
import zipfile
import io

data_dir = "data/"

def download_timetable(data_dir, date_of_analysis):
    data_dir = data_dir + date_of_analysis
    print("Downloading " + date_of_analysis + " timetable to " + data_dir + "...")
    f = open("credentials.txt", 'r')
    apikey = f.read()

    url = 'https://api.transport.nsw.gov.au/v1/gtfs/schedule/sydneytrains'

    req = urllib.request.Request(url)
    req.add_header('Authorization', 'apikey ' + apikey)
    response = urllib.request.urlopen(req)

    file_name = data_dir + "/gtfs_schedule_sydneytrains.zip"
    # Download the file from `url` and save it locally under `file_name`:
    with urllib.request.urlopen(req) as response, open(file_name, 'wb') as out_file:
        shutil.copyfileobj(response, out_file)

def unzip_timetable(data_dir, date_of_analysis):
    data_dir = data_dir + date_of_analysis
    print("Unzipping " + date_of_analysis + " timetable to " + data_dir + "...")
    file_name = data_dir + "/gtfs_schedule_sydneytrains.zip"
    with open(file_name, "rb") as f:
        z = zipfile.ZipFile(io.BytesIO(f.read()))
    
    z.extractall(path=data_dir)

def create_daily_timetable(data_dir, date_of_analysis):
    data_dir = data_dir + date_of_analysis
    print("Creating timetable for " + date_of_analysis + " in " + data_dir)

    my_date = time.strptime(date_of_analysis, "%Y%m%d")
    day_of_analysis = str.lower(calendar.day_name[my_date.tm_wday])

    # create list of services that run on this day
    todays_services = []
    with open(data_dir + '/calendar.txt', mode='r', encoding='utf-8-sig') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        line_count = 0
        for row in csv_reader:
            if line_count != 0:
                if row[day_of_analysis] == '1':
                    start_date = time.strptime(row['start_date'], "%Y%m%d")
                    end_date = time.strptime(row['end_date'], "%Y%m%d")
                    if my_date >= start_date and my_date <= end_date:
                        todays_services.append(row['service_id'])
            line_count += 1

    # create dataframe that is only this day's trips
    df = pd.read_csv(data_dir + '/trips.txt', header=0, encoding='utf-8-sig')
    df = df[df['service_id'].isin(todays_services)]
    df = df[~df['route_id'].isin(['RTTA_DEF', 'RTTA_REV'])]

   
    df.to_pickle(data_dir + '/trips_' + date_of_analysis + '.pickle')

    print("Created timetable for " + date_of_analysis + " in " + data_dir)
    print("Created this day's timetable")

def static_train_timetable_run(data_dir, date_str):
    download_timetable(data_dir, date_str)
    unzip_timetable(data_dir, date_str)
    create_daily_timetable(data_dir, date_str)

if __name__== "__main__":
    date_str = time.strftime("%Y%m%d", time.localtime())
    if not os.path.exists(data_dir + date_str):
        os.makedirs(data_dir)
    static_train_timetable_run(data_dir, date_str)
