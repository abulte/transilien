"""Tests module"""

import os
import sys
import json
import unittest
import time
from datetime import datetime, timedelta

TOPDIR = os.path.join(os.path.dirname(__file__), "..")
sys.path.append(TOPDIR)

import web
import utils
from test_flag import FlagBaseTestCase


class WebTestCase(FlagBaseTestCase):

    def setUp(self):
        super(WebTestCase, self).setUp()
        self.app = web.app.test_client()
        web.app.config['TESTING'] = True

    def _get_api(self, since=None):
        """Helper"""
        url = '/api'
        if since:
            url += '?since=%s' % int(since)
        rv = self.app.get(url)
        self.assertEqual(rv.status_code, 200)
        return json.loads(rv.data)

    def test_api_empty(self):
        """Test /api w/o data"""
        data = self._get_api()
        self.assertTrue('retour' in data)
        self.assertTrue('aller' in data)
        self.assertEqual(data['aller'], [])
        self.assertEqual(data['retour'], [])

    def test_api_w_data(self):
        """Test /api w/ data"""
        self._create_record(miss='LOL')
        data = self._get_api()
        self.assertTrue('retour' in data)
        self.assertTrue('aller' in data)
        trains = data['aller'] + data['retour']
        self.assertEqual(len(trains), 1)
        self.assertEqual(trains[0]['miss'], 'LOL')

    def test_api_since_default(self):
        """Test /api w/ since default arg"""
        self._create_record(date=datetime.now() - timedelta(days=2))
        data = self._get_api()
        self.assertEqual(data['aller'], [])
        self.assertEqual(data['retour'], [])

    def test_api_since(self):
        """Test /api w/ since default arg"""
        self._create_record(date=datetime.now() - timedelta(days=2), miss='LOL')
        since = datetime.now() - timedelta(days=3)
        data = self._get_api(since=time.mktime(since.timetuple()))
        trains = data['aller'] + data['retour']
        self.assertEqual(len(trains), 1)
        self.assertEqual(trains[0]['miss'], 'LOL')

    def test_api_aggregate_bad_args(self):
        """Test api aggregate w/ wrong url arg"""
        rv = self.app.get('/api/aggregate')
        self.assertEqual(rv.status_code, 404)
        rv = self.app.get('/api/aggregate/minute')
        self.assertEqual(rv.status_code, 400)

    def test_api_aggregate_day(self):
        """Test api aggregate by day"""
        start_date = utils.get_datetime_from_iso('2017-02-12 01:01:01')
        self._create_record(date=start_date)
        self._create_record(num=256, etat='R', date=start_date)
        self._create_record(num=789, etat='R', date=start_date)
        self._create_record(date=start_date - timedelta(days=1))
        self._create_record(num=256, etat='S', date=start_date - timedelta(days=1))
        rv = self.app.get('/api/aggregate/day')
        data = json.loads(rv.data)
        self.assertCountEqual(data, [{
            'count': 1,
            'date': '2017-02-11',
            'type': 'NORMAL'
        }, {
            'count': 1,
            'date': '2017-02-11',
            'type': 'SUPPR'
        }, {
            'count': 1,
            'date': '2017-02-12',
            'type': 'NORMAL'
        }, {
            'count': 2,
            'date': '2017-02-12',
            'type':
            'RETARD'
        }])

    def test_api_aggregate_month(self):
        """Test api aggregate by day"""
        start_date = utils.get_datetime_from_iso('2017-02-12 01:01:01')
        self._create_record(date=start_date)
        self._create_record(num=256, etat='R', date=start_date)
        self._create_record(num=789, etat='R', date=start_date)
        self._create_record(date=start_date - timedelta(days=30))
        self._create_record(num=256, etat='S', date=start_date - timedelta(days=30))
        rv = self.app.get('/api/aggregate/month')
        data = json.loads(rv.data)
        self.assertCountEqual(data, [{
            'count': 1,
            'date': '2017-01',
            'type': 'NORMAL'
        }, {
            'count': 1,
            'date': '2017-01',
            'type': 'SUPPR'
        }, {
            'count': 1,
            'date': '2017-02',
            'type': 'NORMAL'
        }, {
            'count': 2,
            'date': '2017-02',
            'type':
            'RETARD'
        }])

    def test_api_aggregate_year(self):
        """Test api aggregate by year"""
        start_date = utils.get_datetime_from_iso('2017-02-12 01:01:01')
        self._create_record(date=start_date)
        self._create_record(num=256, etat='R', date=start_date)
        self._create_record(num=789, etat='R', date=start_date)
        self._create_record(date=start_date - timedelta(days=365))
        self._create_record(num=256, etat='S', date=start_date - timedelta(days=365))
        rv = self.app.get('/api/aggregate/year')
        data = json.loads(rv.data)
        self.assertCountEqual(data, [{
            'count': 1,
            'date': '2016',
            'type': 'NORMAL'
        }, {
            'count': 1,
            'date': '2016',
            'type': 'SUPPR'
        }, {
            'count': 1,
            'date': '2017',
            'type': 'NORMAL'
        }, {
            'count': 2,
            'date': '2017',
            'type':
            'RETARD'
        }])

    def test_api_aggregate_hour(self):
        """Test api aggregate by year"""
        start_date = utils.get_datetime_from_iso('2017-02-12 01:01:01')
        self._create_record(date=start_date)
        self._create_record(num=256, etat='R', date=start_date)
        self._create_record(num=789, etat='R', date=start_date)
        self._create_record(date=start_date - timedelta(hours=1))
        self._create_record(num=256, etat='S', date=start_date - timedelta(hours=1))
        rv = self.app.get('/api/aggregate/hour')
        data = json.loads(rv.data)
        self.assertCountEqual(data, [{
            'count': 1,
            'date': '2017-02-12 00:',
            'type': 'NORMAL'
        }, {
            'count': 1,
            'date': '2017-02-12 00:',
            'type': 'SUPPR'
        }, {
            'count': 1,
            'date': '2017-02-12 01:',
            'type': 'NORMAL'
        }, {
            'count': 2,
            'date': '2017-02-12 01:',
            'type':
            'RETARD'
        }])

    def test_api_aggregate_hour_overall(self):
        """Test api aggregate by hour overall"""
        start_date = utils.get_datetime_from_iso('2017-02-12 01:01:01')
        self._create_record(date=start_date)
        self._create_record(num=256, etat='R', date=start_date)
        self._create_record(num=789, etat='R', date=start_date)
        self._create_record(date=start_date - timedelta(days=1))
        self._create_record(num=256, etat='S', date=start_date - timedelta(days=1))
        rv = self.app.get('/api/aggregate/hour_overall')
        data = json.loads(rv.data)
        self.assertCountEqual(data, [{
            'count': 1,
            'date': '01',
            'type': 'SUPPR'
        }, {
            'count': 2,
            'date': '01',
            'type': 'NORMAL'
        }, {
            'count': 2,
            'date': '01',
            'type': 'RETARD'
        }])

    def test_api_aggregate_weekday(self):
        """Test api aggregate by weekday"""
        start_date = utils.get_datetime_from_iso('2017-02-12 01:01:01')
        self._create_record(date=start_date)
        self._create_record(num=256, etat='R', date=start_date)
        self._create_record(num=789, etat='R', date=start_date)
        self._create_record(date=start_date - timedelta(weeks=1))
        self._create_record(num=256, etat='S', date=start_date - timedelta(weeks=1))
        rv = self.app.get('/api/aggregate/weekday')
        data = json.loads(rv.data)
        self.assertCountEqual(data, [{
            'count': 1,
            'date': 7,
            'type': 'SUPPR'
        }, {
            'count': 2,
            'date': 7,
            'type': 'NORMAL'
        }, {
            'count': 2,
            'date': 7,
            'type': 'RETARD'
        }])

    def test_api_aggregate_since(self):
        """Test api aggregate since arg"""
        start_date = utils.get_datetime_from_iso('2017-02-12 01:01:01')
        self._create_record(date=start_date)
        self._create_record(date=start_date - timedelta(days=2))
        since = start_date - timedelta(days=1)
        rv = self.app.get('/api/aggregate/hour?since=%s' % int(time.mktime(since.timetuple())))
        data = json.loads(rv.data)
        self.assertCountEqual(data, [{
            'count': 1,
            'date': '2017-02-12 01:',
            'type': 'NORMAL'
        }])


if __name__ == '__main__':
    unittest.main()
