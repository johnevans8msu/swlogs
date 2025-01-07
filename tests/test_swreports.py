# standard library imports
import datetime as dt
import importlib.resources as ir
import io
import unittest
from unittest.mock import patch

# 3rd party library imports
import pandas as pd

# local imports
from swlogs.swreports import SWReport


@patch('swlogs.common.sqlalchemy')
@patch('swlogs.common.psycopg.connect')
@patch('swlogs.common.yaml')
class TestSuite(unittest.TestCase):

    def test_ip16(self, mock_yaml, mock_psycopg, mock_sqlalchemy):
        """
        Scenario:  report daily IP address counts for 16 bit address range

        Expected result:  report is verified
        """
        mock_yaml.safe_load.return_value = {'connection_string': None}
        mock_psycopg.connect.return_value = None
        mock_sqlalchemy.create_engine.return_value = None

        time = [
            dt.date(2024, 11, 7),
            dt.date(2024, 11, 7),
            dt.date(2024, 11, 7)
        ]
        data = {
            'ip': ['153.90', '52.167', '24.57'],
            'hits': [86, 12, 2],
            'date': time
        }
        expected = pd.DataFrame(data=data).set_index('date')

        with (
            patch('swlogs.swreports.pd.read_sql') as mock_read_sql,
            patch('swlogs.swreports.date') as mock_date,
            patch(
                'swlogs.swreports.sys.stdout', new=io.StringIO()
            ) as fake_stdout,
        ):
            mock_read_sql.return_value = expected
            mock_date.today.return_value = dt.date(2024, 11, 8)
            mock_date.side_effect = lambda *args, **kw: dt.date(*args, **kw)

            with SWReport(ip16=True) as o:
                o.run()

            actual = fake_stdout.getvalue()

        expected = (
            ir.files('tests.data.swreport')
              .joinpath('daily-ip16.txt')
              .read_text()
        )

        self.assertEqual(actual, expected)

    def test_ip24(self, mock_yaml, mock_psycopg, mock_sqlalchemy):
        """
        Scenario:  report daily IP address counts for 24 bit address range

        Expected result:  report is verified
        """
        mock_yaml.safe_load.return_value = {'connection_string': None}
        mock_psycopg.connect.return_value = None
        mock_sqlalchemy.create_engine.return_value = None

        path = ir.files('tests.data.swreport').joinpath('ip24.csv')
        df = pd.read_csv(path, parse_dates=['date'])
        df = df.query('date == @dt.date(2024, 11, 7)').set_index('date')
        df = df.sort_values(by='hits', ascending=False)
        df = df.drop(labels='error_pct', axis='columns')

        with (
            patch('swlogs.swreports.pd.read_sql') as mock_read_sql,
            patch('swlogs.swreports.date') as mock_date,
            patch(
                'swlogs.swreports.sys.stdout', new=io.StringIO()
            ) as fake_stdout,
        ):
            mock_read_sql.return_value = df
            mock_date.today.return_value = dt.date(2024, 11, 8)
            mock_date.side_effect = lambda *args, **kw: dt.date(*args, **kw)

            with SWReport(ip24=True) as o:
                o.run()

                actual = fake_stdout.getvalue()

        expected = (
            ir.files('tests.data.swreport')
              .joinpath('daily-ip24.txt')
              .read_text()
        )
        self.assertEqual(actual, expected)

    def test_ip32(self, mock_yaml, mock_psycopg, mock_sqlalchemy):
        """
        Scenario:  report daily IP address counts

        Expected result:  report is verified
        """
        mock_yaml.safe_load.return_value = {'connection_string': None}
        mock_psycopg.connect.return_value = None
        mock_sqlalchemy.create_engine.return_value = None

        path = ir.files('tests.data.swreport').joinpath('ip32.csv')
        df = pd.read_csv(path, parse_dates=['date'])
        df = df.query('date == @dt.date(2024, 11, 7)').set_index('date')
        df = df.sort_values(by='hits', ascending=False)
        df = df.drop(labels='error_pct', axis='columns')

        with (
            patch('swlogs.swreports.pd.read_sql') as mock_read_sql,
            patch('swlogs.swreports.date') as mock_date,
            patch(
                'swlogs.swreports.sys.stdout', new=io.StringIO()
            ) as fake_stdout,
        ):
            mock_date.today.return_value = dt.date(2024, 11, 8)
            mock_date.side_effect = lambda *args, **kw: dt.date(*args, **kw)
            mock_read_sql.return_value = df

            with SWReport(ip32=True) as o:
                o.run()

            actual = fake_stdout.getvalue()

        expected = (
            ir.files('tests.data.swreport')
              .joinpath('daily-ip32.txt')
              .read_text()
        )

        self.assertEqual(actual, expected)

    def test_bots_smoke(self, mock_yaml, mock_psycopg, mock_sqlalchemy):
        """
        Scenario:  report daily bots

        Expected result:  report is verified
        """
        mock_yaml.safe_load.return_value = {'connection_string': None}
        mock_psycopg.connect.return_value = None
        mock_sqlalchemy.create_engine.return_value = None

        path = ir.files('tests.data.swreport').joinpath('bots.csv')
        df = pd.read_csv(path, parse_dates=['date'])
        df = df.query('date == @dt.date(2024, 11, 13)').set_index('date')

        with (
            patch('swlogs.swreports.pd.read_sql') as mock_read_sql,
            patch('swlogs.swreports.date') as mock_date,
            patch(
                'swlogs.swreports.sys.stdout', new=io.StringIO()
            ) as fake_stdout,
        ):
            mock_read_sql.return_value = df

            mock_date.today.return_value = dt.date(2024, 11, 14)
            mock_date.side_effect = lambda *args, **kw: dt.date(*args, **kw)

            with SWReport() as o:
                o.run()

            actual = fake_stdout.getvalue()

        expected = (
            ir.files('tests.data.swreport')
              .joinpath('daily-bots.txt')
              .read_text()
        )
        self.assertEqual(actual, expected)

    def test_bots_specific_date(self, mock_yaml, mock_psycopg, mock_sqlalchemy):  # noqa : E501
        """
        Scenario:  report daily bots for a specific date

        Expected result:  report is verified
        """
        mock_yaml.safe_load.return_value = {'connection_string': None}
        mock_psycopg.connect.return_value = None
        mock_sqlalchemy.create_engine.return_value = None

        path = ir.files('tests.data.swreport').joinpath('bots.csv')
        df = pd.read_csv(path, parse_dates=['date'])
        df = df.query('date == @dt.date(2024, 11, 12)').set_index('date')

        with (
            patch('swlogs.swreports.pd.read_sql') as mock_read_sql,
            patch(
                'swlogs.swreports.sys.stdout', new=io.StringIO()
            ) as fake_stdout,
            SWReport(thedate=dt.date(2024, 11, 12)) as o,
        ):
            mock_read_sql.return_value = df

            o.run()

            actual = fake_stdout.getvalue()

        expected = (
            ir.files('tests.data.swreport')
              .joinpath('yesterday-bots.txt')
              .read_text()
        )

        self.assertEqual(actual, expected)

    def test_bots_user_agent(self, mock_yaml, mock_psycopg, mock_sqlalchemy):
        """
        Scenario:  report time series for a specific bot

        Expected result:  report is verified
        """
        mock_yaml.safe_load.return_value = {'connection_string': None}
        mock_psycopg.connect.return_value = None
        mock_sqlalchemy.create_engine.return_value = None

        path = ir.files('tests.data.swreport').joinpath('bots.csv')
        df = pd.read_csv(path, parse_dates=['date'])

        date = dt.date(2024, 11, 7)  # noqa : F841
        df = df.query('ua == "Chrome/Win10/Blink" and date <= @date')
        df = df.set_index('date')

        with (
            patch('swlogs.swreports.pd.read_sql') as mock_read_sql,
            patch('swlogs.swreports.date') as mock_date,
            patch(
                'swlogs.swreports.sys.stdout', new=io.StringIO()
            ) as fake_stdout,
        ):
            mock_date.today.return_value = dt.date(2024, 11, 8)
            mock_read_sql.return_value = df

            with SWReport(useragent='Chrome/Win10/Blink') as o:
                o.run()

            actual = fake_stdout.getvalue()

        tfile = ir.files('tests.data.swreport').joinpath('chrome-w10-b.txt')
        expected = tfile.read_text()

        self.assertEqual(actual, expected)

    def test_overall_smoke(self, mock_yaml, mock_psycopg, mock_sqlalchemy):
        """
        Scenario:  report overall

        Expected result:  report is verified
        """
        mock_yaml.safe_load.return_value = {'connection_string': None}
        mock_psycopg.connect.return_value = None
        mock_sqlalchemy.create_engine.return_value = None

        path = ir.files('tests.data.swreport').joinpath('overall.csv')
        df = pd.read_csv(path, parse_dates=['date'])
        df = df.groupby('date').sum()
        df['bytes'] = df['bytes'] / 1024 ** 3
        df['hits'] = df['hits'] / 1e6
        df.columns = ['GBytes', 'hits (million)']

        with (
            patch('swlogs.swreports.pd.read_sql') as mock_read_sql,
            patch(
                'swlogs.swreports.sys.stdout',
                new=io.StringIO()
            ) as fake_stdout,
            SWReport(overall=True) as o,
        ):
            mock_read_sql.return_value = df

            o.run()

            actual = fake_stdout.getvalue()

        expfile = ir.files('tests.data.swreport').joinpath('daily-overall.txt')
        expected = expfile.read_text()

        self.assertEqual(actual, expected)
