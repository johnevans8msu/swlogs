import datetime as dt
import importlib.resources as ir
import unittest
from unittest import mock

import pandas as pd

from swlogs.loglogs import LogLogs


@mock.patch('swlogs.loglogs.pd.DataFrame.to_sql')
@mock.patch('swlogs.common.psycopg.connect')
class TestSuite(unittest.TestCase):

    def test_bot_smoke(self, mock_pconnect, mock_to_sql):
        """
        Scenario:  read log file

        Expected result:  no errors
        """

        logfile = ir.files('tests.data').joinpath('smoke.log')
        with LogLogs(logfile) as o:
            o.run()

    def test_overall_smoke(self, mock_pconnect, mock_to_sql):
        """
        Scenario:  read log file

        Expected result:  no errors
        """
        logfile = ir.files('tests.data').joinpath('smoke.log')
        with LogLogs(logfile) as o:
            o.run()

    def test_split_over_two_days(self, mock_pconnect, mock_to_sql):
        """
        Scenario:  read log file that is split over two days.  99 hits are
        from today, 1 hit from previous day

        Expected result:  no errors
        """
        logfile = ir.files('tests.data').joinpath('two-days.log')
        with LogLogs(logfile) as o:
            o.run()

    def test_gzipped(self, mock_pconnect, mock_to_sql):
        """
        Scenario:  read gzipped log file

        Expected result:  no errors
        """
        logfile = ir.files('tests.data').joinpath('gzipped.log.gz')
        with LogLogs(logfile) as o:
            o.run()

    def test_yesterdays_log(self, mock_pconnect, mock_to_sql):
        """
        Scenario:  read gzipped log file and specify the date

        Expected result:  no errors
        """
        logfile = ir.files('tests.data').joinpath('gzipped.log.gz')
        with LogLogs(logfile) as o:
            o.run()

    def test_ip24(self, mock_pconnect, mock_to_sql):
        """
        Scenario:  compute the daily IP24 counts

        Expected result:  no errors
        """
        logfile = ir.files('tests.data').joinpath('smoke.log')
        with LogLogs(logfile) as o:
            o.run()

    def test_ip32(self, mock_pconnect, mock_to_sql):
        """
        Scenario:  compute the daily IP32 counts

        Expected result:  no errors
        """
        logfile = ir.files('tests.data').joinpath('smoke.log')
        with LogLogs(logfile) as o:
            o.run()

    def test_item_percentage(self, mock_pconnect, mock_to_sql):
        """
        Scenario:  compute the item views percentage

        Expected result:  no errors
        """
        logfile = ir.files('tests.data').joinpath('10-items.log')
        with LogLogs(logfile) as o:
            o.run()
