import pickle
import time
from trip_objects import *
import os
from progress.bar import Bar
import csv

def analyse_by_trip(data_dir):
    print("Analysing trips in " + data_dir)
    try:
        trips = pickle.load(open(data_dir + "/collated_delays.pickle", "rb" ))
    except:
        return
    
    print("Parsing timetable in " + data_dir)

    with open(data_dir + '/stop_times.txt', mode='r', encoding='utf-8-sig') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                print(f'Column names are {", ".join(row)}')
            else:
                for trip in trips:
                    if row['trip_id'] == trip.trip_id:
                        print("Trip id match")
                        break
            line_count += 1
        print(f'Processed {line_count} lines.')

    print("Analysed " + str(len(trips)) + " trips")


if __name__== "__main__":
    data_dir = "data/" + time.strftime("%Y%m%d", time.localtime())
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    analyse_by_trip(data_dir)
