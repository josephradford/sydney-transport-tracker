import pickle
import time
from trip_objects import *
from progress.bar import Bar
import csv
import pandas as pd
import numpy as np
from datetime import datetime

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

def analyse_by_stop(data_dir, date_of_analysis, stop_id):
    data_dir = data_dir + date_of_analysis
    print("Analysing stop " + stop_id + " in " + data_dir)

    try:
        df_trips = pd.read_csv(data_dir + "/timetable_with_delays.csv", header=0, 
                                encoding='utf-8-sig', 
                                dtype={'stop_id': str},
                                parse_dates=['arrival_time', 'departure_time'])
    except:
        return

    am_start = pd.datetime.strptime(date_of_analysis + "0700", "%Y%m%d%H%M")
    am_end   = datetime.strptime(date_of_analysis + "0900", "%Y%m%d%H%M")
    pm_start = datetime.strptime(date_of_analysis + "1600", "%Y%m%d%H%M")
    pm_end   = datetime.strptime(date_of_analysis + "1830", "%Y%m%d%H%M")

    print('Date: ' + str(pm_start))

    #df_trips = df_trips[(df_trips['stop_id'] == stop_id)]
    #df_trips = df_trips[(df_trips['departure_delay'] != 'N/A')]
    df_trips = df_trips[((df_trips['departure_time'] >= am_start) &
                         (df_trips['departure_time'] <= am_end)) | 
                        ((df_trips['departure_time'] >= pm_start) &
                         (df_trips['departure_time'] <= pm_end))]
    
    print(df_trips)
    

def analyse_by_route(data_dir, date_of_analysis):
    data_dir = data_dir + date_of_analysis
    print("Analysing routes in " + data_dir)

    try:
        df_trips = pd.read_pickle(data_dir + '/trips_' + date_of_analysis + '.pickle')
        trip_delays = pickle.load(open(data_dir + "/collated_delays.pickle", "rb" ))
    except:
        return

    # populate routes
    bar = Bar('Analyse trips', max=len(trip_delays))
    routes = []
    for trip in trip_delays:
        # check to see trip was supposed to happen
        if not trip.trip_id in df_trips['trip_id'].values:
            #print("Trip " + trip.trip_id + " was not supposed to run today!")
            continue
        #if trip.schedule_relationship != 0:
        #    print(trip)
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

    most_delays = 0
    most_delayed_route = RouteStats('nothing')
    for route in routes:
        num_trips_route_today = len(df_trips[df_trips['route_id'] == route.route_id])
        if len(route.trips) > num_trips_route_today:
            print("More trips recorded on realtime than on timetable on route " + route.route_id)

        delay_pc = route.delays() / num_trips_route_today
        if delay_pc > most_delays:
            most_delays = delay_pc
            most_delayed_route = route

        print("Route " + route.route_id + " " + str(route.delays()) + " delays from " +
                     str(num_trips_route_today))

    print("Analysed " + str(len(trip_delays)) + " trips")


if __name__== "__main__":
    data_dir = "data/"
    date_str = time.strftime("%Y%m%d", time.localtime())
    analyse_by_stop(data_dir, date_str, '2131123')
    #analyse_by_route(data_dir, date_str)
