import csv
import calendar
import time
import pandas as pd
import os
import sys
import logging


def create_daily_timetable(source_dir, dest_dir, date_of_analysis):
    my_date = time.strptime(date_of_analysis, "%Y%m%d")
    day_of_analysis = str.lower(calendar.day_name[my_date.tm_wday])

    # create list of services that run on this day
    todays_services = []
    with open(source_dir + '/calendar.txt', mode='r', encoding='utf-8-sig') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        line_count = 0
        for row in csv_reader:
            if line_count != 0:
                if row[day_of_analysis] == '1':
                    start_date = time.strptime(row['start_date'], "%Y%m%d")
                    end_date = time.strptime(row['end_date'], "%Y%m%d")
                    if start_date <= my_date <= end_date:
                        todays_services.append(row['service_id'])
            line_count += 1

    # create dataframe that is only this day's trips
    df = pd.read_csv(source_dir + '/trips.txt', header=0, encoding='utf-8-sig')
    df = df[df['service_id'].isin(todays_services)]
    df = df[~df['route_id'].isin(['RTTA_DEF', 'RTTA_REV'])]

    df.to_pickle(dest_dir + '/trips_' + date_of_analysis + '.pickle')

    logging.info("Created timetable for " + date_of_analysis + " in " + dest_dir)


if __name__ == "__main__":
    # run in own directory
    os.chdir(os.path.dirname(sys.argv[0]))
    source_data_dir = "../../data/raw/" + time.strftime("%Y%m%d", time.localtime())
    destination_data_dir = "../../data/interim/" + time.strftime("%Y%m%d", time.localtime())
    if not os.path.exists(destination_data_dir):
        os.makedirs(destination_data_dir)
    log_dir = '../../data/logs/'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    logging.basicConfig(filename=log_dir+'train_create_daily_timetable.log', level=logging.INFO,
                        format='%(asctime)s %(message)s')
    create_daily_timetable(source_data_dir, destination_data_dir, time.strftime("%Y%m%d", time.localtime()))
