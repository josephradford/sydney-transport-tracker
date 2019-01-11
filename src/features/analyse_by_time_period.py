import os
from datetime import date, datetime
import time
import sys
from transform_train_downloads import TransformTrainDownloads
import tweepy
from dotenv import load_dotenv
import argparse

ROUTES_TO_IGNORE = ["CTY_NC1", "CTY_NC1a", "CTY_NC2", "CTY_NW1a", "CTY_NW1b", "CTY_NW1c", "CTY_NW1d",
                    "CTY_NW2a", "CTY_NW2b", "CTY_S1a", "CTY_S1b", "CTY_S1c", "CTY_S1d", "CTY_S1e",
                    "CTY_S1f", "CTY_S1g", "CTY_S1h", "CTY_S1i", "CTY_S2a", "CTY_S2b", "CTY_S2c",
                    "CTY_S2d", "CTY_S2e", "CTY_S2f", "CTY_S2g", "CTY_S2h", "CTY_S2i", "CTY_W1a",
                    "CTY_W1b", "CTY_W2a", "CTY_W2b", "HUN_1a", "HUN_1b", "HUN_2a", "HUN_2b",
                    "RTTA_DEF", "RTTA_REV"]


def analyse_by_time_run(start_time, end_time, date_of_analysis):
    transform = TransformTrainDownloads(start_time, end_time, date_of_analysis, ROUTES_TO_IGNORE)
    transform.transform()

    # currently, a lot of these are duplicates of each other due to not making deep copies in pandas
    # transform.df_filtered_trips.to_csv("df_filtered_trips.csv")
    # transform.df_filtered_trips_delays.to_csv("df_filtered_trips_delays.csv")
    # transform.df_filtered_stop_times.to_csv("df_filtered_stop_times.csv")
    # transform.df_filtered_stop_times_delays.to_csv("df_filtered_stop_times_delays.csv")

    print("Total trips = " + str(transform.get_total_trips()))
    print("Trips delayed = " + str(transform.get_delayed_trips()))
    print("Trips not scheduled = " + str(transform.get_cancelled_trips()))

    # During the morning peak time, x% of trips experienced delays #sydneytrains
    delay_ratio_string = "Between " + start_time.strftime("%H:%M") + " and " + end_time.strftime("%H:%M") + \
                         " today, " + str(transform.get_delay_ratio()) + "% of trips experienced delays. #sydneytrains"

    print(delay_ratio_string)

    # worst delay
    # The worst delay was x minutes, on the HH:MM ABC service #sydneytrains
    worst_delay_status_string = "The worst delay was " + str(transform.get_worst_delay_minutes_rounded_down()) + \
                                " minutes, on the " + transform.get_worst_delay_time_str() + " " + \
                                transform.get_worst_delay_route_name() + " service. #sydneytrains"

    print(worst_delay_status_string)

    # tweet it
    consumer_key = os.getenv("CONSUMER_KEY")
    consumer_secret = os.getenv("CONSUMER_SECRET")
    access_token = os.getenv("ACCESS_TOKEN")
    access_token_secret = os.getenv("ACCESS_TOKEN_SECRET")

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    api = tweepy.API(auth)
    api.update_status(status=delay_ratio_string)
    time.sleep(5)
    api.update_status(status=worst_delay_status_string)


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
