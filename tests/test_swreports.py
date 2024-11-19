# standard library imports
import datetime as dt
import importlib.resources as ir
import io
import pathlib
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

# 3rd party library imports
import pandas as pd

# local imports
from swlogs.swreports import SWReport


class TestSuite(unittest.TestCase):

    def setUp(self):
        """
        Before each test, setup a test SQLITE database.
        """

        self.tdir = tempfile.TemporaryDirectory()

        self.dbfile = pathlib.Path(self.tdir.name) / 'test.db'
        conn = sqlite3.connect(self.dbfile)

        path = ir.files('tests.data.swreport').joinpath('bots.csv')
        df = pd.read_csv(path)
        df.to_sql('bots', conn, index=False)

        path = ir.files('tests.data.swreport').joinpath('overall.csv')
        df = pd.read_csv(path)
        df.to_sql('overall', conn, index=False)

        path = ir.files('tests.data.swreport').joinpath('ip32.csv')
        df = pd.read_csv(path, index_col=False)
        df.to_sql('ip32', conn, index=False)

        path = ir.files('tests.data.swreport').joinpath('ip24.csv')
        df = pd.read_csv(path, index_col=False)
        df.to_sql('ip24', conn, index=False)

    def tearDown(self):
        self.tdir.cleanup()

    def test_ip24(self):
        """
        Scenario:  report daily IP address counts for 24 bit address range

        Expected result:  report is verified
        """

        newconn = sqlite3.connect(self.dbfile)

        with patch('swlogs.swreports.date') as mock_date:
            mock_date.today.return_value = dt.date(2024, 11, 14)
            mock_date.side_effect = lambda *args, **kw: dt.date(*args, **kw)

            with SWReport(ip24=True) as o:
                with patch(
                    'swlogs.swreports.sys.stdout', new=io.StringIO()
                ) as fake_stdout:
                    with patch.object(o, 'conn', new=newconn):
                        o.run()

                    actual = fake_stdout.getvalue()

        expected = (
            ir.files('tests.data.swreport')
              .joinpath('daily-ip24.txt')
              .read_text()
        )

        self.assertEqual(actual, expected)

    def test_ip32(self):
        """
        Scenario:  report daily IP address counts

        Expected result:  report is verified
        """

        newconn = sqlite3.connect(self.dbfile)

        with patch('swlogs.swreports.date') as mock_date:
            mock_date.today.return_value = dt.date(2024, 11, 14)
            mock_date.side_effect = lambda *args, **kw: dt.date(*args, **kw)

            with SWReport(ip32=True) as o:
                with patch(
                    'swlogs.swreports.sys.stdout', new=io.StringIO()
                ) as fake_stdout:
                    with patch.object(o, 'conn', new=newconn):
                        o.run()

                    actual = fake_stdout.getvalue()

        expected = (
            ir.files('tests.data.swreport')
              .joinpath('daily-ip32.txt')
              .read_text()
        )

        self.assertEqual(actual, expected)

    def test_bots_smoke(self):
        """
        Scenario:  report daily bots

        Expected result:  report is verified
        """

        newconn = sqlite3.connect(self.dbfile)

        with patch('swlogs.swreports.date') as mock_date:
            mock_date.today.return_value = dt.date(2024, 11, 14)
            mock_date.side_effect = lambda *args, **kw: dt.date(*args, **kw)

            with SWReport() as o:
                with patch(
                    'swlogs.swreports.sys.stdout', new=io.StringIO()
                ) as fake_stdout:
                    with patch.object(o, 'conn', new=newconn):
                        o.run()

                    actual = fake_stdout.getvalue()

        expected = (
            ir.files('tests.data.swreport')
              .joinpath('daily-bots.txt')
              .read_text()
        )

        self.assertEqual(actual, expected)

    def test_bots_specific_date(self):
        """
        Scenario:  report daily bots for a specific date

        Expected result:  report is verified
        """

        newconn = sqlite3.connect(self.dbfile)

        with SWReport(thedate=dt.date(2024, 11, 12)) as o:
            with patch(
                'swlogs.swreports.sys.stdout', new=io.StringIO()
            ) as fake_stdout:
                with patch.object(o, 'conn', new=newconn):
                    o.run()

                actual = fake_stdout.getvalue()

        expected = (
            ir.files('tests.data.swreport')
              .joinpath('yesterday-bots.txt')
              .read_text()
        )

        self.assertEqual(actual, expected)

    def test_overall_smoke(self):
        """
        Scenario:  report overall

        Expected result:  report is verified
        """

        newconn = sqlite3.connect(self.dbfile)

        with SWReport(overall=True) as o:
            with patch(
                'swlogs.swreports.sys.stdout', new=io.StringIO()
            ) as fake_stdout:
                with patch.object(o, 'conn', new=newconn):
                    o.run()

                actual = fake_stdout.getvalue()

        expected = (
            ir.files('tests.data.swreport')
              .joinpath('daily-overall.txt')
              .read_text()
        )

        self.assertEqual(actual, expected)
