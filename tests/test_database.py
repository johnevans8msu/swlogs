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

    def test_smoke(self, mock_dt):
        """
        Scenario:  read log file

        Expected result:  hits are verified
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
                detect_types = sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
            ) as conn:
                actual = pd.read_sql(
                    'select * from logs', conn, index_col='ua'
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
            'date': [dt.date.today(), dt.date.today(), dt.date.today()],
        }
        expected = pd.DataFrame(index=index, data=data)

        pd.testing.assert_frame_equal(
            actual, expected, check_exact=False, rtol=0.1
        )
