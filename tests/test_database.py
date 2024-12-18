# standard library imports
import datetime as dt
import importlib.resources as ir
from unittest import mock

# 3rd party library imports
import pandas as pd

# local imports
from swlogs.loglogs import LogLogs
from .common import CommonTestCase


class TestSuite(CommonTestCase):

    def test_bot_smoke(self):
        """
        Scenario:  read log file

        Expected result:  the contents of several tables is verified
        """

        logfile = ir.files('tests.data').joinpath('smoke.log')
        with LogLogs(logfile) as o:
            with mock.patch.object(o, 'conn', new=self.conn):
                o.run()

        # Verify the bots table.
        actual = pd.read_sql(
            'select * from swlogs.bots',
            self.engine,
            index_col='ua'
        )

        # The id column is volatile and does not add value, so get rid of it.
        actual = actual.drop(labels='id', axis='columns')

        data = [
            'dspace-internal', 'bingbot/2.0', "Safari/iOS/WebKit/iPhone"
        ]
        index = pd.Index(data, name='ua')
        data = {
            'hits': [86, 12, 2],
            'error_pct': [7.0, 0, 0],
            'c429': [0, 0, 0],
            'robots': [False, False, False],
            'xmlui': [False, False, False],
            'sitemaps': [False, False, False],
            'item_pct': [0.0, 0.0, 0.0],
            'date': [
                dt.date.today() - dt.timedelta(days=1),
                dt.date.today() - dt.timedelta(days=1),
                dt.date.today() - dt.timedelta(days=1),
            ]
        }
        expected = pd.DataFrame(index=index, data=data)

        pd.testing.assert_frame_equal(
            actual, expected, check_exact=False, rtol=0.1
        )

        # Verify the overall table.
        actual = pd.read_sql(
            'select * from swlogs.overall',
            self.engine,
            index_col='date'
        )

        # The id column is volatile and does not add value, so get rid of it.
        actual = actual.drop(labels='id', axis='columns')

        data = [dt.date(2024, 11, 7)]
        index = pd.Index(data, name='date')
        data = {
            'bytes': [1233768],
            'hits': [100],
        }
        expected = pd.DataFrame(index=index, data=data)

        pd.testing.assert_frame_equal(actual, expected)

        # verify the ip24 table
        actual = pd.read_sql(
            'select * from swlogs.ip24 order by ip',
            self.engine,
            index_col='date'
        )

        data = [
            dt.date.today() - dt.timedelta(days=1),
            dt.date.today() - dt.timedelta(days=1),
            dt.date.today() - dt.timedelta(days=1),
        ]
        index = pd.Index(data, name='date')
        data = {
            'ip': ['24.57.50.0/24', '52.167.144.0/24', '153.90.6.0/24'],
            'hits': [2, 12, 86],
            'error_pct': [0.0, 0.0, 7.0]
        }
        expected = pd.DataFrame(index=index, data=data)

        pd.testing.assert_frame_equal(
            actual, expected, check_exact=False, rtol=0.1
        )

        # verify the ip32 table
        actual = pd.read_sql(
            'select * from swlogs.ip32 order by ip',
            self.engine,
            index_col='date'
        )

        data = [
            dt.date.today() - dt.timedelta(days=1),
            dt.date.today() - dt.timedelta(days=1),
            dt.date.today() - dt.timedelta(days=1),
        ]
        index = pd.Index(data, name='date')
        data = {
            'ip': ['24.57.50.45/32', '52.167.144.22/32', '153.90.6.244/32'],
            'hits': [2, 12, 86],
            'error_pct': [0.0, 0.0, 7.0]
        }
        expected = pd.DataFrame(index=index, data=data)

        pd.testing.assert_frame_equal(
            actual, expected, check_exact=False, rtol=0.1
        )

    def test_item_percentage(self):
        """
        Scenario:  compute the item views percentage

        Expected result:  no errors
        """
        logfile = ir.files('tests.data').joinpath('10-items.log')
        with LogLogs(logfile) as o:
            with mock.patch.object(o, 'conn', new=self.conn):
                o.run()

        actual = pd.read_sql(
            'select * from swlogs.bots', self.engine, index_col='ua'
        )
        actual = actual['item_pct']

        data = [
            'Chrome/Win10/Blink',
            'Chrome/Mactel32/Blink',
            'Firefox/iOS/WebKit/iPhone'
        ]
        index = pd.Index(data, name='ua')
        data = [71.4, 0.0, 100.0]
        expected = pd.Series(index=index, data=data, name='item_pct')

        pd.testing.assert_series_equal(
            actual, expected, check_exact=False, rtol=0.1
        )

    def test_split_over_two_days(self):
        """
        Scenario:  read log file that is split over two days.  99 hits are
        from today, 1 hit from previous day

        Expected result:  no errors
        """
        logfile = ir.files('tests.data').joinpath('two-days.log')
        with LogLogs(logfile) as o:
            with mock.patch.object(o, 'conn', new=self.conn):
                o.run()

        actual = pd.read_sql(
            'select * from swlogs.overall', self.engine, index_col='date'
        )

        # The id column is volatile and does not add value, so get rid of it.
        actual = actual.drop(labels='id', axis='columns')

        data = [dt.date(2024, 11, 6), dt.date(2024, 11, 7)]
        index = pd.Index(data, name='date')
        data = {
            'bytes': [9352, 1224416],
            'hits': [1, 99],
        }
        expected = pd.DataFrame(index=index, data=data)

        pd.testing.assert_frame_equal(actual, expected)

    def test_gzipped(self):
        """
        Scenario:  read gzipped log file

        Expected result:  no errors
        """
        logfile = ir.files('tests.data').joinpath('gzipped.log.gz')
        with LogLogs(logfile) as o:
            with mock.patch.object(o, 'conn', new=self.conn):
                o.run()

        actual = pd.read_sql(
            'select * from swlogs.bots', self.engine, index_col='ua'
        )

        # The id column is volatile and does not add value, so get rid of it.
        actual = actual.drop(labels='id', axis='columns')

        data = [
            'dspace-internal', 'bingbot/2.0', "Safari/iOS/WebKit/iPhone"
        ]
        index = pd.Index(data, name='ua')
        data = {
            'hits': [86, 12, 2],
            'error_pct': [7.0, 0, 0],
            'c429': [0, 0, 0],
            'robots': [False, False, False],
            'xmlui': [False, False, False],
            'sitemaps': [False, False, False],
            'item_pct': [0.0, 0.0, 0.0],
            'date': [
                dt.date.today() - dt.timedelta(days=1),
                dt.date.today() - dt.timedelta(days=1),
                dt.date.today() - dt.timedelta(days=1),
            ]
        }
        expected = pd.DataFrame(index=index, data=data)

        pd.testing.assert_frame_equal(
            actual, expected, check_exact=False, rtol=0.1
        )
