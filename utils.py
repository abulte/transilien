"""Utils"""

from datetime import datetime, timedelta


def convert_to_iso(string):
    return get_datestring(get_datetime(string))


def get_datetime(string):
    "Format : 22/07/2015 10:23"
    dt_format = '%d/%m/%Y %H:%M'
    return datetime.strptime(string, dt_format)


def get_datetime_from_iso(string):
    dt_format = '%Y-%m-%d %H:%M:%S'
    return datetime.strptime(string, dt_format)


def get_datestring(thedatetime):
    dt_format = '%Y-%m-%d %H:%M:%S'
    return thedatetime.strftime(dt_format)


def get_limit_date():
    """Return `limit_date` for de-duplicating the trains
    i.e. now - max delay before considering a late train is a new train
    """
    return datetime.now() - timedelta(hours=4)
