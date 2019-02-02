import datetime


def merge_trips(old_trip, new_trip):
    if old_trip.trip_id != new_trip.trip_id:
        return old_trip
    # do not compare timestamps. Same timestamps can have different delay data.

    for new_stop_time_update in new_trip.stop_time_updates:
        if new_stop_time_update in old_trip.stop_time_updates:
            # take the new one for now
            old_trip.stop_time_updates[new_stop_time_update] = new_trip.stop_time_updates[new_stop_time_update]
            old_trip.timestamp = new_trip.timestamp
        else:
            old_trip.stop_time_updates[new_stop_time_update] = new_trip.stop_time_updates[new_stop_time_update]

    return old_trip


def update_time(date_of_analysis_str, time_str, delay_val):
    try:
        # this could be optimised
        delay_val = int(delay_val)
        original_time = datetime.datetime.strptime(date_of_analysis_str + time_str, "%Y%m%d%H:%M:%S")
        updated_time = original_time + datetime.timedelta(seconds=delay_val)
        return updated_time.strftime("%H:%M:%S")
    except:
        return "Exception"


def convert_to_timestamp(date_of_analysis_str, time_str):
    hours = int(time_str[0:2])
    if hours > 23:
        time_str = '0' + str(hours-23) + time_str[2:]
        retval = datetime.datetime.strptime(date_of_analysis_str + time_str, "%Y%m%d%H:%M:%S")
        retval += datetime.timedelta(days=1)
        return retval
    else:
        retval = datetime.datetime.strptime(date_of_analysis_str + time_str, "%Y%m%d%H:%M:%S")
        return retval
