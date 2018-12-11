
class TransformTrainDownloads:

    def __init__(self, start_time, stop_time, date_of_analysis):
        self.start_time = start_time
        self.stop_time = stop_time
        self.date_of_analysis = date_of_analysis

    def transform(self):
        self._merge_delays()
        self._filter_trips()
        self._filter_stop_times()
        self._merge_stop_time_delays()
        self._merge_trip_delays()

    def _merge_delays(self):
        pass

    def _filter_trips(self):
        pass

    def _filter_stop_times(self):
        pass

    def _merge_stop_time_delays(self):
        pass

    def _merge_trip_delays(self):
        pass
