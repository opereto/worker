from datetime import *

def get_duration(start, end):
    start_ts=None
    if start:
        start_ts = int(get_ts_from_time(start))
    if not end:
        end_ts = get_utc_current_ts()
    elif end:
        end_ts = int(get_ts_from_time(end))

    if start_ts and end_ts:
        delta = int(end_ts)-int(start_ts)
        if int(delta)>0:
            return int(delta)
    return 0


def get_duration_str(seconds):
    return str(timedelta(seconds=seconds))

def _get_ts_from_datetime(dt):
    return long(seconds_diff_between_dates(dt, datetime(1970, 1, 1)))

def _get_datetime_from_ts(ts):
    return datetime.utcfromtimestamp(long(ts))

def _get_datetime_from_str(str):
    try:
        return datetime.strptime(str, '%Y-%m-%dT%H:%M:%S.%f')
    except ValueError:
        return datetime.strptime(str, '%Y-%m-%dT%H:%M:%S')


def get_str_from_datetime(dt):
    return dt.isoformat()


def ts_to_log_datetime(ts):
    try:
        return get_time_from_ts(ts)
    except Exception,e:
        return ''

def get_time_from_ts(ts):
    dt = _get_datetime_from_ts(long(ts))
    return get_str_from_datetime(dt)

def get_utc_current_time():
    return get_str_from_datetime(datetime.utcnow())

def get_utc_current_ts():
    return _get_ts_from_datetime(datetime.utcnow())


def get_ts_from_time(str):
    dt = _get_datetime_from_str(str)
    return _get_ts_from_datetime(dt)

def seconds_diff_between_dates(date1, date2):
    return int((date1-date2).total_seconds())