# -*- coding: utf-8 -*-
"""Tests module"""

import os
import sys
import unittest
import tempfile
from datetime import datetime, timedelta
import requests_mock

TOPDIR = os.path.join(os.path.dirname(__file__), "..")
sys.path.append(TOPDIR)

import settings
import database
import flag
import utils


class FlagBaseTestCase(unittest.TestCase):

    def setUp(self):
        self.db_fd, self.db_file_path = tempfile.mkstemp()
        settings.DATABASE_URI = 'sqlite:///%s' % self.db_file_path
        settings.TESTING = True
        # insert a dummy record to define a "model" in dataset
        # otherwise it won't find the columns in an empty test database
        self.database = database.get()
        self.database['results'].insert({
            'date': 'X',
            'num': 'X',
            'miss': 'X',
            'term': 1,
            'etat': 'X',
            'type': 'X',
            'from_gare': '123',
            'to_gare': '123',
            'delay': 0,
            'weekday': 0
        })
        self.database['results'].delete()

        self.database['aggregate'].insert({
            'week': 1, 'on_time': 1, 'late': 1, 'canceled': 1, 'total_late': 1
        })
        self.database['aggregate'].delete()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(self.db_file_path)

    def _get_transilien_datestring(self, thedatetime):
        """Translate a datetime to the internal transilien format"""
        return thedatetime.strftime('%d/%m/%Y %H:%M')

    def _create_record(
            self,
            date=datetime.now(),
            num=123,
            miss='LOL',
            term=87384008,
            etat=None,
            from_gare=settings.FROM_STATION_CODE,
            to_gare=settings.TO_STATION_CODE
        ):
        """Helper to create a record, w/ default values"""
        date = self._get_transilien_datestring(date)
        flag.record({
            'date': date,
            'num': num,
            'miss': miss,
            'term': term,
            'etat': etat,
            'from_gare': from_gare,
            'to_gare': to_gare
        })


class FlagRecordTestCase(FlagBaseTestCase):

    def _get_results(self):
        """Helper to get all results"""
        return self.database['results'].all()

    def _count_results(self):
        """Helper to count all results"""
        return self.database['results'].count()

    def test_empty_db(self):
        self.assertEqual(self._count_results(), 0)

    def test_record_new_normal(self):
        """Record a new train with NORMAL type"""
        train_date = datetime.now()
        self._create_record(date=train_date)

        # one record created
        self.assertEqual(self._count_results(), 1)

        res = self._get_results()
        # attrs are OK
        for train in res:
            self.assertEqual(train['etat'], '')
            self.assertEqual(train['type'], 'NORMAL')
            self.assertEqual(train['delay'], None)
            self.assertEqual(train['from_gare'], str(settings.FROM_STATION_CODE))
            self.assertEqual(train['to_gare'], str(settings.TO_STATION_CODE))
            # we loose the seconds while converting to transilien format
            expected_date = train_date.replace(second=0)
            self.assertEqual(train['date'], utils.get_datestring(expected_date))
            self.assertEqual(train['num'], '123')
            self.assertEqual(train['miss'], 'LOL')
            self.assertEqual(train['term'], 87384008)
            self.assertEqual(train.weekday, train_date.isoweekday())

    def test_record_existing_w_delay(self):
        """Existing train w/ a different date, delay computed"""
        # normal train
        train_date = datetime.now()
        self._create_record(train_date)

        # same, w/ delay
        delayed_date = train_date + timedelta(minutes=2)
        self._create_record(date=delayed_date)

        # one record created, then updated
        self.assertEqual(self._count_results(), 1)

        res = self._get_results()
        for train in res:
            self.assertEqual(train['delay'], 120)

    def test_record_existing_other_day(self):
        """Existing train w/ a different date < 1 day, no delay"""
        # yesterday train
        train_date = datetime.now()
        self._create_record(train_date - timedelta(days=1))

        # same today
        delayed_date = train_date
        self._create_record(date=delayed_date)

        self.assertEqual(self._count_results(), 2)

        res = self._get_results()
        for train in res:
            self.assertEqual(train['type'], 'NORMAL')

    def test_record_new_w_suppr(self):
        """New train that has been removed from service"""
        self._create_record(etat='Suppr')
        self._create_record(num=356, etat='S')
        self._create_record(num=789, etat=u'Supprimé')

        self.assertEqual(self._count_results(), 3)

        res = self._get_results()
        for train in res:
            self.assertEqual(train['type'], 'SUPPR')

    def test_record_existing_w_suppr(self):
        """Existing train that has been removed from service"""
        self._create_record()
        self._create_record(etat='S')

        self.assertEqual(self._count_results(), 1)

        res = self._get_results()
        for train in res:
            self.assertEqual(train['type'], 'SUPPR')

    def test_record_existing_w_unsuppr(self):
        """Removed train that has been put back on service"""
        self._create_record(etat='S')
        self._create_record()

        self.assertEqual(self._count_results(), 1)

        res = self._get_results()
        for train in res:
            self.assertEqual(train['type'], 'NORMAL')

    def test_record_existing_w_unsuppr_delay(self):
        """Removed train that has been put back on service w/ delay"""
        train_date = datetime.now()
        self._create_record(date=train_date, etat='S')
        self._create_record(date=train_date + timedelta(minutes=2))

        self.assertEqual(self._count_results(), 1)

        res = self._get_results()
        for train in res:
            self.assertEqual(train['type'], 'RETARD')
            self.assertEqual(train['delay'], 120)

    def test_retard_etats(self):
        """Test Retard* etat from API"""
        self._create_record(etat='Retard')
        self._create_record(num=356, etat=u'Retardé')

        self.assertEqual(self._count_results(), 2)

        res = self._get_results()
        for train in res:
            self.assertEqual(train['type'], 'RETARD')

    def test_unknown_etat(self):
        """Test the recording of an unknown etat from API"""
        self._create_record(etat='X' * 50)

        self.assertEqual(self._count_results(), 1)

        res = self._get_results()
        for train in res:
            self.assertEqual(train['type'], 'X' * 50)
            self.assertEqual(train['etat'], 'X' * 50)


