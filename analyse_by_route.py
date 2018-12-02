import pickle
import time
from trip_objects import *
import os
from progress.bar import Bar

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

def analyse_by_route(data_dir):
    print("Analysing routes in " + data_dir)
    try:
        trips = pickle.load(open(data_dir + "/collated_delays.pickle", "rb" ))
    except:
        return

    # populate routes
    bar = Bar('Analyse trips', max=len(trips))
    routes = []
    for trip in trips:
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
        print("Route " + route.route_id + " " + str(route.delays()) + " delays from " + str(len(route.trips)))

    print("Analysed " + str(len(trips)) + " trips")


if __name__== "__main__":
    data_dir = "data/" + time.strftime("%Y%m%d", time.localtime())
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    analyse_by_route(data_dir)
