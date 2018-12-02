import pickle
import time
from trip_objects import *
import os
from progress.bar import Bar
import csv
import calendar
import datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

class RouteStats:
    def __init__(self, route_id):
        self.trips = []
        self.route_id = route_id

    def delays(self):
        retval = 0
        for trip in self.trips:
            if trip.is_delayed():
                retval += 1
        return retval

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
            if line_count == 0:
                print(f'Column names are {", ".join(row)}')
            else:
                if row[day_of_analysis] == '1':
                    start_date = time.strptime(row['start_date'], "%Y%m%d")
                    end_date = time.strptime(row['end_date'], "%Y%m%d")
                    if my_date >= start_date and my_date <= end_date:
                        todays_services.append(row['service_id'])
            line_count += 1

    # create dataframe that is only this day's trips
    df = pd.read_csv(data_dir + '/trips.txt', header=0, encoding='utf-8-sig')
    df = df[df['service_id'].isin(todays_services)]
   
    df.to_pickle(data_dir + '/trips_' + date_of_analysis + '.pickle')

    print("Created this day's timetable")


if __name__== "__main__":
    data_dir = "data/"
    date_str = time.strftime("%Y%m%d", time.localtime())

    create_daily_timetable(data_dir, date_str)
