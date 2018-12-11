import logging
import os
import datetime
import glob
from progress.bar import Bar
from google.transit import gtfs_realtime_pb2
from trip_objects import *
import pickle


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

        self.source_data_dir = "../../data/raw/" + datetime.date.strftime(self.date_of_analysis, "%Y%m%d")
        self.destination_data_dir = "../../data/interim/" + datetime.date.strftime(self.date_of_analysis, "%Y%m%d")

        log_dir = '../../data/logs/'
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        logging.basicConfig(filename=log_dir + 'transform_train_dwonloads.log', level=logging.INFO,
                            format='%(asctime)s %(message)s')

    def transform(self):
        if not self.is_valid:
            return

        self._merge_delays()
        self._filter_trips()
        self._filter_stop_times()
        self._merge_stop_time_delays()
        self._merge_trip_delays()

    def _merge_trips(self, old_trip, new_trip):
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

        logging.info("Merging delays in " + self.source_data_dir + " to " + self.destination_data_dir)

        # TODO filter the files to those with actual time strings
        files_in_dir = glob.glob(self.source_data_dir + '/*.pickle')
        files = []
        for delay_data_file in files_in_dir:
            time_f_str = datetime.datetime.strptime(delay_data_file[-13:-7], "%H%M%S").time()
            if self.start_time <= time_f_str < self.end_time:
                files.append(delay_data_file)

        bar = Bar('Merging files', max=len(files))
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

        logging.info("Found " + str(len(self.merged_delays)) + " trips")

    def _filter_trips(self):
        pass

    def _filter_stop_times(self):
        pass

    def _merge_stop_time_delays(self):
        pass

    def _merge_trip_delays(self):
        pass
