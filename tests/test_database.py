import datetime as dt
import importlib.resources as ir
import sqlite3
import tempfile
import unittest
from unittest import mock

import pandas as pd

from swlogs.loglogs import LogLogs


@mock.patch('swlogs.loglogs.date')
class TestSuite(unittest.TestCase):

    def test_bot_smoke(self, mock_dt):
        """
        Scenario:  read log file

        Expected result:  bot hits are verified
        """
        mock_dt.today.return_value = dt.date.today()
        mock_dt.side_effect = lambda *args, **kw:  dt.date(*args, **kw)

        logfile = ir.files('tests.data').joinpath('smoke.log')
        with tempfile.TemporaryDirectory() as tdir:
            dbfile = f"{tdir}/test.db"
            with LogLogs(logfile, dbfile=dbfile) as o:
                o.run()

            with sqlite3.connect(
                dbfile,
                detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
            ) as conn:
                actual = pd.read_sql(
                    'select * from bots', conn, index_col='ua'
                )

        data = [
            'dspace-internal', 'bingbot/2.0', "Safari/iOS/WebKit on iPhone"
        ]
        index = pd.Index(data, name='ua')
        data = {
            'hits': [86, 12, 2],
            'error_pct': [7.0, 0, 0],
            '429': [0, 0, 0],
            'robots': [0, 0, 0],
            'xmlui': [0, 0, 0],
            'sitemaps': [0, 0, 0],
            'date': [
                dt.date(2024, 11, 7),
                dt.date(2024, 11, 7),
                dt.date(2024, 11, 7),
            ]
        }
        expected = pd.DataFrame(index=index, data=data)

        pd.testing.assert_frame_equal(
            actual, expected, check_exact=False, rtol=0.1
        )

    def test_overall_smoke(self, mock_dt):
        """
        Scenario:  read log file

        Expected result:  overall hits are verified
        """
        mock_dt.today.return_value = dt.date.today()
        mock_dt.side_effect = lambda *args, **kw:  dt.date(*args, **kw)

        logfile = ir.files('tests.data').joinpath('smoke.log')
        with tempfile.TemporaryDirectory() as tdir:
            dbfile = f"{tdir}/test.db"
            with LogLogs(logfile, dbfile=dbfile) as o:
                o.run()

            with sqlite3.connect(
                dbfile,
                detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
            ) as conn:
                actual = pd.read_sql(
                    'select * from overall', conn, index_col='date'
                )

        data = [dt.date(2024, 11, 7)]
        index = pd.Index(data, name='date')
        data = {
            'bytes': [1233768],
            'hits': [100],
        }
        expected = pd.DataFrame(index=index, data=data)

        pd.testing.assert_frame_equal(actual, expected)

    def test_split_over_two_days(self, mock_dt):
        """
        Scenario:  read log file that is split over two days.  99 hits are
        from today, 1 hit from previous day

        Expected result:  overall hits are verified
        """
        mock_dt.today.return_value = dt.date.today()
        mock_dt.side_effect = lambda *args, **kw:  dt.date(*args, **kw)

        logfile = ir.files('tests.data').joinpath('two-days.log')
        with tempfile.TemporaryDirectory() as tdir:
            dbfile = f"{tdir}/test.db"
            with LogLogs(logfile, dbfile=dbfile) as o:
                o.run()

            with sqlite3.connect(
                dbfile,
                detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
            ) as conn:
                actual = pd.read_sql(
                    'select * from overall', conn, index_col='date'
                )

        data = [dt.date(2024, 11, 6), dt.date(2024, 11, 7)]
        index = pd.Index(data, name='date')
        data = {
            'bytes': [9352, 1224416],
            'hits': [1, 99],
        }
        expected = pd.DataFrame(index=index, data=data)

        pd.testing.assert_frame_equal(actual, expected)

    def test_gzipped(self, mock_dt):
        """
        Scenario:  read gzipped log file

        Expected result:  hits are verified
        """
        mock_dt.today.return_value = dt.date.today()
        mock_dt.side_effect = lambda *args, **kw:  dt.date(*args, **kw)

        logfile = ir.files('tests.data').joinpath('gzipped.log.gz')
        with tempfile.TemporaryDirectory() as tdir:
            dbfile = f"{tdir}/test.db"
            with LogLogs(logfile, dbfile=dbfile) as o:
                o.run()

            with sqlite3.connect(
                dbfile,
                detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
            ) as conn:
                actual = pd.read_sql(
                    'select * from bots', conn, index_col='ua'
                )

        data = [
            'dspace-internal', 'bingbot/2.0', "Safari/iOS/WebKit on iPhone"
        ]
        index = pd.Index(data, name='ua')
        data = {
            'hits': [86, 12, 2],
            'error_pct': [7.0, 0, 0],
            '429': [0, 0, 0],
            'robots': [0, 0, 0],
            'xmlui': [0, 0, 0],
            'sitemaps': [0, 0, 0],
            'date': [
                dt.date(2024, 11, 7),
                dt.date(2024, 11, 7),
                dt.date(2024, 11, 7),
            ]
        }
        expected = pd.DataFrame(index=index, data=data)

        pd.testing.assert_frame_equal(
            actual, expected, check_exact=False, rtol=0.1
        )

    def test_yesterdays_log(self, mock_dt):
        """
        Scenario:  read gzipped log file and specify the date

        Expected result:  hits are verified
        """
        mock_dt.today.return_value = dt.date.today()
        mock_dt.side_effect = lambda *args, **kw:  dt.date(*args, **kw)

        logfile = ir.files('tests.data').joinpath('gzipped.log.gz')
        with tempfile.TemporaryDirectory() as tdir:
            dbfile = f"{tdir}/test.db"
            with LogLogs(logfile, dbfile=dbfile) as o:
                o.run()

            with sqlite3.connect(
                dbfile,
                detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
            ) as conn:
                actual = pd.read_sql(
                    'select * from bots', conn, index_col='ua'
                )

        data = [
            'dspace-internal', 'bingbot/2.0', "Safari/iOS/WebKit on iPhone"
        ]
        index = pd.Index(data, name='ua')
        data = {
            'hits': [86, 12, 2],
            'error_pct': [7.0, 0, 0],
            '429': [0, 0, 0],
            'robots': [0, 0, 0],
            'xmlui': [0, 0, 0],
            'sitemaps': [0, 0, 0],
            'date': [
                dt.date(2024, 11, 7),
                dt.date(2024, 11, 7),
                dt.date(2024, 11, 7),
            ]
        }
        expected = pd.DataFrame(index=index, data=data)

        pd.testing.assert_frame_equal(
            actual, expected, check_exact=False, rtol=0.1
        )
