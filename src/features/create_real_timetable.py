def create_real_timetable(data_dir, date_of_analysis):
    data_dir = data_dir + date_of_analysis
    print("Creating real timetable for " + date_of_analysis + " in " + data_dir)

    # load the static timetable into a data frame
    df_stop_times = pd.read_csv(data_dir + '/stop_times.txt', header=0,
                                encoding='utf-8-sig',
                                dtype={'stop_id': str},
                                parse_dates=['arrival_time', 'departure_time'])
    # date_parser=dateparse)

    # load the trip ids of that actual trips that happend on this day
    df_trips = pd.read_pickle(data_dir + '/trips_' + date_of_analysis + '.pickle')

    # remove any trips from stop_times that did NOT happen on this date
    df_stop_times = df_stop_times[df_stop_times['trip_id'].isin(df_trips['trip_id'])]

    # insert actual arrival, actual departure, and cancellation states into dataframe
    # mark all as N/A to start with, so we know which things never had real time updates
    df_stop_times.insert(2, 'arrival_delay', 'N/A')
    df_stop_times.insert(3, 'actual_arrival_time', 'N/A')
    df_stop_times.insert(5, 'departure_delay', 'N/A')
    df_stop_times.insert(6, 'actual_departure_time', 'N/A')
    df_stop_times.insert(7, 'schedule_relationship', 'N/A')

    # load all delays found on this date
    trip_delays = pickle.load(open(data_dir + "/collated_delays.pickle", "rb"))

    bar = Bar('Analyse trips', max=len(trip_delays))
    for trip in trip_delays:
        bar.next()
        if not trip.trip_id in df_trips['trip_id'].values:
            # print("Trip " + trip.trip_id + " was not supposed to run today!")
            continue

        for stop_time_update in trip.stop_time_updates:
            # some of these values might be 24:00, 25:00 etc to signfiy next day

            idx = df_stop_times[(df_stop_times['trip_id'] == trip.trip_id) &
                                (df_stop_times['stop_id'] == stop_time_update.stop_id)].index
            if idx.empty:
                # it shouldn't be
                continue

            idx = idx.item()

            # calculate the real time
            actual_arrival_time = update_time(date_of_analysis, df_stop_times.at[idx, 'arrival_time'],
                                              stop_time_update.arrival_delay)
            actual_departure_time = update_time(date_of_analysis, df_stop_times.at[idx, 'departure_time'],
                                                stop_time_update.departure_delay)

            # add the new values to the new columns

            df_stop_times.at[idx, 'arrival_delay'] = stop_time_update.arrival_delay
            df_stop_times.at[idx, 'actual_arrival_time'] = actual_arrival_time
            df_stop_times.at[idx, 'departure_delay'] = stop_time_update.departure_delay
            df_stop_times.at[idx, 'actual_departure_time'] = actual_departure_time
            df_stop_times.at[idx, 'schedule_relationship'] = stop_time_update.schedule_relationship

    bar.finish()

    df_stop_times.to_csv(data_dir + "/timetable_with_delays.csv")
    df_stop_times.to_pickle(data_dir + "/timetable_with_delays.pickle")
    print("Pickled the real timetable in " + data_dir)


def match_delays_with_trips(data_dir, date_of_analysis):
    data_dir = data_dir + date_of_analysis
    print("Creating real trip summaries " + date_of_analysis + " in " + data_dir)

    # load the trip ids of that actual trips that happend on this day
    df_trips = pd.read_pickle(data_dir + '/trips_' + date_of_analysis + '.pickle')

    # insert actual arrival, actual departure, and cancellation states into dataframe
    # mark all as N/A to start with, so we know which things never had real time updates
    df_trips.insert(4, 'maximum_arrival_delay', 'N/A')
    df_trips.insert(5, 'average_arrival_delay', 'N/A')
    df_trips.insert(7, 'maximum_departure_delay', 'N/A')
    df_trips.insert(8, 'average_departure_delay', 'N/A')
    df_trips.insert(9, 'schedule_relationship', 'N/A')

    # load all delays found on this date
    trip_delays = pickle.load(open(data_dir + "/collated_delays.pickle", "rb"))

    bar = Bar('Analyse trips', max=len(trip_delays))
    for trip in trip_delays:
        bar.next()
        if not trip.trip_id in df_trips['trip_id'].values:
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

    df_trips.to_csv(data_dir + "/trips_with_delays.csv")
    df_trips.to_pickle(data_dir + "/trips_with_delays.pickle")
    print("Pickled the real trip summaries in " + data_dir)


def update_time(date_of_analysis, time_str, delay_val):
    try:
        delay_val = int(delay_val)
        original_time = time.mktime(time.strptime(date_of_analysis + time_str, "%Y%m%d%H:%M:%S"))
        updated_time = original_time + delay_val
        updated_time = time.localtime(updated_time)
        return time.strftime("%H:%M:%S", updated_time)
    except:
        return "Exception"