class FlagParserTestCase(FlagBaseTestCase):

    response_text = """<?xml version="1.0" encoding="UTF-8"?>
    <passages gare="87393009">
        <train>
            <date mode="R">23/05/2012 12:14</date>
            <num>148614</num>
            <miss>VICK</miss>
            <term>87393157</term>
            <etat>S</etat>
        </train>
        <train>
            <date mode="R">23/05/2012 12:14</date>
            <num>148614</num>
            <miss>VICK</miss>
            <term>87393157</term>
            <etat>R</etat>
        </train>
        <train>
            <date mode="R">23/05/2012 12:14</date>
            <num>148614</num>
            <miss>VICK</miss>
            <term>87393157</term>
        </train>
    </passages>"""

    def test_parse_request(self):
        """Test the parse_request method"""
        with requests_mock.Mocker() as mock:
            mock.get(
                flag.BASE_URL % (settings.TO_STATION_CODE, settings.FROM_STATION_CODE),
                text=self.response_text
            )
            flag.api_request(settings.TO_STATION_CODE, settings.FROM_STATION_CODE)
            self.assertEqual(self.database['results'].count(), 3)
            res = self.database['results'].all()
            for idx, train in enumerate(res):
                if idx == 0:
                    self.assertEqual(train.type, 'SUPPR')
                    self.assertEqual(train.etat, 'S')
                elif idx == 1:
                    self.assertEqual(train.type, 'RETARD')
                    self.assertEqual(train.etat, 'R')
                elif idx == 2:
                    self.assertEqual(train.type, 'NORMAL')
                    self.assertEqual(train.etat, '')
                self.assertEqual(train.from_gare, str(settings.TO_STATION_CODE))
                self.assertEqual(train.to_gare, str(settings.FROM_STATION_CODE))
                self.assertEqual(train.term, 87393157)
                self.assertEqual(train.miss, 'VICK')
                self.assertEqual(train.date, '2012-05-23 12:14:00')
                self.assertEqual(train.num, '148614')


if __name__ == '__main__':
    unittest.main()
