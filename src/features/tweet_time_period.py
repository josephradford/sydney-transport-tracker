import os
from datetime import date, datetime
import time
import sys
from analyse_by_time_period import AnalyseByTimePeriod
import tweepy
from dotenv import load_dotenv
import argparse


def tweet_time_period_run(start_time, end_time, date_of_analysis):
    analysis = AnalyseByTimePeriod(start_time, end_time, date_of_analysis)

    # print details
    print("Total trips = " + str(analysis.transform.get_total_trips()))
    print("Trips delayed = " + str(analysis.transform.get_delayed_trips()))
    print("Trips not scheduled = " + str(analysis.transform.get_cancelled_trips()))
    print(analysis.delay_ratio_string())
    print(analysis.worst_delay_status_string())

    # tweet it
    consumer_key = os.getenv("CONSUMER_KEY")
    consumer_secret = os.getenv("CONSUMER_SECRET")
    access_token = os.getenv("ACCESS_TOKEN")
    access_token_secret = os.getenv("ACCESS_TOKEN_SECRET")

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    api = tweepy.API(auth)
    api.update_status(status=analysis.delay_ratio_string())
    time.sleep(5)
    api.update_status(status=analysis.worst_delay_status_string())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Tweet delays for a time period')
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
    tweet_time_period_run(from_time, to_time, date.today())
