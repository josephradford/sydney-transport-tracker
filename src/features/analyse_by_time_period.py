import os
from datetime import time, date, datetime
import sys
from transform_train_downloads import TransformTrainDownloads
import tweepy
from dotenv import load_dotenv
import argparse


def analyse_by_time_run(start_time, end_time, date_of_analysis):
    transform = TransformTrainDownloads(start_time, end_time, date_of_analysis)
    transform.transform()

    # currently, a lot of these are duplicates of each other due to not making deep copies in pandas
    # transform.df_filtered_trips.to_csv("df_filtered_trips.csv")
    # transform.df_filtered_trips_delays.to_csv("df_filtered_trips_delays.csv")
    # transform.df_filtered_stop_times.to_csv("df_filtered_stop_times.csv")
    # transform.df_filtered_stop_times_delays.to_csv("df_filtered_stop_times_delays.csv")

    start_dt = datetime(datetime.today().year,
                        datetime.today().month,
                        datetime.today().day,
                        start_time.hour,
                        start_time.minute,
                        start_time.second)

    end_dt = datetime(datetime.today().year,
                      datetime.today().month,
                      datetime.today().day,
                      end_time.hour,
                      end_time.minute,
                      end_time.second)

    trips = transform.df_filtered_trips_delays
    trips_time = trips[((start_dt < trips['start_timestamp']) & (trips['start_timestamp'] < end_dt)) |
                       ((start_dt < trips['end_timestamp']) & (trips['end_timestamp'] < end_dt))]

    total_trips = len(trips_time)

    trips_time_delay = trips_time[trips_time['maximum_departure_delay'] > 0]

    trips_cancelled = trips_time[trips_time['schedule_relationship'] > 0]

    print("Total trips = " + str(total_trips))
    print("Trips delayed = " + str(len(trips_time_delay)))
    print("Trips cancelled = " + str(len(trips_cancelled)))

    delay_ratio = 100 * len(trips_time_delay) / len(trips_time)
    delay_ratio = round(delay_ratio)

    tweet_string = "Between " + start_time.strftime("%H:%M") + " and " + end_time.strftime("%H:%M") \
                   + " today, out of " + str(len(trips_time)) + " trips, " + str(len(trips_time_delay)) \
                   + " experienced delays (" + str(delay_ratio) + "%)."

    print(tweet_string)

    consumer_key = os.getenv("CONSUMER_KEY")
    consumer_secret = os.getenv("CONSUMER_SECRET")
    access_token = os.getenv("ACCESS_TOKEN")
    access_token_secret = os.getenv("ACCESS_TOKEN_SECRET")

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    api = tweepy.API(auth)

    print(api.me().name)

    api.update_status(status=tweet_string)

    print("Transformed using new class")


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