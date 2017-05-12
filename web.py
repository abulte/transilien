"""Web interface"""
from datetime import datetime, timedelta

from flask import Flask, jsonify, request, g
from werkzeug.exceptions import BadRequest
from flask_cors import CORS

import database
import settings
from utils import get_datestring
from frontend import frontend


# define static_url_path to avoid conflict w/ blueprint static
app = Flask(__name__, static_url_path='/static/core')
app.debug = settings.DEBUG
app.register_blueprint(frontend)
CORS(app)


def connect_db():
    """Connects to the specific database."""
    return database.get()


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


def get_since(default_days_ago=1):
    """Get since from request or provide default date"""
    since = request.args.get('since')
    if since:
        try:
            since_date = datetime.fromtimestamp(int(since))
        except ValueError:
            raise BadRequest()
    elif default_days_ago:
        since_date = datetime.now() - timedelta(days=default_days_ago)
    else:
        return None

    return get_datestring(since_date)


@app.route('/api')
def api():
    """API root (list last results)"""
    table = get_db()['results']
    since_date = get_since()

    aller = table.find(
        table.table.columns.date > since_date,
        from_gare=settings.FROM_STATION_CODE,
        order_by='-date'
    )
    retour = table.find(
        table.table.columns.date > since_date,
        from_gare=settings.TO_STATION_CODE,
        order_by='-date'
    )

    return jsonify(
        aller=[r for r in aller],
        retour=[r for r in retour],
        infos={
            'from_station': settings.FROM_STATION_LABEL,
            'to_station': settings.TO_STATION_LABEL
        }
    )


@app.route('/api/aggregate/<frequency>')
def api_aggregate(frequency):
    """Aggregate trains by type on given frequency"""
    if frequency == 'hour':
        group_by = 'substr(date, 0, 15)'
    elif frequency == 'day':
        group_by = 'substr(date, 0, 11)'
    elif frequency == 'month':
        group_by = 'substr(date, 0, 8)'
    elif frequency == 'year':
        group_by = 'substr(date, 0, 5)'
    elif frequency == 'hour_overall':
        group_by = 'substr(date, 12, 2)'
    elif frequency == 'weekday':
        group_by = 'weekday'
    else:
        raise BadRequest()

    since = get_since(default_days_ago=None)

    res = get_db().query("""
        SELECT
        %(group_by)s as date, type, COUNT(*) as count
        FROM results
        %(since)s
        GROUP BY %(group_by)s, type;
    """ % {
        'group_by': group_by,
        'since': "WHERE date > '%s'" % since if since else ''
    })

    return jsonify([r for r in res])


if __name__ == '__main__':
    app.run(host='0.0.0.0')
