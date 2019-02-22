import os
from datetime import date, datetime
import sys
from transform_train_downloads import TransformTrainDownloads
from dotenv import load_dotenv
import argparse

ROUTES_TO_IGNORE = ["CTY_NC1", "CTY_NC1a", "CTY_NC2", "CTY_NW1a", "CTY_NW1b", "CTY_NW1c", "CTY_NW1d",
                    "CTY_NW2a", "CTY_NW2b", "CTY_S1a", "CTY_S1b", "CTY_S1c", "CTY_S1d", "CTY_S1e",
                    "CTY_S1f", "CTY_S1g", "CTY_S1h", "CTY_S1i", "CTY_S2a", "CTY_S2b", "CTY_S2c",
                    "CTY_S2d", "CTY_S2e", "CTY_S2f", "CTY_S2g", "CTY_S2h", "CTY_S2i", "CTY_W1a",
                    "CTY_W1b", "CTY_W2a", "CTY_W2b", "HUN_1a", "HUN_1b", "HUN_2a", "HUN_2b",
                    "RTTA_DEF", "RTTA_REV"]


class AnalyseByTimePeriod:

    def __init__(self, start_time, end_time, date_of_analysis):
        self.start_time = start_time
        self.end_time = end_time
        self.date_of_analysis = date_of_analysis
        self.transform = TransformTrainDownloads(self.start_time, self.end_time, self.date_of_analysis, ROUTES_TO_IGNORE)
        self.transform.transform()

        # delay files outside of the time range will need to be considered
        # if a stop at the end of the time range is a few minutes late at the end of the time range,
        # then is reported much later after the time range is finished, this needs to be parsed

        # currently, a lot of these are duplicates of each other due to not making deep copies in pandas
        # transform.df_filtered_trips.to_csv("df_filtered_trips.csv")
        # transform.df_filtered_trips_delays.to_csv("df_filtered_trips_delays.csv")
        # transform.df_filtered_stop_times.to_csv("df_filtered_stop_times.csv")
        # transform.df_filtered_stop_times_delays.to_csv("df_filtered_stop_times_delays.csv")

    def delay_ratio_string(self):
        # During the morning peak time, x% of trips experienced delays #sydneytrains
        return "Between " + self.start_time.strftime("%H:%M") + " and " + self.end_time.strftime("%H:%M") + \
               " today, " + str(self.transform.get_delay_ratio()) + "% of trips experienced delays. #sydneytrains"

    def worst_delay_status_string(self):
        # The worst delay was x minutes, on the HH:MM ABC service #sydneytrains
        return "The worst delay was " + str(self.transform.get_worst_delay_minutes_rounded_down()) + \
               " minutes, on the " + self.transform.get_worst_delay_time_str() + " " + \
               self.transform.get_worst_delay_route_name() + " service. #sydneytrains"


def analyse_by_time_run(start_time, end_time, date_of_analysis):
    analysis = AnalyseByTimePeriod(start_time, end_time, date_of_analysis)
    print("Total trips = " + str(analysis.transform.get_total_trips()))
    print("Trips delayed = " + str(analysis.transform.get_delayed_trips()))
    print("Trips not scheduled = " + str(analysis.transform.get_cancelled_trips()))
    print(analysis.delay_ratio_string())
    print(analysis.worst_delay_status_string())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process delays for a time period')
    parser.add_argument('start_time', type=str,
                        help='start time to process from, HH:MM')
    parser.add_argument('end_time', type=str,
                        help='end time to process to, HH:MM')

    args = parser.parse_args()

    # run in own directory
    os.chdir(os.path.dirname(sys.argv[0]))
    load_dotenv()
    from_time = datetime.strptime(args.start_time, "%H:%M").time()
    to_time = datetime.strptime(args.end_time, "%H:%M").time()
    analyse_by_time_run(from_time, to_time, date.today())
