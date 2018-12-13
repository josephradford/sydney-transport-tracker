import logging
import os
import datetime
import glob
from progress.bar import Bar
from google.transit import gtfs_realtime_pb2
from trip_objects import *
import pickle
import calendar
import csv
import pandas as pd


class TransformTrainDownloads:

    def __init__(self, start_time, end_time, date_of_analysis):
        self.is_valid = False
        if type(start_time) is not datetime.time:
            return
        if type(end_time) is not datetime.time:
            return
        if type(date_of_analysis) is not datetime.date:
            return

        self.is_valid = True
        self.start_time = start_time
        self.end_time = end_time
        self.date_of_analysis = date_of_analysis
        self.date_of_analysis_str = datetime.date.strftime(self.date_of_analysis, "%Y%m%d")

        self.source_data_dir = "../../data/raw/" + self.date_of_analysis_str
        self.destination_data_dir = "../../data/interim/" + self.date_of_analysis_str

        log_dir = '../../data/logs/'
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        logging.basicConfig(filename=log_dir + 'transform_train_downloads.log', level=logging.INFO,
                            format='%(asctime)s %(message)s')

    def transform(self):
        if not self.is_valid:
            return

        self._merge_delays()
        self._filter_trips()
        self._filter_stop_times()
        self._merge_stop_time_delays()
        self._merge_trip_delays()

    @staticmethod
    def _log_and_print(message):
        logging.info(message)
        print(message)

    @staticmethod
    def _merge_trips(old_trip, new_trip):
        if old_trip.trip_id != new_trip.trip_id:
            return old_trip
        if old_trip.timestamp == new_trip.timestamp:
            # no updates
            return old_trip

        for new_stop_time_update in new_trip.stop_time_updates:
            if new_stop_time_update in old_trip.stop_time_updates:
                # take the new one for now
                old_trip.stop_time_updates[new_stop_time_update] = new_trip.stop_time_updates[new_stop_time_update]
                old_trip.timestamp = new_trip.timestamp
            else:
                old_trip.stop_time_updates[new_stop_time_update] = new_trip.stop_time_updates[new_stop_time_update]

        return old_trip

    def _merge_delays(self):
        self._log_and_print("Merging delays in " + self.source_data_dir + " to " + self.destination_data_dir)

        # TODO filter the files to those with actual time strings
        files_in_dir = glob.glob(self.source_data_dir + '/*.pickle')
        files = []
        for delay_data_file in files_in_dir:
            time_f_str = datetime.datetime.strptime(delay_data_file[-13:-7], "%H%M%S").time()
            if self.start_time <= time_f_str < self.end_time:
                files.append(delay_data_file)

        bar = Bar('Merging delay responses', max=len(files))
        self.merged_delays = dict()

        for delay_data_file in files:
            bar.next()
            try:
                current_delay_response = pickle.load(open(delay_data_file, "rb"))
            except:
                continue  # next file

            feed = gtfs_realtime_pb2.FeedMessage()
            feed.ParseFromString(current_delay_response)
            for entity in feed.entity:
                if entity.HasField('trip_update') and len(entity.trip_update.stop_time_update) > 0:
                    trip_update = TripUpdate(entity.trip_update.trip.trip_id,
                                             entity.trip_update.trip.route_id,
                                             entity.trip_update.trip.schedule_relationship,
                                             entity.trip_update.timestamp)

                    for stop_time_update in entity.trip_update.stop_time_update:
                        trip_update.stop_time_updates[stop_time_update.stop_id] \
                            = StopTimeUpdate(stop_time_update.stop_id,
                                             stop_time_update.arrival.delay,
                                             stop_time_update.departure.delay,
                                             stop_time_update.schedule_relationship)

                    if trip_update is None:
                        print('trip update is none')
                    # merge with current trips
                    if trip_update.trip_id in self.merged_delays:
                        self.merged_delays[trip_update.trip_id] = \
                            self._merge_trips(self.merged_delays[trip_update.trip_id], trip_update)
                    else:
                        self.merged_delays[trip_update.trip_id] = trip_update

        bar.finish()
        self._log_and_print("Found " + str(len(self.merged_delays)) + " trips")

    def _filter_trips(self):
        self._log_and_print("Creating table of trips that occur on " + self.date_of_analysis_str)
        day_of_analysis = str.lower(calendar.day_name[self.date_of_analysis.isoweekday() - 1])

        # create list of services that run on this day
        todays_services = []
        with open(self.source_data_dir + '/calendar.txt', mode='r', encoding='utf-8-sig') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            line_count = 0
            for row in csv_reader:
                if line_count != 0:
                    if row[day_of_analysis] == '1':
                        start_date = datetime.datetime.strptime(row['start_date'], "%Y%m%d").date()
                        end_date = datetime.datetime.strptime(row['end_date'], "%Y%m%d").date()
                        if start_date <= self.date_of_analysis <= end_date:
                            todays_services.append(row['service_id'])
                line_count += 1

        # create data frame that is only this day's trips
        df = pd.read_csv(self.source_data_dir + '/trips.txt', header=0, encoding='utf-8-sig')
        df = df[df['service_id'].isin(todays_services)]
        df = df[~df['route_id'].isin(['RTTA_DEF', 'RTTA_REV'])]

        self.df_filtered_trips = df

        self._log_and_print("Created table of trips that occur on " + self.date_of_analysis_str)
        # TODO filter out by time as well, by looking at the trip.txt

    def _filter_stop_times(self):
        self._log_and_print("Creating real schedule of stop times on " + self.date_of_analysis_str + " between " +
                            self.start_time.strftime("%H:%M") + " and " + self.end_time.strftime("%H:%M"))

        # load the static timetable into a data frame
        df_stop_times = pd.read_csv(self.source_data_dir + '/stop_times.txt', header=0,
                                    encoding='utf-8-sig',
                                    dtype={'stop_id': str},
                                    parse_dates=['arrival_time', 'departure_time'])

        # remove any trips from stop_times that did NOT happen on this date
        self.df_filtered_stop_times = df_stop_times[df_stop_times['trip_id'].isin(self.df_filtered_trips['trip_id'])]
        self._log_and_print("Created real schedule of stop times on " + self.date_of_analysis_str + " between " +
                            self.start_time.strftime("%H:%M") + " and " + self.end_time.strftime("%H:%M"))

    def _merge_stop_time_delays(self):
        self._log_and_print("Creating stop times with delays on " + self.date_of_analysis_str + " between " +
                            self.start_time.strftime("%H:%M") + " and " + self.end_time.strftime("%H:%M"))
        df_stop_times = self.df_filtered_stop_times

        # insert actual arrival, actual departure, and cancellation states into data frame
        # mark all as N/A to start with, so we know which things never had real time updates
        df_stop_times.insert(2, 'arrival_delay', 'N/A')
        df_stop_times.insert(3, 'actual_arrival_time', 'N/A')
        df_stop_times.insert(5, 'departure_delay', 'N/A')
        df_stop_times.insert(6, 'actual_departure_time', 'N/A')
        df_stop_times.insert(7, 'schedule_relationship', 'N/A')

        # load all delays found on this date
        trip_delays = self.merged_delays

        df_trips = self.df_filtered_trips

        bar = Bar('Add delays to stop times', max=len(trip_delays))
        for trip in trip_delays.values():
            bar.next()
            if trip.trip_id not in df_trips['trip_id'].values:
                # print("Trip " + trip.trip_id + " was not supposed to run today!")
                continue

            for stop_time_update in trip.stop_time_updates.values():
                # some of these values might be 24:00, 25:00 etc to signify next day

                idx = df_stop_times[(df_stop_times['trip_id'] == trip.trip_id) &
                                    (df_stop_times['stop_id'] == stop_time_update.stop_id)].index
                if idx.empty:
                    # it shouldn't be
                    continue

                idx = idx.item()

                # calculate the real time
                actual_arrival_time = self.update_time(df_stop_times.at[idx, 'arrival_time'],
                                                       stop_time_update.arrival_delay)
                actual_departure_time = self.update_time(df_stop_times.at[idx, 'departure_time'],
                                                         stop_time_update.departure_delay)

                # add the new values to the new columns

                df_stop_times.at[idx, 'arrival_delay'] = stop_time_update.arrival_delay
                df_stop_times.at[idx, 'actual_arrival_time'] = actual_arrival_time
                df_stop_times.at[idx, 'departure_delay'] = stop_time_update.departure_delay
                df_stop_times.at[idx, 'actual_departure_time'] = actual_departure_time
                df_stop_times.at[idx, 'schedule_relationship'] = stop_time_update.schedule_relationship

        bar.finish()
        self.df_filtered_stop_times_delays = df_stop_times
        self._log_and_print("Created stop times with delays on " + self.date_of_analysis_str + " between " +
                            self.start_time.strftime("%H:%M") + " and " + self.end_time.strftime("%H:%M"))

    def _merge_trip_delays(self):
        self._log_and_print("Creating real trip summaries on " + self.date_of_analysis_str + " between " +
                            self.start_time.strftime("%H:%M") + " and " + self.end_time.strftime("%H:%M"))

        # load the trip ids of that actual trips that happened on this day
        df_trips = self.df_filtered_trips

        # get the stop times for trips that happened this day
        df_stop_times = self.df_filtered_stop_times_delays

        # insert actual arrival, actual departure, and cancellation states into dataframe
        # mark all as N/A to start with, so we know which things never had real time updates
        df_trips.insert(0, 'start_timestamp', 'N/A')
        df_trips.insert(1, 'end_timestamp', 'N/A')
        df_trips.insert(6, 'maximum_arrival_delay', 0)
        df_trips.insert(7, 'average_arrival_delay', 0)
        df_trips.insert(8, 'maximum_departure_delay', 0)
        df_trips.insert(9, 'average_departure_delay', 0)
        df_trips.insert(10, 'schedule_relationship', 0)

        # load all delays found on this date
        trip_delays = self.merged_delays

        bar = Bar('Add delays to trips', max=len(trip_delays))
        for trip in trip_delays.values():
            bar.next()
            if trip.trip_id not in df_trips['trip_id'].values:
                # print("Trip " + trip.trip_id + " was not supposed to run today!")
                continue

            idx = df_trips[(df_trips['trip_id'] == trip.trip_id)].index
            if idx.empty:
                # it shouldn't be
                continue

            idx = idx.item()

            df_trips.at[idx, 'maximum_arrival_delay'] = trip.maximum_arrival_delay()
            df_trips.at[idx, 'average_arrival_delay'] = trip.average_arrival_delay()
            df_trips.at[idx, 'maximum_departure_delay'] = trip.maximum_departure_delay()
            df_trips.at[idx, 'average_departure_delay'] = trip.average_departure_delay()
            df_trips.at[idx, 'schedule_relationship'] = trip.overall_schedule_relationship()

        bar.finish()

        bar = Bar('Add stop and start times to trips', max=len(df_trips))
        for i in df_trips.index:
            bar.next()
            departure_series = df_stop_times[df_stop_times['trip_id'] == df_trips.at[i, 'trip_id']]['departure_time']
            df_trips.at[i, 'start_timestamp'] = self.convert_to_timestamp(departure_series.iloc[0])
            df_trips.at[i, 'end_timestamp'] = self.convert_to_timestamp(departure_series.iloc[-1])

        bar.finish()

        self.df_filtered_trips_delays = df_trips

        self._log_and_print("Created real trip summaries on " + self.date_of_analysis_str + " between " +
                            self.start_time.strftime("%H:%M") + " and " + self.end_time.strftime("%H:%M"))

    def update_time(self, time_str, delay_val):
        try:
            # this could be optimised
            delay_val = int(delay_val)
            original_time = datetime.datetime.strptime(self.date_of_analysis_str + time_str, "%Y%m%d%H:%M:%S")
            updated_time = original_time + datetime.timedelta(seconds=delay_val)
            return updated_time.strftime("%H:%M:%S")
        except:
            return "Exception"

    def convert_to_timestamp(self, time_str):
        hours = int(time_str[0:2])
        if hours > 23:
            time_str = '0' + str(hours-23) + time_str[2:]
            retval = datetime.datetime.strptime(self.date_of_analysis_str + time_str, "%Y%m%d%H:%M:%S")
            retval += datetime.timedelta(days=1)
            return retval
        else:
            retval = datetime.datetime.strptime(self.date_of_analysis_str + time_str, "%Y%m%d%H:%M:%S")
            return retval