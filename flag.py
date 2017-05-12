"""Requests transilien API for live train schedule"""

import xml.etree.ElementTree as ET

import click
import requests

import settings
import database
import notifications
from utils import get_datetime_from_iso, get_limit_date, convert_to_iso


BASE_URL = 'http://api.transilien.com/gare/%s/depart/%s/'


def record(data):
    """Record a data row into DB and trigger alert if needed"""
    table = database.get()['results']

    data['type'] = 'NORMAL'
    etat = data.get('etat', False)
    if etat:
        if etat.startswith('Suppr') or etat == 'S':
            data['type'] = 'SUPPR'
        elif etat.startswith('Retard') or etat == 'R':
            data['type'] = 'RETARD'
        else:
            data['type'] = etat
    else:
        data['etat'] = ''

    # convert to ISO
    data['date'] = convert_to_iso(data['date'])
    data['weekday'] = get_datetime_from_iso(data['date']).isoweekday()

    limit_date = get_limit_date()
    # no duplicates
    # date can change for same train, num supposed unique each day
    try:
        existing = table.find_one(table.table.columns.date > limit_date, num=data['num'])
    # AttributeError on `date` when DB is empty (first run)
    except AttributeError:
        existing = None

    do_notif = False
    if existing is None:
        if data['type'] == 'SUPPR':
            do_notif = True
        table.insert(data)
    # type has changed, maybe suppr
    elif data['type'] != existing.type and data['type'] == 'SUPPR':
        do_notif = True
        table.update({
            'id': existing.id,
            'etat': data['etat'],
            'type': data['type']
        }, ['id'])
    # date has changed, compute delay
    elif data['date'] != existing['date']:
        data['type'] = 'RETARD'
        delta = get_datetime_from_iso(data['date']) - get_datetime_from_iso(existing['date'])
        data['delay'] = delta.seconds
        table.update({
            'id': existing.id,
            'etat': data['etat'],
            'type': data['type'],
            'delay': data['delay']
        }, ['id'])
    # no delay but RETARD??
    elif data['type'] != existing['type']:
        table.update({
            'id': existing.id,
            'etat': data['etat'],
            'type': data['type']
        }, ['id'])
        # sometimes train are "uncancelled" apparently
        if existing['type'] == 'SUPPR':
            notifications.send(data, cancel=True)

    if do_notif:
        notifications.send(data)


def api_request(from_station, to_station):
    """Request Transilien API"""
    url = BASE_URL % (from_station, to_station)
    req = requests.get(url, auth=(settings.TRANSILIEN_API_LOGIN, settings.TRANSILIEN_API_PWD))
    if req.status_code == 200:
        root = ET.fromstring(req.text.encode('utf-8'))
        for train in root.iter('train'):
            data = {
                'from_gare': from_station,
                'to_gare': to_station
            }
            for info in train:
                data[info.tag] = info.text
            record(data)
    else:
        click.secho('ERROR for %s to %s, status %s : %s' % (
            from_station, to_station, req.status_code, req.text
        ), err=True, bg='red')


@click.command()
@click.option('--from-station', default=None, help='From station (override config)')
@click.option('--to-station', default=None, help='To station (override config)')
def run(from_station, to_station):
    """CLI cmd"""
    if not from_station:
        from_station = settings.FROM_STATION_CODE
    if not to_station:
        to_station = settings.TO_STATION_CODE

    api_request(from_station, to_station)
    api_request(to_station, from_station)


if __name__ == "__main__":
    run() # pylint: disable=E1120
