import pickle
import time
from trip_objects import *
import os
from progress.bar import Bar
import csv
import calendar
import datetime

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

def analyse_by_route(data_dir, date_of_analysis):
    data_dir = data_dir + date_of_analysis
    print("Analysing routes in " + data_dir)

    my_date = time.strptime(date_of_analysis, "%Y%m%d")
    day_of_analysis = str.lower(calendar.day_name[my_date.tm_wday])

    route_trips_dict = {}

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

    with open(data_dir + '/trips.txt', mode='r', encoding='utf-8-sig') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                print(f'Column names are {", ".join(row)}')
            else:
                if row['service_id'] in todays_services:
                    if row['route_id'] in route_trips_dict:
                        route_trips_dict[row['route_id']] = route_trips_dict[row['route_id']] + 1
                    else:
                        route_trips_dict[row['route_id']] = 1
            line_count += 1

    print(f'Processed {line_count} lines.')

    try:
        trips = pickle.load(open(data_dir + "/collated_delays.pickle", "rb" ))
    except:
        return

    # populate routes
    bar = Bar('Analyse trips', max=len(trips))
    routes = []
    for trip in trips:
        if trip.schedule_relationship != 0:
            print(trip)
        routeFound = False
        for route in routes:
            if trip.route_id == route.route_id:
                route.trips.append(trip)
                routeFound = True
        if not routeFound:
            route = RouteStats(trip.route_id)
            route.trips.append(trip)
            routes.append(route)

        bar.next()

    bar.finish()

    for route in routes:
        print("Route " + route.route_id + " " + str(route.delays()) + " delays from " + str(route_trips_dict[route.route_id]))

    print("Analysed " + str(len(trips)) + " trips")


if __name__== "__main__":
    data_dir = "data/"
    date_str = time.strftime("%Y%m%d", time.localtime())

    analyse_by_route(data_dir, date_str)
