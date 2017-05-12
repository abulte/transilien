"""Generate a list of trains and export to JSON"""

import json

import click

import database
import settings


def get_nominal_hour(train_num):
    """Get the nominal hour for a train num (most frequent)"""
    res = database.get().query("""
        SELECT count(*) as count, substr(date, 12, 5) as hour
        FROM results WHERE num = '%s'
        GROUP BY hour ORDER BY count DESC LIMIT 1;
    """ % train_num)
    return next(res).hour


@click.command()
def make_train_list():
    """Compute a distinct train list for a typical day"""
    res_db = database.get()
    table = res_db['results']

    def get_count_days(weekdays_list, num):
        """Return the count of this trains on given weekdays"""
        res = res_db.query("SELECT count(*) as count from results \
            where num = '%s' and weekday in (%s)" % (
                num,
                ','.join([str(w) for w in weekdays_list])
            ))
        return next(res).count

    trains = {}
    # use NORMAL to get the nominal hour
    for train in table.find(type='NORMAL'):
        existing = trains.get(train.num)
        if not existing:
            trains[train.num] = {
                'hour': get_nominal_hour(train.num),
                'count': len(list(table.find(num=train.num))),
                'direction': 'poissy' if train.to_gare == str(settings.FROM_STATION_CODE) \
                    else 'paris',
                'count_weekend': get_count_days([6, 7], train.num),
                'count_week': get_count_days([1, 2, 3, 4, 5], train.num),
            }

    # restructure as list
    # in Python3, spread or something would be great :-(
    trains_list = [
        {
            'num': k,
            'hour': v['hour'],
            'direction': v['direction'],
            'count': v['count'],
            'count_weekend': v['count_weekend'],
            'count_week': v['count_week'],
        } for k, v in trains.items()
    ]

    with open('trains.json', 'w') as jsonfile:
        jsonfile.write(json.dumps(trains_list, indent=2))


if __name__ == '__main__':
    make_train_list()
